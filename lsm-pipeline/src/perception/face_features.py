"""
Face Mesh Feature Extraction for RNM (Non-Manual Features) (Task 1.4.4)

Extracts non-manual signal features from MediaPipe Face Mesh (468/478 landmarks):
  - Eyebrow position → NEUTRAL, RAISED, FURROWED
  - Mouth shape → NEUTRAL, OPEN, CLOSED, ROUNDED, STRETCHED
  - Head orientation → NOD, SHAKE, TILT_LEFT, TILT_RIGHT, TILT_BACK, TILT_DOWN
  - Eye gaze direction
  - Body lean (requires body pose data)

These features map directly to the NonManualSpec in the LSM-PN schema.

Reference: Cruz Aldrete (2008) §4.6 — Rasgos No Manuales (Non-Manual Features)
MediaPipe Face Mesh provides 468 3D landmarks covering face contour,
eyebrows, eyes, nose, lips, and iris (478 with iris landmarks).
"""
import math
import numpy as np
from dataclasses import dataclass
from typing import Optional


# ── Key Face Mesh Landmark Indices ───────────────────────────────────────────
# MediaPipe Face Mesh uses 468 landmarks. These are the key ones for RNM.

class FaceLandmarkIdx:
    """Key MediaPipe Face Mesh landmark indices for RNM extraction."""
    # Eyebrows (inner → outer, for left and right)
    LEFT_EYEBROW = [336, 296, 334, 293, 300]   # inner to outer
    RIGHT_EYEBROW = [107, 66, 105, 63, 70]

    # Eyes
    LEFT_EYE_TOP = 159
    LEFT_EYE_BOTTOM = 145
    LEFT_EYE_INNER = 133
    LEFT_EYE_OUTER = 33

    RIGHT_EYE_TOP = 386
    RIGHT_EYE_BOTTOM = 374
    RIGHT_EYE_INNER = 362
    RIGHT_EYE_OUTER = 263

    # Iris (if available — indices 468-477)
    LEFT_IRIS_CENTER = 468
    RIGHT_IRIS_CENTER = 473

    # Lips
    UPPER_LIP_TOP = 13
    LOWER_LIP_BOTTOM = 14
    MOUTH_LEFT = 61
    MOUTH_RIGHT = 291
    UPPER_LIP_CENTER = 0
    LOWER_LIP_CENTER = 17

    # Nose
    NOSE_TIP = 1
    NOSE_BRIDGE = 6

    # Face contour / head orientation reference points
    FOREHEAD_CENTER = 10
    CHIN = 152
    LEFT_CHEEK = 234
    RIGHT_CHEEK = 454
    LEFT_TEMPLE = 127
    RIGHT_TEMPLE = 356


# ── Data Structures ──────────────────────────────────────────────────────────

@dataclass
class EyebrowFeatures:
    """Eyebrow position features."""
    left_height: float    # Relative height (normalized)
    right_height: float
    symmetry: float       # 0 = perfectly symmetric, 1 = fully asymmetric
    state: str           # NEUTRAL, RAISED, FURROWED
    furrow_score: float  # 0-1, how furrowed (inner brow distance)


@dataclass
class MouthFeatures:
    """Mouth shape features."""
    openness: float      # 0 = closed, 1 = fully open
    width: float         # Relative mouth width
    roundness: float     # 0 = stretched wide, 1 = perfectly round
    state: str          # NEUTRAL, OPEN, CLOSED, ROUNDED, STRETCHED
    aspect_ratio: float  # height/width


@dataclass
class HeadPoseFeatures:
    """Head orientation features."""
    pitch: float    # Up/down rotation (degrees). Negative = looking down
    yaw: float      # Left/right rotation (degrees). Negative = looking left
    roll: float     # Tilt (degrees). Negative = tilting left
    state: str     # NONE, NOD, SHAKE, TILT_LEFT, TILT_RIGHT, TILT_BACK, TILT_DOWN


@dataclass
class EyeGazeFeatures:
    """Eye gaze direction features."""
    left_iris_offset: np.ndarray   # (2,) offset from eye center
    right_iris_offset: np.ndarray
    gaze_direction: str  # UP, DOWN, LEFT, RIGHT, CENTER
    has_iris_data: bool


