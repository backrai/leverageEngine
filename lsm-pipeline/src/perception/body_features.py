"""
Body Pose Feature Extraction for UB (Location) Classification (Task 1.4.3)

Converts body pose keypoints + wrist positions into LSM-PN LocationSpec
predictions. Determines which of Cruz Aldrete's 76 body locations the
hand is closest to, and extracts movement trajectories.

Key features:
  - Hand-to-body spatial relationship computation
  - Body region classification (HEAD, FACE, NECK, TRUNK, ARM, etc.)
  - Movement trajectory analysis (contour, direction, velocity)
  - Neutral space detection and vector classification

Reference: Cruz Aldrete (2008) §4.3 — Ubicación (Location system)
"""
import math
import numpy as np
from dataclasses import dataclass
from typing import Optional

from .keypoint_schema import BodyLandmark


# ── Body Region Anchors ──────────────────────────────────────────────────────
# Maps body regions to the MediaPipe body landmarks that define them.
# We compute the hand's position relative to these anchors.

BODY_REGION_ANCHORS = {
    "HEAD": {
        "landmarks": [BodyLandmark.NOSE, BodyLandmark.LEFT_EAR, BodyLandmark.RIGHT_EAR],
        "center_method": "mean",
    },
    "FACE": {
        "landmarks": [
            BodyLandmark.NOSE,
            BodyLandmark.LEFT_EYE, BodyLandmark.RIGHT_EYE,
            BodyLandmark.MOUTH_LEFT, BodyLandmark.MOUTH_RIGHT,
        ],
        "center_method": "mean",
    },
    "NECK": {
        "landmarks": [BodyLandmark.LEFT_SHOULDER, BodyLandmark.RIGHT_SHOULDER],
        "center_method": "midpoint_elevated",  # midpoint of shoulders, slightly above
    },
    "TRUNK": {
        "landmarks": [
            BodyLandmark.LEFT_SHOULDER, BodyLandmark.RIGHT_SHOULDER,
            BodyLandmark.LEFT_HIP, BodyLandmark.RIGHT_HIP,
        ],
        "center_method": "mean",
    },
    "ARM": {
        "landmarks": [BodyLandmark.LEFT_ELBOW, BodyLandmark.RIGHT_ELBOW],
        "center_method": "per_side",
    },
    "FOREARM": {
        "landmarks": [
            BodyLandmark.LEFT_ELBOW, BodyLandmark.LEFT_WRIST,
            BodyLandmark.RIGHT_ELBOW, BodyLandmark.RIGHT_WRIST,
        ],
        "center_method": "per_side_midpoint",
    },
}

# Specific body anchor points for Cruz Aldrete location codes
# Maps location code → which body landmarks to use for distance computation
LOCATION_ANCHOR_LANDMARKS = {
    "Fr": [BodyLandmark.NOSE],                    # Forehead ≈ above nose
    "Oc": [BodyLandmark.LEFT_EYE, BodyLandmark.RIGHT_EYE],  # Eyes
    "Na": [BodyLandmark.NOSE],                    # Nose
    "Au": [BodyLandmark.LEFT_EAR, BodyLandmark.RIGHT_EAR],  # Ears
    "Os": [BodyLandmark.MOUTH_LEFT, BodyLandmark.MOUTH_RIGHT],  # Mouth
    "Me": [BodyLandmark.MOUTH_LEFT, BodyLandmark.MOUTH_RIGHT],  # Chin ≈ below mouth
    "Um": [BodyLandmark.LEFT_SHOULDER, BodyLandmark.RIGHT_SHOULDER],  # Shoulders
    "Pe": [BodyLandmark.LEFT_SHOULDER, BodyLandmark.RIGHT_SHOULDER],  # Chest
    "Co": [BodyLandmark.LEFT_SHOULDER, BodyLandmark.RIGHT_SHOULDER],  # Neck
    "Cut": [BodyLandmark.LEFT_ELBOW, BodyLandmark.RIGHT_ELBOW],  # Elbows
    "Car": [BodyLandmark.LEFT_WRIST, BodyLandmark.RIGHT_WRIST],  # Wrists
    "Ve": [BodyLandmark.LEFT_HIP, BodyLandmark.RIGHT_HIP],  # Stomach
    "Cox": [BodyLandmark.LEFT_HIP, BodyLandmark.RIGHT_HIP],  # Hip
}


# ── Data Structures ──────────────────────────────────────────────────────────

@dataclass
class BodyAnchorPosition:
    """Position of a body anchor in frame coordinates."""
    name: str
    position: np.ndarray  # (3,)
    confidence: float


