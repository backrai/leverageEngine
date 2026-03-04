"""
Keypoint Schema Definitions for Pose Estimation Evaluation.

Defines the target keypoint layout for the LSM pipeline, mapping
vendor-specific landmark indices to a unified schema.

Target keypoints:
  - Body:  33 landmarks (MediaPipe convention)
  - Hands:  21 landmarks × 2 = 42 total
  - Face: 468 landmarks (MediaPipe Face Mesh convention)
  - Total: 543 landmarks

Reference: Cruz Aldrete (2008) §4.2 — articulatory parameters require
keypoints at specific anatomical locations for UB classification.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


# ── Hand Landmark Indices (21 per hand) ──────────────────────────────────────

class HandLandmark(Enum):
    """MediaPipe / COCO-WholeBody hand landmark indices."""
    WRIST = 0
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4
    INDEX_MCP = 5
    INDEX_PIP = 6
    INDEX_DIP = 7
    INDEX_TIP = 8
    MIDDLE_MCP = 9
    MIDDLE_PIP = 10
    MIDDLE_DIP = 11
    MIDDLE_TIP = 12
    RING_MCP = 13
    RING_PIP = 14
    RING_DIP = 15
    RING_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20


# Finger joint groups — used for flexion angle computation (CM classification)
FINGER_JOINTS = {
    "thumb":  [HandLandmark.THUMB_CMC, HandLandmark.THUMB_MCP,
               HandLandmark.THUMB_IP, HandLandmark.THUMB_TIP],
    "index":  [HandLandmark.INDEX_MCP, HandLandmark.INDEX_PIP,
               HandLandmark.INDEX_DIP, HandLandmark.INDEX_TIP],
    "middle": [HandLandmark.MIDDLE_MCP, HandLandmark.MIDDLE_PIP,
               HandLandmark.MIDDLE_DIP, HandLandmark.MIDDLE_TIP],
    "ring":   [HandLandmark.RING_MCP, HandLandmark.RING_PIP,
               HandLandmark.RING_DIP, HandLandmark.RING_TIP],
    "pinky":  [HandLandmark.PINKY_MCP, HandLandmark.PINKY_PIP,
               HandLandmark.PINKY_DIP, HandLandmark.PINKY_TIP],
}


# ── Body Landmark Indices (33, MediaPipe convention) ─────────────────────────

class BodyLandmark(Enum):
    """MediaPipe Pose 33-landmark layout."""
    NOSE = 0
    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3
    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6
    LEFT_EAR = 7
    RIGHT_EAR = 8
    MOUTH_LEFT = 9
    MOUTH_RIGHT = 10
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_PINKY = 17
    RIGHT_PINKY = 18
    LEFT_INDEX = 19
    RIGHT_INDEX = 20
    LEFT_THUMB = 21
    RIGHT_THUMB = 22
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32


# Body landmarks critical for LSM UB (location) classification
# Maps Cruz Aldrete location codes → body landmarks
UB_CRITICAL_LANDMARKS = {
    # Head & Face
    "Fr": BodyLandmark.NOSE,                # forehead (approximate)
    "Au": [BodyLandmark.LEFT_EAR, BodyLandmark.RIGHT_EAR],
    "Os": [BodyLandmark.MOUTH_LEFT, BodyLandmark.MOUTH_RIGHT],
    "Oc": [BodyLandmark.LEFT_EYE, BodyLandmark.RIGHT_EYE],
    # Trunk
    "Um": [BodyLandmark.LEFT_SHOULDER, BodyLandmark.RIGHT_SHOULDER],
    "Pe": [BodyLandmark.LEFT_SHOULDER, BodyLandmark.RIGHT_SHOULDER],  # chest approximated
    "Ve": [BodyLandmark.LEFT_HIP, BodyLandmark.RIGHT_HIP],  # stomach approximated
    # Arm
    "Cut": [BodyLandmark.LEFT_ELBOW, BodyLandmark.RIGHT_ELBOW],
    "Car": [BodyLandmark.LEFT_WRIST, BodyLandmark.RIGHT_WRIST],
}


# ── Evaluation Metrics ───────────────────────────────────────────────────────

@dataclass
class KeypointResult:
    """Result of extracting keypoints from a single frame."""
    body_landmarks: list        # [(x, y, z, visibility), ...] × 33
    left_hand_landmarks: list   # [(x, y, z), ...] × 21
    right_hand_landmarks: list  # [(x, y, z), ...] × 21
    face_landmarks: list        # [(x, y, z), ...] × 468
    inference_time_ms: float
    frame_index: int
    confidence: float           # overall detection confidence


@dataclass
class BenchmarkResult:
    """Aggregated benchmark result for a model on a video set."""
    model_name: str
    total_frames: int
    detected_frames: int        # frames with at least partial detection
    hand_detected_frames: int   # frames where BOTH hands detected
    mean_inference_ms: float
    p95_inference_ms: float
    fps: float
    hand_keypoint_completeness: float   # % of hand keypoints detected
    body_keypoint_completeness: float
    face_keypoint_completeness: float
    model_size_mb: float
    ios_compatible: bool
    license: str
    notes: str = ""

    def summary(self) -> str:
        return (
            f"{'─'*60}\n"
            f"Model: {self.model_name}\n"
            f"  Frames: {self.detected_frames}/{self.total_frames} "
            f"({100*self.detected_frames/max(self.total_frames,1):.1f}%)\n"
            f"  Hands detected: {self.hand_detected_frames}/{self.total_frames} "
            f"({100*self.hand_detected_frames/max(self.total_frames,1):.1f}%)\n"
            f"  Speed: {self.fps:.1f} fps "
            f"(mean {self.mean_inference_ms:.1f}ms, p95 {self.p95_inference_ms:.1f}ms)\n"
            f"  Completeness — Hand: {self.hand_keypoint_completeness:.1f}%, "
            f"Body: {self.body_keypoint_completeness:.1f}%, "
            f"Face: {self.face_keypoint_completeness:.1f}%\n"
            f"  Model size: {self.model_size_mb:.1f} MB | "
            f"iOS: {'✅' if self.ios_compatible else '❌'} | "
            f"License: {self.license}\n"
            f"{'─'*60}"
        )


# ── Keypoint Count Constants ────────────────────────────────────────────────

KEYPOINT_COUNTS = {
    "mediapipe_holistic": {
        "body": 33,
        "hand": 21,  # per hand
        "face": 468,
        "total": 33 + 42 + 468,
    },
    "dwpose_wholebody": {
        "body": 17,     # COCO body
        "hand": 21,     # per hand
        "face": 68,     # COCO face
        "total": 17 + 42 + 68 + 6,  # +6 foot
    },
    "rtmpose_wholebody": {
        "body": 17,
        "hand": 21,
        "face": 68,
        "total": 133,  # COCO-WholeBody 133
    },
    "smpler_x": {
        "body": 22,     # SMPL joints
        "hand": 15,     # per hand (MANO model)
        "face": 68,     # FLAME model
        "total": 22 + 30 + 68,  # full mesh has many more
    },
}