@dataclass
class NonManualFeatures:
    """Complete non-manual feature extraction result."""
    eyebrows: EyebrowFeatures
    mouth: MouthFeatures
    head_pose: HeadPoseFeatures
    eye_gaze: EyeGazeFeatures
    confidence: float

    def to_lsm_pn(self) -> dict:
        """Convert to LSM-PN NonManualSpec dict."""
        result = {
            "eyebrows": self.eyebrows.state,
            "mouth": self.mouth.state,
            "head": self.head_pose.state,
        }
        if self.eye_gaze.gaze_direction != "CENTER":
            result["eye_gaze"] = self.eye_gaze.gaze_direction
        return result


# ── Feature Extraction Functions ─────────────────────────────────────────────

def extract_eyebrow_features(landmarks: np.ndarray) -> EyebrowFeatures:
    """
    Extract eyebrow position from face mesh landmarks.

    Compares eyebrow height relative to eye positions.
    """
    # Left eyebrow mean height vs left eye top
    left_brow_y = np.mean([landmarks[i][1] for i in FaceLandmarkIdx.LEFT_EYEBROW])
    left_eye_y = landmarks[FaceLandmarkIdx.LEFT_EYE_TOP][1]

    # Right eyebrow mean height vs right eye top
    right_brow_y = np.mean([landmarks[i][1] for i in FaceLandmarkIdx.RIGHT_EYEBROW])
    right_eye_y = landmarks[FaceLandmarkIdx.RIGHT_EYE_TOP][1]

    # Face height reference (forehead to chin)
    face_height = abs(landmarks[FaceLandmarkIdx.CHIN][1] -
                      landmarks[FaceLandmarkIdx.FOREHEAD_CENTER][1])
    if face_height < 1e-6:
        face_height = 0.2

    # Normalized eyebrow heights (relative to eyes, scaled by face height)
    left_height = (left_eye_y - left_brow_y) / face_height
    right_height = (right_eye_y - right_brow_y) / face_height

    # Symmetry (0 = symmetric)
    avg_height = (left_height + right_height) / 2
    symmetry = abs(left_height - right_height) / max(avg_height, 0.01)

    # Inner brow distance → furrow detection
    left_inner = landmarks[FaceLandmarkIdx.LEFT_EYEBROW[0]]
    right_inner = landmarks[FaceLandmarkIdx.RIGHT_EYEBROW[0]]
    inner_dist = np.linalg.norm(left_inner - right_inner)
    # Normalize by face width
    face_width = np.linalg.norm(
        landmarks[FaceLandmarkIdx.LEFT_CHEEK] - landmarks[FaceLandmarkIdx.RIGHT_CHEEK]
    )
    furrow_score = max(0, 1.0 - inner_dist / (face_width * 0.15 + 1e-6))

    # Classify state
    if avg_height > 0.12 and furrow_score < 0.4:
        state = "RAISED"
    elif furrow_score > 0.6:
        state = "FURROWED"
    else:
        state = "NEUTRAL"

    return EyebrowFeatures(
        left_height=float(left_height),
        right_height=float(right_height),
        symmetry=float(min(symmetry, 1.0)),
        state=state,
        furrow_score=float(furrow_score),
    )


def extract_mouth_features(landmarks: np.ndarray) -> MouthFeatures:
    """
    Extract mouth shape features from face mesh landmarks.
    """
    upper_lip = landmarks[FaceLandmarkIdx.UPPER_LIP_TOP]
    lower_lip = landmarks[FaceLandmarkIdx.LOWER_LIP_BOTTOM]
    mouth_left = landmarks[FaceLandmarkIdx.MOUTH_LEFT]
    mouth_right = landmarks[FaceLandmarkIdx.MOUTH_RIGHT]

    # Mouth dimensions
    mouth_height = abs(lower_lip[1] - upper_lip[1])
    mouth_width = np.linalg.norm(mouth_right - mouth_left)

    # Face scale reference
    face_height = abs(landmarks[FaceLandmarkIdx.CHIN][1] -
                      landmarks[FaceLandmarkIdx.FOREHEAD_CENTER][1])
    if face_height < 1e-6:
        face_height = 0.2

    # Normalized openness
    openness = mouth_height / face_height

    # Aspect ratio
    aspect_ratio = mouth_height / max(mouth_width, 1e-6)

    # Roundness (how circular the mouth opening is)
    # Perfect round: aspect_ratio close to 1.0 and mouth_width moderate
    nose_width = np.linalg.norm(
        landmarks[FaceLandmarkIdx.NOSE_TIP] - landmarks[FaceLandmarkIdx.NOSE_BRIDGE]
    )
    relative_width = mouth_width / max(face_height * 0.4, 1e-6)
    roundness = 1.0 - abs(aspect_ratio - 0.6) if aspect_ratio < 1.2 else 0.0

    # Classify state
    if openness < 0.015:
        state = "CLOSED"
    elif openness > 0.08:
        if aspect_ratio > 0.5 and relative_width < 0.8:
            state = "ROUNDED"
        else:
            state = "OPEN"
    elif relative_width > 1.1:
        state = "STRETCHED"
    else:
        state = "NEUTRAL"

    return MouthFeatures(
        openness=float(openness),
        width=float(mouth_width),
        roundness=float(max(0, min(1, roundness))),
        state=state,
        aspect_ratio=float(aspect_ratio),
    )