@dataclass
class LocationPrediction:
    """Predicted LSM-PN location from body pose analysis."""
    body_region: str           # HEAD, FACE, NECK, TRUNK, ARM, FOREARM, HAND, NEUTRAL_SPACE
    body_anchor: str           # Cruz Aldrete code (e.g., "Fr", "Pe", "mØTo")
    distance_to_anchor: float  # distance from hand to nearest anchor
    contact: str               # TOUCHING, NEAR, MEDIAL, DISTANT
    laterality: str            # IPSILATERAL, CONTRALATERAL, MIDLINE
    space_distance: Optional[str]  # PROXIMAL, MEDIAL, DISTAL (for neutral space)
    confidence: float


@dataclass
class MovementTrajectory:
    """Extracted movement trajectory from a sequence of frames."""
    contour: Optional[str]     # STRAIGHT, ARC, CIRCLE, ZIGZAG, SEVEN
    direction: np.ndarray      # (3,) normalized direction vector
    distance: str              # SHORT, MEDIUM, LONG
    plane: Optional[str]       # HORIZONTAL, VERTICAL, SAGITTAL, OBLIQUE
    mean_speed: float
    max_speed: float
    is_repeated: bool
    total_distance: float


# ── Body Pose Feature Extraction ─────────────────────────────────────────────

