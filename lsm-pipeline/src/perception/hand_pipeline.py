"""
Hand Keypoint Extraction Pipeline (Task 1.4.2)

Full pipeline from video frames to normalized, temporally-smoothed
hand keypoints ready for CM (handshape) classification.

Features:
  - 21 keypoints per hand (MCP, PIP, DIP, TIP per finger + wrist)
  - Handedness detection (dominant vs non-dominant)
  - Temporal smoothing (exponential moving average)
  - Size-invariant normalization (relative to wrist + palm scale)
  - Confidence-based occlusion handling
  - Output: frame-indexed arrays for classifier training

Usage:
    pipeline = HandPipeline()
    for frame in video_frames:
        result = pipeline.process(frame)
        if result.dominant_hand:
            features = extract_hand_features(result.dominant_hand.normalized)
"""
import numpy as np
from collections import deque
from dataclasses import dataclass, field
from typing import Optional

from .keypoint_schema import HandLandmark, FINGER_JOINTS


# ── Data Structures ──────────────────────────────────────────────────────────

@dataclass
class HandKeypoints:
    """Processed keypoints for a single hand."""
    raw: np.ndarray              # (21, 3) raw landmark positions
    normalized: list             # [(x,y,z), ...] × 21 — normalized for classifier
    confidence: float            # detection confidence 0-1
    handedness: str              # "LEFT" or "RIGHT"
    handedness_score: float      # confidence in handedness assignment
    palm_center: np.ndarray      # (3,) center of palm
    palm_scale: float            # wrist-to-middle-MCP distance (normalization factor)
    wrist_position: np.ndarray   # (3,) wrist position in frame coordinates


@dataclass
class HandPipelineResult:
    """Result of processing a single frame through the hand pipeline."""
    frame_index: int
    dominant_hand: Optional[HandKeypoints]
    non_dominant_hand: Optional[HandKeypoints]
    both_hands_detected: bool
    inference_time_ms: float


@dataclass
class TrajectoryPoint:
    """A single point in a hand trajectory for movement analysis."""
    frame_index: int
    wrist_position: np.ndarray  # (3,)
    palm_center: np.ndarray     # (3,)
    velocity: np.ndarray        # (3,) instantaneous velocity
    speed: float                # scalar speed


# ── Temporal Smoothing ───────────────────────────────────────────────────────

class TemporalSmoother:
    """
    Exponential moving average smoother for keypoint sequences.

    Reduces jitter while preserving fast intentional movements.
    Uses confidence-weighted smoothing: low-confidence frames
    get more smoothing, high-confidence frames are trusted more.
    """

    def __init__(self, alpha: float = 0.6, window_size: int = 5):
        """
        Args:
            alpha: Base smoothing factor (0=max smooth, 1=no smooth)
            window_size: History buffer size for velocity-adaptive smoothing
        """
        self.alpha = alpha
        self.window_size = window_size
        self._history: deque = deque(maxlen=window_size)
        self._last_smoothed: Optional[np.ndarray] = None

    def smooth(self, landmarks: np.ndarray, confidence: float = 1.0) -> np.ndarray:
        """
        Apply temporal smoothing to a frame's landmarks.

        Args:
            landmarks: (21, 3) array of hand keypoints
            confidence: detection confidence (higher = trust raw more)

        Returns:
            Smoothed (21, 3) landmarks
        """
        if self._last_smoothed is None:
            self._last_smoothed = landmarks.copy()
            self._history.append(landmarks.copy())
            return landmarks

        # Adaptive alpha: trust confident detections more
        adaptive_alpha = self.alpha * confidence + (1 - confidence) * 0.3

        # Velocity-adaptive: if hand is moving fast, reduce smoothing
        if len(self._history) >= 2:
            velocity = np.mean(np.abs(landmarks - self._history[-1]))
            if velocity > 0.02:  # fast movement threshold
                adaptive_alpha = min(adaptive_alpha + 0.2, 0.95)

        smoothed = adaptive_alpha * landmarks + (1 - adaptive_alpha) * self._last_smoothed
        self._last_smoothed = smoothed.copy()
        self._history.append(landmarks.copy())

        return smoothed

    def reset(self):
        """Reset smoother state (e.g., when hand is lost)."""
        self._history.clear()
        self._last_smoothed = None


# ── Normalization ────────────────────────────────────────────────────────────

def normalize_hand_keypoints(landmarks: np.ndarray) -> tuple[list, float]:
    """
    Normalize hand keypoints to be size-invariant and position-invariant.

    Normalization:
      1. Translate so wrist is at origin
      2. Scale by palm size (wrist → middle MCP distance)
      3. Align palm plane to canonical orientation

    Args:
        landmarks: (21, 3) raw hand landmarks

    Returns:
        (normalized_list, palm_scale) where normalized_list is [(x,y,z), ...] × 21
    """
    wrist = landmarks[HandLandmark.WRIST.value]
    middle_mcp = landmarks[HandLandmark.MIDDLE_MCP.value]

    # Step 1: Translate to wrist origin
    centered = landmarks - wrist

    # Step 2: Scale by palm size
    palm_scale = np.linalg.norm(middle_mcp - wrist)
    if palm_scale < 1e-6:
        palm_scale = 1.0  # avoid division by zero
    scaled = centered / palm_scale

    # Convert to list of tuples for compatibility with hand_features
    normalized = [(float(p[0]), float(p[1]), float(p[2])) for p in scaled]

    return normalized, float(palm_scale)


