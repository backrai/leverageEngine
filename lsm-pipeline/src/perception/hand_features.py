"""
Hand Feature Extraction for CM (Handshape) Classification

Converts raw 21-landmark hand keypoints into LSM-PN relevant features:
  - Per-finger flexion angles → FlexionLevel (EXTENDED, CURVED, BENT, CLOSED)
  - Thumb opposition angle → ThumbOpposition (OPPOSED, PARALLEL, CROSSED)
  - Finger spread → FingerSpread (CLOSED, NEUTRAL, SPREAD)
  - Finger interaction → FingerInteraction (NONE, SPREAD, STACKED, CROSSED)
  - Thumb contact → bool

These features directly map to the ParsedCM dataclass in cruz_aldrete_parser.py,
enabling automatic CM classification from video.

Reference: Cruz Aldrete (2008) §4.2.5 — notation system for finger postures
"""
import math
import numpy as np
from dataclasses import dataclass
from typing import Optional

from .keypoint_schema import HandLandmark, FINGER_JOINTS


@dataclass
class FingerAngles:
    """Joint angles for a single finger."""
    mcp_angle: float   # Metacarpophalangeal joint angle (degrees)
    pip_angle: float   # Proximal interphalangeal joint angle
    dip_angle: float   # Distal interphalangeal joint angle
    total_flexion: float  # Weighted sum → 0 (extended) to 180 (closed)


@dataclass
class HandFeatures:
    """Extracted features for one hand, ready for CM classification."""
    # Per-finger flexion
    thumb_flexion: float    # 0-180
    index_flexion: float
    middle_flexion: float
    ring_flexion: float
    pinky_flexion: float

    # Per-finger FlexionLevel (quantized)
    thumb_level: str   # "EXTENDED", "CURVED", "BENT", "CLOSED"
    index_level: str
    middle_level: str
    ring_level: str
    pinky_level: str

    # Thumb parameters
    thumb_opposition: str  # "OPPOSED", "PARALLEL", "CROSSED"
    thumb_contact: bool

    # Finger interaction
    spread: str            # "CLOSED", "NEUTRAL", "SPREAD"
    interaction: str       # "NONE", "SPREAD", "STACKED", "CROSSED"

    # Raw data
    landmarks: list        # 21 (x, y, z) tuples
    confidence: float

    def to_cm_search_vector(self) -> dict:
        """
        Convert to a search vector for matching against CM inventory.
        Returns a dict compatible with cm_inventory.CMEntry comparison.
        """
        return {
            "finger_states": {
                "index": self.index_level,
                "middle": self.middle_level,
                "ring": self.ring_level,
                "pinky": self.pinky_level,
            },
            "thumb_flexion": self.thumb_level,
            "thumb_opposition": self.thumb_opposition,
            "spread": self.spread,
            "interaction": self.interaction,
            "thumb_contact": self.thumb_contact,
        }


# ── Geometry Helpers ─────────────────────────────────────────────────────────

def _angle_between(v1: np.ndarray, v2: np.ndarray) -> float:
    """Angle between two 3D vectors in degrees."""
    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    return math.degrees(math.acos(cos_angle))