class BodyPoseAnalyzer:
    """
    Analyzes body pose keypoints to determine hand-to-body spatial
    relationships for UB (location) classification.
    """

    def __init__(self):
        # Contact distance thresholds (relative to shoulder width)
        self.contact_thresholds = {
            "TOUCHING": 0.08,
            "NEAR": 0.20,
            "MEDIAL": 0.50,
            "DISTANT": 1.0,
        }

    def compute_body_anchors(self, body_landmarks: list) -> dict[str, BodyAnchorPosition]:
        """
        Compute named body anchor positions from MediaPipe body landmarks.

        Args:
            body_landmarks: List of 33 (x, y, z, visibility) tuples

        Returns:
            Dict of anchor_name → BodyAnchorPosition
        """
        if len(body_landmarks) < 33:
            return {}

        pts = np.array([(lm[0], lm[1], lm[2]) for lm in body_landmarks], dtype=np.float32)
        vis = np.array([lm[3] for lm in body_landmarks], dtype=np.float32)

        anchors = {}

        # Forehead (above nose, estimated)
        nose = pts[BodyLandmark.NOSE.value]
        left_eye = pts[BodyLandmark.LEFT_EYE.value]
        eye_to_nose = nose[1] - left_eye[1]
        forehead = nose.copy()
        forehead[1] -= eye_to_nose * 1.5  # above eyes
        anchors["Fr"] = BodyAnchorPosition("Fr", forehead, float(vis[BodyLandmark.NOSE.value]))

        # Eyes
        eye_center = (pts[BodyLandmark.LEFT_EYE.value] + pts[BodyLandmark.RIGHT_EYE.value]) / 2
        anchors["Oc"] = BodyAnchorPosition("Oc", eye_center, float(
            (vis[BodyLandmark.LEFT_EYE.value] + vis[BodyLandmark.RIGHT_EYE.value]) / 2
        ))

        # Nose
        anchors["Na"] = BodyAnchorPosition("Na", nose, float(vis[BodyLandmark.NOSE.value]))

        # Ears
        for side, ear_lm in [("L", BodyLandmark.LEFT_EAR), ("R", BodyLandmark.RIGHT_EAR)]:
            anchors[f"Au_{side}"] = BodyAnchorPosition(
                f"Au_{side}", pts[ear_lm.value], float(vis[ear_lm.value])
            )
        anchors["Au"] = BodyAnchorPosition("Au",
            (pts[BodyLandmark.LEFT_EAR.value] + pts[BodyLandmark.RIGHT_EAR.value]) / 2,
            float((vis[BodyLandmark.LEFT_EAR.value] + vis[BodyLandmark.RIGHT_EAR.value]) / 2)
        )

        # Mouth
        mouth_center = (pts[BodyLandmark.MOUTH_LEFT.value] + pts[BodyLandmark.MOUTH_RIGHT.value]) / 2
        anchors["Os"] = BodyAnchorPosition("Os", mouth_center, 0.8)

        # Chin (below mouth)
        chin = mouth_center.copy()
        chin[1] += eye_to_nose * 0.8
        anchors["Me"] = BodyAnchorPosition("Me", chin, 0.7)

        # Neck (midpoint of shoulders, slightly elevated)
        left_shoulder = pts[BodyLandmark.LEFT_SHOULDER.value]
        right_shoulder = pts[BodyLandmark.RIGHT_SHOULDER.value]
        neck = (left_shoulder + right_shoulder) / 2
        neck[1] -= 0.03  # slightly above shoulder line
        anchors["Co"] = BodyAnchorPosition("Co", neck, 0.8)

        # Shoulders
        anchors["Um"] = BodyAnchorPosition("Um",
            (left_shoulder + right_shoulder) / 2, 0.9)

        # Chest (between shoulders, slightly below)
        chest = (left_shoulder + right_shoulder) / 2
        chest[1] += 0.05
        anchors["Pe"] = BodyAnchorPosition("Pe", chest, 0.85)

        # Elbows
        anchors["Cut_L"] = BodyAnchorPosition("Cut_L",
            pts[BodyLandmark.LEFT_ELBOW.value], float(vis[BodyLandmark.LEFT_ELBOW.value]))
        anchors["Cut_R"] = BodyAnchorPosition("Cut_R",
            pts[BodyLandmark.RIGHT_ELBOW.value], float(vis[BodyLandmark.RIGHT_ELBOW.value]))

        # Wrists
        anchors["Car_L"] = BodyAnchorPosition("Car_L",
            pts[BodyLandmark.LEFT_WRIST.value], float(vis[BodyLandmark.LEFT_WRIST.value]))
        anchors["Car_R"] = BodyAnchorPosition("Car_R",
            pts[BodyLandmark.RIGHT_WRIST.value], float(vis[BodyLandmark.RIGHT_WRIST.value]))

        # Stomach/Waist (midpoint of hips)
        left_hip = pts[BodyLandmark.LEFT_HIP.value]
        right_hip = pts[BodyLandmark.RIGHT_HIP.value]
        stomach = (left_hip + right_hip) / 2
        stomach[1] -= 0.03
        anchors["Ve"] = BodyAnchorPosition("Ve", stomach, 0.7)

        # Hip
        anchors["Cox"] = BodyAnchorPosition("Cox",
            (left_hip + right_hip) / 2, 0.7)

        return anchors

    def classify_location(
        self,
        hand_position: np.ndarray,
        body_anchors: dict[str, BodyAnchorPosition],
        body_landmarks: list,
        dominant_side: str = "RIGHT",
    ) -> LocationPrediction:
        """
        Classify the hand's location relative to the body.

        Args:
            hand_position: (3,) hand position (wrist or palm center)
            body_anchors: Computed body anchor positions
            body_landmarks: Raw 33-landmark list
            dominant_side: "LEFT" or "RIGHT"

        Returns:
            LocationPrediction with body region, anchor, contact, laterality
        """
        if not body_anchors or len(body_landmarks) < 33:
            return LocationPrediction(
                body_region="NEUTRAL_SPACE", body_anchor="mØ",
                distance_to_anchor=1.0, contact="DISTANT",
                laterality="MIDLINE", space_distance="MEDIAL",
                confidence=0.3,
            )

        pts = np.array([(lm[0], lm[1], lm[2]) for lm in body_landmarks], dtype=np.float32)

        # Compute shoulder width for scale reference
        shoulder_width = np.linalg.norm(
            pts[BodyLandmark.LEFT_SHOULDER.value] - pts[BodyLandmark.RIGHT_SHOULDER.value]
        )
        if shoulder_width < 1e-6:
            shoulder_width = 0.3

        # Find nearest body anchor
        min_dist = float('inf')
        nearest_anchor = "mØ"
        nearest_pos = hand_position

        # Priority anchors to check (ordered by anatomical specificity)
        priority_anchors = ["Fr", "Oc", "Na", "Au", "Os", "Me", "Co",
                           "Um", "Pe", "Cut_L", "Cut_R", "Ve", "Cox"]

        for anchor_name in priority_anchors:
            if anchor_name not in body_anchors:
                continue
            anchor = body_anchors[anchor_name]
            dist = float(np.linalg.norm(hand_position - anchor.position))
            if dist < min_dist:
                min_dist = dist
                nearest_anchor = anchor_name.split("_")[0]  # Remove L/R suffix
                nearest_pos = anchor.position

        # Classify distance → contact type
        relative_dist = min_dist / shoulder_width
        contact = "DISTANT"
        for contact_type, threshold in self.contact_thresholds.items():
            if relative_dist <= threshold:
                contact = contact_type
                break

        # Classify body region based on nearest anchor
        region = self._anchor_to_region(nearest_anchor)

        # Check if in neutral space (hand is far from all body anchors)
        if relative_dist > 0.6:
            region = "NEUTRAL_SPACE"
            nearest_anchor = self._classify_neutral_space(hand_position, pts)

        # Laterality
        body_center_x = (pts[BodyLandmark.LEFT_SHOULDER.value][0] +
                         pts[BodyLandmark.RIGHT_SHOULDER.value][0]) / 2
        hand_offset_x = hand_position[0] - body_center_x
        if abs(hand_offset_x) < shoulder_width * 0.15:
            laterality = "MIDLINE"
        elif (dominant_side == "RIGHT" and hand_offset_x > 0) or \
             (dominant_side == "LEFT" and hand_offset_x < 0):
            laterality = "IPSILATERAL"
        else:
            laterality = "CONTRALATERAL"

        # Space distance for neutral space
        space_distance = None
        if region == "NEUTRAL_SPACE":
            # Forward distance from body
            body_center_z = (pts[BodyLandmark.LEFT_SHOULDER.value][2] +
                            pts[BodyLandmark.RIGHT_SHOULDER.value][2]) / 2
            z_offset = hand_position[2] - body_center_z
            if z_offset < -0.1:
                space_distance = "PROXIMAL"
            elif z_offset > 0.1:
                space_distance = "DISTAL"
            else:
                space_distance = "MEDIAL"

        return LocationPrediction(
            body_region=region,
            body_anchor=nearest_anchor,
            distance_to_anchor=min_dist,
            contact=contact,
            laterality=laterality,
            space_distance=space_distance,
            confidence=0.8 if min_dist < shoulder_width else 0.5,
        )

    def _anchor_to_region(self, anchor: str) -> str:
        """Map a Cruz Aldrete anchor code to a body region."""
        region_map = {
            "Fr": "FACE", "Oc": "FACE", "Na": "FACE", "Os": "FACE",
            "Me": "FACE", "Ci": "FACE", "Ge": "FACE", "La": "FACE",
            "Au": "HEAD", "Te": "HEAD", "Vx": "HEAD", "Par": "HEAD",
            "Co": "NECK", "Ce": "NECK", "Gu": "NECK",
            "Um": "TRUNK", "Pe": "TRUNK", "Ve": "TRUNK", "Cox": "TRUNK",
            "Cor": "TRUNK", "Es": "TRUNK", "To": "TRUNK", "Abd": "TRUNK",
            "Cit": "TRUNK", "Cos": "TRUNK", "Cla": "TRUNK", "Dor": "TRUNK",
            "Br": "ARM", "IntBr": "ARM",
            "Cut": "ARM",
            "Abr": "FOREARM", "IntAbr": "FOREARM", "ExtAbr": "FOREARM",
            "Car": "HAND",
        }
        return region_map.get(anchor, "NEUTRAL_SPACE")

    def _classify_neutral_space(self, hand_pos: np.ndarray, body_pts: np.ndarray) -> str:
        """Classify neutral space location code (e.g., mØPe, mØTo)."""
        # Determine height relative to body
        shoulder_y = (body_pts[BodyLandmark.LEFT_SHOULDER.value][1] +
                     body_pts[BodyLandmark.RIGHT_SHOULDER.value][1]) / 2
        hip_y = (body_pts[BodyLandmark.LEFT_HIP.value][1] +
                body_pts[BodyLandmark.RIGHT_HIP.value][1]) / 2
        nose_y = body_pts[BodyLandmark.NOSE.value][1]

        hand_y = hand_pos[1]

        if hand_y < nose_y:
            return "mØFr"   # forehead height
        elif hand_y < shoulder_y:
            return "mØCo"   # neck/shoulder height
        elif hand_y < (shoulder_y + hip_y) / 2:
            return "mØPe"   # chest height
        else:
            return "mØVe"   # stomach/waist height