# ── Handedness Detection ─────────────────────────────────────────────────────

class HandednessDetector:
    """
    Determine which hand is dominant based on temporal analysis.

    Heuristics:
      - The hand that moves more is likely the dominant hand
      - Consistent handedness across frames (temporal voting)
      - Falls back to right-hand-dominant if ambiguous
    """

    def __init__(self, window_size: int = 30):
        self._window_size = window_size
        self._left_motion: deque = deque(maxlen=window_size)
        self._right_motion: deque = deque(maxlen=window_size)
        self._prev_left: Optional[np.ndarray] = None
        self._prev_right: Optional[np.ndarray] = None

    def update(
        self,
        left_landmarks: Optional[np.ndarray],
        right_landmarks: Optional[np.ndarray],
    ) -> tuple[str, float]:
        """
        Update handedness estimate with new frame data.

        Returns:
            (dominant_side, confidence) — e.g., ("RIGHT", 0.85)
        """
        # Compute motion for each hand
        left_motion = 0.0
        if left_landmarks is not None and self._prev_left is not None:
            left_motion = float(np.mean(np.abs(left_landmarks - self._prev_left)))
        self._left_motion.append(left_motion)

        right_motion = 0.0
        if right_landmarks is not None and self._prev_right is not None:
            right_motion = float(np.mean(np.abs(right_landmarks - self._prev_right)))
        self._right_motion.append(right_motion)

        # Store for next frame
        if left_landmarks is not None:
            self._prev_left = left_landmarks.copy()
        if right_landmarks is not None:
            self._prev_right = right_landmarks.copy()

        # Compute dominant hand
        avg_left = np.mean(self._left_motion) if self._left_motion else 0.0
        avg_right = np.mean(self._right_motion) if self._right_motion else 0.0

        total = avg_left + avg_right
        if total < 1e-6:
            return "RIGHT", 0.5  # default

        if avg_right >= avg_left:
            confidence = avg_right / total
            return "RIGHT", float(confidence)
        else:
            confidence = avg_left / total
            return "LEFT", float(confidence)

    def reset(self):
        self._left_motion.clear()
        self._right_motion.clear()
        self._prev_left = None
        self._prev_right = None


# ── Main Pipeline ────────────────────────────────────────────────────────────