def _joint_angle(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
    """
    Compute the angle at joint p2 formed by segments p1-p2 and p2-p3.
    Returns angle in degrees (0 = straight/extended, 180 = fully folded).
    """
    v1 = p1 - p2
    v2 = p3 - p2
    angle = _angle_between(v1, v2)
    return 180.0 - angle  # Convert: 0° = extended, 180° = closed


def _landmarks_to_array(landmarks: list) -> np.ndarray:
    """Convert list of (x, y, z) tuples to numpy array."""
    return np.array(landmarks, dtype=np.float32)


# ── Flexion Level Quantization ───────────────────────────────────────────────

# Cruz Aldrete's 4-level system:
#   EXTENDED = 0%     → angle < 30°
#   CURVED   = 33%    → angle 30°-80°
#   BENT     = 66%    → angle 80°-130°
#   CLOSED   = 100%   → angle > 130°

FLEXION_THRESHOLDS = {
    "EXTENDED": (0, 30),
    "CURVED": (30, 80),
    "BENT": (80, 130),
    "CLOSED": (130, 180),
}


def quantize_flexion(angle: float) -> str:
    """Convert a flexion angle to a FlexionLevel string."""
    for level, (lo, hi) in FLEXION_THRESHOLDS.items():
        if lo <= angle < hi:
            return level
    return "CLOSED"


# ── Thumb Opposition ─────────────────────────────────────────────────────────

def compute_thumb_opposition(landmarks: np.ndarray) -> str:
    """
    Determine thumb opposition from landmark positions.

    OPPOSED:  Thumb rotated across palm (tip points toward fingers)
    PARALLEL: Thumb aligned with fingers plane
    CROSSED:  Thumb crossed over fingers

    Uses the angle between thumb direction vector and the palm normal.
    """
    wrist = landmarks[HandLandmark.WRIST.value]
    thumb_cmc = landmarks[HandLandmark.THUMB_CMC.value]
    thumb_tip = landmarks[HandLandmark.THUMB_TIP.value]
    index_mcp = landmarks[HandLandmark.INDEX_MCP.value]
    pinky_mcp = landmarks[HandLandmark.PINKY_MCP.value]

    # Palm plane normal (cross product of palm vectors)
    v_index = index_mcp - wrist
    v_pinky = pinky_mcp - wrist
    palm_normal = np.cross(v_index, v_pinky)
    palm_normal = palm_normal / (np.linalg.norm(palm_normal) + 1e-8)

    # Thumb direction
    thumb_dir = thumb_tip - thumb_cmc
    thumb_dir = thumb_dir / (np.linalg.norm(thumb_dir) + 1e-8)

    # Dot product with palm normal
    dot = abs(np.dot(thumb_dir, palm_normal))

    if dot > 0.6:
        return "OPPOSED"
    elif dot < 0.25:
        return "PARALLEL"
    else:
        return "PARALLEL"  # default to parallel


# ── Finger Spread ────────────────────────────────────────────────────────────

def compute_finger_spread(landmarks: np.ndarray) -> str:
    """
    Compute spread between extended fingers.

    Uses the angle between adjacent finger MCP-TIP vectors.
    """
    finger_tips = [
        HandLandmark.INDEX_TIP.value,
        HandLandmark.MIDDLE_TIP.value,
        HandLandmark.RING_TIP.value,
        HandLandmark.PINKY_TIP.value,
    ]
    finger_mcps = [
        HandLandmark.INDEX_MCP.value,
        HandLandmark.MIDDLE_MCP.value,
        HandLandmark.RING_MCP.value,
        HandLandmark.PINKY_MCP.value,
    ]

    angles = []
    for i in range(len(finger_tips) - 1):
        v1 = landmarks[finger_tips[i]] - landmarks[finger_mcps[i]]
        v2 = landmarks[finger_tips[i+1]] - landmarks[finger_mcps[i+1]]
        angle = _angle_between(v1, v2)
        angles.append(angle)

    mean_angle = np.mean(angles)

    if mean_angle < 8:
        return "CLOSED"
    elif mean_angle > 20:
        return "SPREAD"
    else:
        return "NEUTRAL"


# ── Finger Interaction ───────────────────────────────────────────────────────

def compute_finger_interaction(landmarks: np.ndarray, spread: str) -> str:
    """
    Detect finger interaction patterns.

    CROSSED: Index and middle fingers cross each other
    STACKED: Fingers layered on top of each other
    SPREAD:  Fingers separated (from spread computation)
    NONE:    Normal parallel configuration
    """
    if spread == "SPREAD":
        return "SPREAD"

    # Check for crossing: index tip is on the opposite side of middle tip
    index_tip = landmarks[HandLandmark.INDEX_TIP.value]
    middle_tip = landmarks[HandLandmark.MIDDLE_TIP.value]
    index_mcp = landmarks[HandLandmark.INDEX_MCP.value]
    middle_mcp = landmarks[HandLandmark.MIDDLE_MCP.value]

    # Cross detection via x-coordinate swap relative to MCP positions
    idx_offset = index_tip[0] - index_mcp[0]
    mid_offset = middle_tip[0] - middle_mcp[0]

    if (idx_offset > 0 and mid_offset < 0) or (idx_offset < 0 and mid_offset > 0):
        # Tips have crossed relative to their MCPs
        return "CROSSED"

    return "NONE"


# ── Thumb Contact ────────────────────────────────────────────────────────────

def compute_thumb_contact(landmarks: np.ndarray) -> bool:
    """
    Detect if thumb tip is touching any finger.

    Contact threshold: distance < 3% of hand span.
    """
    thumb_tip = landmarks[HandLandmark.THUMB_TIP.value]
    wrist = landmarks[HandLandmark.WRIST.value]
    middle_tip = landmarks[HandLandmark.MIDDLE_TIP.value]

    # Hand span = wrist to middle fingertip distance
    hand_span = np.linalg.norm(middle_tip - wrist)
    contact_threshold = hand_span * 0.12  # 12% of hand span

    finger_tips = [
        HandLandmark.INDEX_TIP.value,
        HandLandmark.MIDDLE_TIP.value,
        HandLandmark.RING_TIP.value,
        HandLandmark.PINKY_TIP.value,
    ]
    finger_pips = [
        HandLandmark.INDEX_PIP.value,
        HandLandmark.MIDDLE_PIP.value,
        HandLandmark.RING_PIP.value,
        HandLandmark.PINKY_PIP.value,
    ]

    for tip_idx in finger_tips + finger_pips:
        dist = np.linalg.norm(thumb_tip - landmarks[tip_idx])
        if dist < contact_threshold:
            return True

    return False


# ── Main Feature Extraction ──────────────────────────────────────────────────

def extract_hand_features(landmarks: list, confidence: float = 1.0) -> HandFeatures:
    """
    Extract LSM-PN relevant features from 21 hand landmarks.

    Args:
        landmarks: List of 21 (x, y, z) tuples (MediaPipe hand landmarks)
        confidence: Detection confidence (0-1)

    Returns:
        HandFeatures with flexion levels, thumb opposition, spread, etc.
    """
    if len(landmarks) != 21:
        raise ValueError(f"Expected 21 landmarks, got {len(landmarks)}")

    pts = _landmarks_to_array(landmarks)

    # ── Compute per-finger flexion ──────────────────────────────────────
    finger_flexions = {}
    for finger_name, joint_indices in FINGER_JOINTS.items():
        if finger_name == "thumb":
            # Thumb uses 3-point angle: CMC → MCP → TIP
            p1 = pts[HandLandmark.THUMB_CMC.value]
            p2 = pts[HandLandmark.THUMB_MCP.value]
            p3 = pts[HandLandmark.THUMB_TIP.value]
            flexion = _joint_angle(p1, p2, p3)
        else:
            # Other fingers: average of MCP-PIP-DIP-TIP chain
            indices = [j.value for j in joint_indices]
            angles = []
            for i in range(len(indices) - 2):
                a = _joint_angle(pts[indices[i]], pts[indices[i+1]], pts[indices[i+2]])
                angles.append(a)
            flexion = np.mean(angles) if angles else 0.0

        finger_flexions[finger_name] = float(flexion)

    # ── Quantize to FlexionLevel ────────────────────────────────────────
    levels = {name: quantize_flexion(angle) for name, angle in finger_flexions.items()}

    # ── Thumb opposition ────────────────────────────────────────────────
    thumb_opp = compute_thumb_opposition(pts)

    # ── Finger spread ───────────────────────────────────────────────────
    spread = compute_finger_spread(pts)

    # ── Finger interaction ──────────────────────────────────────────────
    interaction = compute_finger_interaction(pts, spread)

    # ── Thumb contact ───────────────────────────────────────────────────
    thumb_contact = compute_thumb_contact(pts)

    return HandFeatures(
        thumb_flexion=finger_flexions["thumb"],
        index_flexion=finger_flexions["index"],
        middle_flexion=finger_flexions["middle"],
        ring_flexion=finger_flexions["ring"],
        pinky_flexion=finger_flexions["pinky"],
        thumb_level=levels["thumb"],
        index_level=levels["index"],
        middle_level=levels["middle"],
        ring_level=levels["ring"],
        pinky_level=levels["pinky"],
        thumb_opposition=thumb_opp,
        thumb_contact=thumb_contact,
        spread=spread,
        interaction=interaction,
        landmarks=landmarks,
        confidence=confidence,
    )


# ── CM Matching ──────────────────────────────────────────────────────────────

def match_cm(hand_features: HandFeatures, top_k: int = 3) -> list[tuple[int, float]]:
    """
    Match extracted hand features against the 101 CM inventory.

    Returns top-k matches as (cm_id, similarity_score) tuples.
    Similarity is 0-1, where 1 = exact match.
    """
    from ..phonology.cm_inventory import CM_INVENTORY

    search = hand_features.to_cm_search_vector()
    results = []

    for entry in CM_INVENTORY:
        score = 0.0
        total_weight = 0.0

        # Finger state matching (weight: 10 per finger)
        for finger in ["index", "middle", "ring", "pinky"]:
            weight = 10.0
            total_weight += weight
            entry_state = getattr(entry, finger).value  # CMEntry uses: index, middle, ring, pinky
            if search["finger_states"][finger] == entry_state:
                score += weight
            elif _flexion_distance(search["finger_states"][finger], entry_state) == 1:
                score += weight * 0.5  # adjacent level = half credit

        # Thumb opposition (weight: 8)
        total_weight += 8.0
        if search["thumb_opposition"] == entry.thumb_opposition.value:
            score += 8.0

        # Thumb flexion (weight: 5)
        total_weight += 5.0
        if search["thumb_flexion"] == entry.thumb_flexion.value:
            score += 5.0
        elif _flexion_distance(search["thumb_flexion"], entry.thumb_flexion.value) == 1:
            score += 2.5

        # Spread (weight: 3)
        total_weight += 3.0
        if search["spread"] == entry.spread.value:
            score += 3.0

        # Thumb contact (weight: 3)
        total_weight += 3.0
        if search["thumb_contact"] == entry.thumb_contact:
            score += 3.0

        similarity = score / total_weight if total_weight > 0 else 0.0
        results.append((entry.cm_id, similarity))

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]


def _flexion_distance(level_a: str, level_b: str) -> int:
    """Distance between two flexion levels (0-3)."""
    order = ["EXTENDED", "CURVED", "BENT", "CLOSED"]
    try:
        return abs(order.index(level_a) - order.index(level_b))
    except ValueError:
        return 3