# ── Movement Trajectory Analysis ─────────────────────────────────────────────

def analyze_trajectory(positions: list[np.ndarray], fps: float = 30.0) -> MovementTrajectory:
    """
    Analyze a sequence of hand positions to classify the movement type.

    Args:
        positions: List of (3,) arrays representing hand positions over time
        fps: Video frame rate for speed computation

    Returns:
        MovementTrajectory with contour, direction, dynamics
    """
    if len(positions) < 3:
        return MovementTrajectory(
            contour=None, direction=np.zeros(3),
            distance="SHORT", plane=None,
            mean_speed=0.0, max_speed=0.0,
            is_repeated=False, total_distance=0.0,
        )

    pts = np.array(positions, dtype=np.float32)
    n = len(pts)

    # ── Total distance ──────────────────────────────────────────────
    deltas = np.diff(pts, axis=0)
    segment_lengths = np.linalg.norm(deltas, axis=1)
    total_dist = float(np.sum(segment_lengths))

    # ── Speed ───────────────────────────────────────────────────────
    speeds = segment_lengths * fps
    mean_speed = float(np.mean(speeds))
    max_speed = float(np.max(speeds))

    # ── Direction ───────────────────────────────────────────────────
    start = pts[0]
    end = pts[-1]
    direction = end - start
    straight_dist = float(np.linalg.norm(direction))
    if straight_dist > 1e-6:
        direction = direction / straight_dist
    else:
        direction = np.zeros(3)

    # ── Distance classification ─────────────────────────────────────
    if total_dist < 0.05:
        distance = "SHORT"
    elif total_dist < 0.15:
        distance = "MEDIUM"
    else:
        distance = "LONG"

    # ── Contour classification ──────────────────────────────────────
    curvature_ratio = total_dist / max(straight_dist, 1e-6)

    contour = _classify_contour(pts, curvature_ratio, straight_dist)

    # ── Plane classification ────────────────────────────────────────
    plane = _classify_plane(pts)

    # ── Repetition detection ────────────────────────────────────────
    is_repeated = _detect_repetition(pts)

    return MovementTrajectory(
        contour=contour,
        direction=direction,
        distance=distance,
        plane=plane,
        mean_speed=mean_speed,
        max_speed=max_speed,
        is_repeated=is_repeated,
        total_distance=total_dist,
    )