def extract_head_pose(landmarks: np.ndarray) -> HeadPoseFeatures:
    """
    Estimate head pose (pitch, yaw, roll) from face mesh landmarks.

    Uses face geometry to estimate 3D head rotation without a
    dedicated PnP solver (lightweight approach using face mesh directly).
    """
    nose = landmarks[FaceLandmarkIdx.NOSE_TIP]
    forehead = landmarks[FaceLandmarkIdx.FOREHEAD_CENTER]
    chin = landmarks[FaceLandmarkIdx.CHIN]
    left_cheek = landmarks[FaceLandmarkIdx.LEFT_CHEEK]
    right_cheek = landmarks[FaceLandmarkIdx.RIGHT_CHEEK]

    # Face vertical axis (forehead → chin)
    face_vertical = chin - forehead
    face_vertical_norm = face_vertical / (np.linalg.norm(face_vertical) + 1e-8)

    # Face horizontal axis (left → right cheek)
    face_horizontal = right_cheek - left_cheek
    face_horizontal_norm = face_horizontal / (np.linalg.norm(face_horizontal) + 1e-8)

    # Pitch: angle of face vertical from true vertical
    # Looking down = nose-chin vector tilts forward (z decreases)
    pitch = math.degrees(math.atan2(face_vertical[2], -face_vertical[1]))

    # Yaw: left-right rotation
    # Looking right = nose shifts right relative to face center
    face_center = (left_cheek + right_cheek) / 2
    nose_offset = nose[0] - face_center[0]
    face_width = np.linalg.norm(face_horizontal)
    yaw = math.degrees(math.asin(np.clip(nose_offset / max(face_width * 0.5, 1e-6), -1, 1)))

    # Roll: head tilt
    roll = math.degrees(math.atan2(face_horizontal[1], face_horizontal[0]))

    # Classify state based on current pose (static analysis)
    # For dynamic analysis (NOD, SHAKE), temporal analysis is needed
    state = "NONE"
    if abs(pitch) > 15:
        state = "TILT_BACK" if pitch > 0 else "TILT_DOWN"
    elif abs(roll) > 12:
        state = "TILT_LEFT" if roll > 0 else "TILT_RIGHT"
    elif abs(yaw) > 15:
        state = "SHAKE"  # Note: static; true shake detection needs temporal

    return HeadPoseFeatures(
        pitch=float(pitch),
        yaw=float(yaw),
        roll=float(roll),
        state=state,
    )


def extract_eye_gaze(landmarks: np.ndarray) -> EyeGazeFeatures:
    """
    Extract eye gaze direction from face mesh landmarks.

    If iris landmarks (468-477) are available, uses iris position
    relative to eye bounds. Otherwise, estimates from eye aspect ratio.
    """
    has_iris = len(landmarks) > 470

    if has_iris:
        # Left iris
        left_iris = landmarks[FaceLandmarkIdx.LEFT_IRIS_CENTER]
        left_eye_center = (landmarks[FaceLandmarkIdx.LEFT_EYE_INNER] +
                          landmarks[FaceLandmarkIdx.LEFT_EYE_OUTER]) / 2
        left_offset = left_iris[:2] - left_eye_center[:2]

        # Right iris
        right_iris = landmarks[FaceLandmarkIdx.RIGHT_IRIS_CENTER]
        right_eye_center = (landmarks[FaceLandmarkIdx.RIGHT_EYE_INNER] +
                           landmarks[FaceLandmarkIdx.RIGHT_EYE_OUTER]) / 2
        right_offset = right_iris[:2] - right_eye_center[:2]
    else:
        left_offset = np.zeros(2)
        right_offset = np.zeros(2)

    # Average gaze direction
    avg_offset = (left_offset + right_offset) / 2

    # Classify
    if not has_iris or np.linalg.norm(avg_offset) < 0.005:
        direction = "CENTER"
    elif abs(avg_offset[0]) > abs(avg_offset[1]):
        direction = "RIGHT" if avg_offset[0] > 0 else "LEFT"
    else:
        direction = "DOWN" if avg_offset[1] > 0 else "UP"

    return EyeGazeFeatures(
        left_iris_offset=left_offset,
        right_iris_offset=right_offset,
        gaze_direction=direction,
        has_iris_data=has_iris,
    )