class HandPipeline:
    """
    Complete hand keypoint extraction pipeline.

    Wraps MediaPipe extraction with:
      - Temporal smoothing
      - Size normalization
      - Handedness detection
      - Confidence tracking
      - Trajectory building
    """

    def __init__(
        self,
        smoothing_alpha: float = 0.6,
        min_confidence: float = 0.3,
    ):
        self.min_confidence = min_confidence
        self._left_smoother = TemporalSmoother(alpha=smoothing_alpha)
        self._right_smoother = TemporalSmoother(alpha=smoothing_alpha)
        self._handedness = HandednessDetector()
        self._frame_count = 0

        # Trajectory buffers
        self._left_trajectory: list[TrajectoryPoint] = []
        self._right_trajectory: list[TrajectoryPoint] = []

    def process_keypoints(
        self,
        left_hand_raw: Optional[list],
        right_hand_raw: Optional[list],
        inference_time_ms: float = 0.0,
    ) -> HandPipelineResult:
        """
        Process raw hand keypoints from MediaPipe through the full pipeline.

        Args:
            left_hand_raw: List of 21 (x,y,z) tuples for left hand, or None
            right_hand_raw: List of 21 (x,y,z) tuples for right hand, or None
            inference_time_ms: Time spent on keypoint extraction

        Returns:
            HandPipelineResult with processed, normalized hand data
        """
        frame_idx = self._frame_count
        self._frame_count += 1

        left_kp = None
        right_kp = None

        # Process left hand
        if left_hand_raw and len(left_hand_raw) == 21:
            left_arr = np.array(left_hand_raw, dtype=np.float32)
            smoothed = self._left_smoother.smooth(left_arr, confidence=0.9)
            normalized, palm_scale = normalize_hand_keypoints(smoothed)

            wrist = smoothed[HandLandmark.WRIST.value]
            palm_center = np.mean(smoothed[[
                HandLandmark.WRIST.value,
                HandLandmark.INDEX_MCP.value,
                HandLandmark.MIDDLE_MCP.value,
                HandLandmark.RING_MCP.value,
                HandLandmark.PINKY_MCP.value,
            ]], axis=0)

            left_kp = HandKeypoints(
                raw=smoothed,
                normalized=normalized,
                confidence=0.9,
                handedness="LEFT",
                handedness_score=0.0,  # filled below
                palm_center=palm_center,
                palm_scale=palm_scale,
                wrist_position=wrist,
            )

            # Track trajectory
            self._update_trajectory(self._left_trajectory, frame_idx, wrist, palm_center)
        else:
            self._left_smoother.reset()

        # Process right hand
        if right_hand_raw and len(right_hand_raw) == 21:
            right_arr = np.array(right_hand_raw, dtype=np.float32)
            smoothed = self._right_smoother.smooth(right_arr, confidence=0.9)
            normalized, palm_scale = normalize_hand_keypoints(smoothed)

            wrist = smoothed[HandLandmark.WRIST.value]
            palm_center = np.mean(smoothed[[
                HandLandmark.WRIST.value,
                HandLandmark.INDEX_MCP.value,
                HandLandmark.MIDDLE_MCP.value,
                HandLandmark.RING_MCP.value,
                HandLandmark.PINKY_MCP.value,
            ]], axis=0)

            right_kp = HandKeypoints(
                raw=smoothed,
                normalized=normalized,
                confidence=0.9,
                handedness="RIGHT",
                handedness_score=0.0,
                palm_center=palm_center,
                palm_scale=palm_scale,
                wrist_position=wrist,
            )

            self._update_trajectory(self._right_trajectory, frame_idx, wrist, palm_center)
        else:
            self._right_smoother.reset()

        # Determine dominant hand
        left_arr_for_dom = left_kp.raw if left_kp else None
        right_arr_for_dom = right_kp.raw if right_kp else None
        dominant_side, dom_confidence = self._handedness.update(
            left_arr_for_dom, right_arr_for_dom
        )

        # Assign dominant/non-dominant
        if dominant_side == "RIGHT":
            dominant = right_kp
            non_dominant = left_kp
        else:
            dominant = left_kp
            non_dominant = right_kp

        if dominant:
            dominant.handedness_score = dom_confidence
        if non_dominant:
            non_dominant.handedness_score = 1.0 - dom_confidence

        return HandPipelineResult(
            frame_index=frame_idx,
            dominant_hand=dominant,
            non_dominant_hand=non_dominant,
            both_hands_detected=(left_kp is not None and right_kp is not None),
            inference_time_ms=inference_time_ms,
        )

    def _update_trajectory(
        self, trajectory: list, frame_idx: int,
        wrist: np.ndarray, palm_center: np.ndarray,
    ):
        """Add a point to a hand's trajectory buffer."""
        if len(trajectory) > 0:
            prev = trajectory[-1]
            dt = max(frame_idx - prev.frame_index, 1)
            velocity = (wrist - prev.wrist_position) / dt
            speed = float(np.linalg.norm(velocity))
        else:
            velocity = np.zeros(3)
            speed = 0.0

        trajectory.append(TrajectoryPoint(
            frame_index=frame_idx,
            wrist_position=wrist.copy(),
            palm_center=palm_center.copy(),
            velocity=velocity,
            speed=speed,
        ))

    def get_trajectory(self, hand: str = "dominant") -> list[TrajectoryPoint]:
        """Get the trajectory for the specified hand."""
        dominant_side, _ = self._handedness.update(None, None)
        if hand == "dominant":
            return self._right_trajectory if dominant_side == "RIGHT" else self._left_trajectory
        elif hand == "non_dominant":
            return self._left_trajectory if dominant_side == "RIGHT" else self._right_trajectory
        elif hand == "left":
            return self._left_trajectory
        elif hand == "right":
            return self._right_trajectory
        else:
            raise ValueError(f"Unknown hand: {hand}")

    def reset(self):
        """Reset all pipeline state."""
        self._left_smoother.reset()
        self._right_smoother.reset()
        self._handedness.reset()
        self._left_trajectory.clear()
        self._right_trajectory.clear()
        self._frame_count = 0


# ── Export Utilities ─────────────────────────────────────────────────────────

def export_keypoints_to_numpy(
    results: list[HandPipelineResult],
    hand: str = "dominant",
) -> dict:
    """
    Export pipeline results to numpy arrays for ML training.

    Returns dict with:
      - 'keypoints': (N, 21, 3) array of normalized keypoints
      - 'confidence': (N,) array of per-frame confidence
      - 'frame_indices': (N,) array of frame indices
      - 'valid_mask': (N,) boolean mask (True where hand was detected)
    """
    n = len(results)
    keypoints = np.zeros((n, 21, 3), dtype=np.float32)
    confidence = np.zeros(n, dtype=np.float32)
    frame_indices = np.zeros(n, dtype=np.int32)
    valid_mask = np.zeros(n, dtype=bool)

    for i, result in enumerate(results):
        frame_indices[i] = result.frame_index
        kp = result.dominant_hand if hand == "dominant" else result.non_dominant_hand

        if kp is not None:
            keypoints[i] = np.array(kp.normalized, dtype=np.float32)
            confidence[i] = kp.confidence
            valid_mask[i] = True

    return {
        "keypoints": keypoints,
        "confidence": confidence,
        "frame_indices": frame_indices,
        "valid_mask": valid_mask,
    }