def _classify_contour(pts: np.ndarray, curvature_ratio: float, straight_dist: float) -> Optional[str]:
    """Classify the path contour type."""
    if straight_dist < 0.02:
        return None  # no significant movement

    # Nearly straight path
    if curvature_ratio < 1.15:
        return "STRAIGHT"

    # Check for circle (start ≈ end)
    start_end_dist = np.linalg.norm(pts[0] - pts[-1])
    if start_end_dist < straight_dist * 0.3 and curvature_ratio > 2.5:
        return "CIRCLE"

    # Check for arc
    if 1.15 <= curvature_ratio < 2.0:
        return "ARC"

    # Check for zigzag (direction changes)
    direction_changes = _count_direction_changes(pts)
    if direction_changes >= 3:
        return "ZIGZAG"

    # Check for seven (L-shape: one direction then sharp turn)
    if direction_changes == 1 and curvature_ratio < 2.0:
        return "SEVEN"

    return "ARC"  # default for curved paths


def _classify_plane(pts: np.ndarray) -> Optional[str]:
    """Classify the spatial plane of movement."""
    if len(pts) < 3:
        return None

    # Compute movement variance along each axis
    variance = np.var(pts, axis=0)
    total_var = np.sum(variance)

    if total_var < 1e-6:
        return None

    # Normalize
    var_ratio = variance / total_var

    # Dominant axes determine the plane
    # x = left/right, y = up/down, z = forward/back
    if var_ratio[1] > 0.6:  # mostly vertical
        return "VERTICAL"
    elif var_ratio[0] > 0.6:  # mostly horizontal
        return "HORIZONTAL"
    elif var_ratio[2] > 0.6:  # mostly sagittal
        return "SAGITTAL"
    else:
        return "OBLIQUE"


def _count_direction_changes(pts: np.ndarray) -> int:
    """Count significant direction changes in a trajectory."""
    if len(pts) < 3:
        return 0

    deltas = np.diff(pts, axis=0)
    changes = 0
    for i in range(1, len(deltas)):
        cos_angle = np.dot(deltas[i], deltas[i-1]) / (
            np.linalg.norm(deltas[i]) * np.linalg.norm(deltas[i-1]) + 1e-8
        )
        if cos_angle < 0:  # direction reversed (>90°)
            changes += 1

    return changes


def _detect_repetition(pts: np.ndarray) -> bool:
    """Detect if a trajectory contains repeated motion patterns."""
    if len(pts) < 6:
        return False

    # Simple autocorrelation check
    mid = len(pts) // 2
    first_half = pts[:mid]
    second_half = pts[mid:mid+len(first_half)]

    if len(first_half) != len(second_half):
        return False

    # Check if the two halves have similar shapes
    diff = np.mean(np.abs(first_half - second_half))
    total_range = np.max(np.abs(pts - pts[0]))

    return diff < total_range * 0.4 if total_range > 0.01 else False