# ── Main Extraction ──────────────────────────────────────────────────────────

def extract_non_manual_features(
    face_landmarks: list,
    confidence: float = 1.0,
) -> NonManualFeatures:
    """
    Extract all non-manual features from MediaPipe Face Mesh landmarks.

    Args:
        face_landmarks: List of 468+ (x, y, z) tuples
        confidence: Face detection confidence

    Returns:
        NonManualFeatures with eyebrows, mouth, head pose, eye gaze
    """
    if len(face_landmarks) < 468:
        # Return neutral defaults
        return NonManualFeatures(
            eyebrows=EyebrowFeatures(0, 0, 0, "NEUTRAL", 0),
            mouth=MouthFeatures(0, 0, 0, "NEUTRAL", 0),
            head_pose=HeadPoseFeatures(0, 0, 0, "NONE"),
            eye_gaze=EyeGazeFeatures(np.zeros(2), np.zeros(2), "CENTER", False),
            confidence=0.0,
        )

    pts = np.array(face_landmarks, dtype=np.float32)

    eyebrows = extract_eyebrow_features(pts)
    mouth = extract_mouth_features(pts)
    head_pose = extract_head_pose(pts)
    eye_gaze = extract_eye_gaze(pts)

    return NonManualFeatures(
        eyebrows=eyebrows,
        mouth=mouth,
        head_pose=head_pose,
        eye_gaze=eye_gaze,
        confidence=confidence,
    )


# ── Temporal Analysis (for NOD/SHAKE detection) ─────────────────────────────

class HeadMotionAnalyzer:
    """
    Temporal head motion analyzer for detecting NOD and SHAKE gestures.

    Requires a sequence of frames to detect oscillatory patterns.
    """

    def __init__(self, window_size: int = 15, fps: float = 30.0):
        self._window_size = window_size
        self._fps = fps
        self._pitch_history: list[float] = []
        self._yaw_history: list[float] = []

    def update(self, head_pose: HeadPoseFeatures) -> str:
        """
        Update with new frame and return detected head gesture.

        Returns: "NOD", "SHAKE", or "NONE"
        """
        self._pitch_history.append(head_pose.pitch)
        self._yaw_history.append(head_pose.yaw)

        if len(self._pitch_history) > self._window_size:
            self._pitch_history.pop(0)
            self._yaw_history.pop(0)

        if len(self._pitch_history) < self._window_size // 2:
            return "NONE"

        # Detect oscillation in pitch (NOD)
        pitch_range = max(self._pitch_history) - min(self._pitch_history)
        pitch_crossings = self._count_zero_crossings(self._pitch_history)

        # Detect oscillation in yaw (SHAKE)
        yaw_range = max(self._yaw_history) - min(self._yaw_history)
        yaw_crossings = self._count_zero_crossings(self._yaw_history)

        if pitch_range > 8 and pitch_crossings >= 2:
            return "NOD"
        elif yaw_range > 10 and yaw_crossings >= 2:
            return "SHAKE"

        return "NONE"

    def _count_zero_crossings(self, values: list[float]) -> int:
        """Count zero crossings (relative to mean) in a signal."""
        if len(values) < 2:
            return 0
        mean = np.mean(values)
        centered = [v - mean for v in values]
        crossings = 0
        for i in range(1, len(centered)):
            if centered[i-1] * centered[i] < 0:
                crossings += 1
        return crossings

    def reset(self):
        self._pitch_history.clear()
        self._yaw_history.clear()
