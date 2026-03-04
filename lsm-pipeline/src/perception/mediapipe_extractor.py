"""
MediaPipe Holistic Keypoint Extractor

Extracts body, hand, and face landmarks from video frames using
Google's MediaPipe framework. This is the primary candidate for
the LSM pipeline due to its real-time speed and iOS/CoreML path.

Usage:
    extractor = MediaPipeExtractor()
    results = extractor.process_video("path/to/video.mp4")
    for frame_result in results:
        print(frame_result.inference_time_ms)
"""
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Generator

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

try:
    import mediapipe as mp
    HAS_MEDIAPIPE = True
except ImportError:
    HAS_MEDIAPIPE = False

import numpy as np

from .keypoint_schema import KeypointResult, BenchmarkResult


class MediaPipeExtractor:
    """
    Extract body, hand, and face keypoints using MediaPipe Holistic.

    MediaPipe Holistic provides:
      - 33 body landmarks (BlazePose)
      - 21 hand landmarks per hand (MediaPipe Hands)
      - 468 face landmarks (MediaPipe Face Mesh)

    For LSM pipeline:
      - Hand landmarks → CM (handshape) classification
      - Body landmarks → UB (location) classification
      - Face landmarks → RNM (non-manual features) in Phase 3
    """

    def __init__(
        self,
        static_image_mode: bool = False,
        model_complexity: int = 2,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ):
        if not HAS_MEDIAPIPE:
            raise ImportError(
                "mediapipe not installed. Run: pip install mediapipe"
            )
        if not HAS_CV2:
            raise ImportError(
                "opencv-python not installed. Run: pip install opencv-python"
            )

        self.mp_holistic = mp.solutions.holistic
        self.holistic = self.mp_holistic.Holistic(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self._model_complexity = model_complexity

    def process_frame(self, frame: np.ndarray, frame_index: int = 0) -> KeypointResult:
        """
        Process a single BGR frame and return keypoints.

        Args:
            frame: BGR image (OpenCV format)
            frame_index: Frame number in the video

        Returns:
            KeypointResult with all detected landmarks
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        t0 = time.perf_counter()
        results = self.holistic.process(rgb)
        t1 = time.perf_counter()

        inference_ms = (t1 - t0) * 1000.0

        # Extract body landmarks
        body = []
        if results.pose_landmarks:
            for lm in results.pose_landmarks.landmark:
                body.append((lm.x, lm.y, lm.z, lm.visibility))

        # Extract hand landmarks
        left_hand = []
        if results.left_hand_landmarks:
            for lm in results.left_hand_landmarks.landmark:
                left_hand.append((lm.x, lm.y, lm.z))

        right_hand = []
        if results.right_hand_landmarks:
            for lm in results.right_hand_landmarks.landmark:
                right_hand.append((lm.x, lm.y, lm.z))

        # Extract face landmarks
        face = []
        if results.face_landmarks:
            for lm in results.face_landmarks.landmark:
                face.append((lm.x, lm.y, lm.z))

        # Compute overall confidence
        confidence = 0.0
        n = 0
        if body:
            confidence += sum(lm[3] for lm in body) / len(body)
            n += 1
        if left_hand:
            confidence += 1.0  # hand presence = confident
            n += 1
        if right_hand:
            confidence += 1.0
            n += 1
        confidence = confidence / max(n, 1)

        return KeypointResult(
            body_landmarks=body,
            left_hand_landmarks=left_hand,
            right_hand_landmarks=right_hand,
            face_landmarks=face,
            inference_time_ms=inference_ms,
            frame_index=frame_index,
            confidence=confidence,
        )

    def process_video(
        self,
        video_path: str | Path,
        max_frames: Optional[int] = None,
        skip_frames: int = 0,
    ) -> Generator[KeypointResult, None, None]:
        """
        Process a video file frame by frame.

        Args:
            video_path: Path to video file
            max_frames: Maximum frames to process (None = all)
            skip_frames: Process every Nth frame (0 = every frame)

        Yields:
            KeypointResult for each processed frame
        """
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise FileNotFoundError(f"Cannot open video: {video_path}")

        frame_idx = 0
        processed = 0

        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if skip_frames > 0 and frame_idx % (skip_frames + 1) != 0:
                    frame_idx += 1
                    continue

                yield self.process_frame(frame, frame_idx)
                processed += 1
                frame_idx += 1

                if max_frames and processed >= max_frames:
                    break
        finally:
            cap.release()

    def benchmark_video(self, video_path: str | Path, max_frames: Optional[int] = None) -> BenchmarkResult:
        """
        Run a full benchmark on a video file.

        Returns:
            BenchmarkResult with aggregated statistics
        """
        inference_times = []
        total_frames = 0
        detected_frames = 0
        hand_detected_frames = 0
        body_completeness = []
        hand_completeness = []
        face_completeness = []

        for result in self.process_video(video_path, max_frames=max_frames):
            total_frames += 1
            inference_times.append(result.inference_time_ms)

            # Frame detection
            has_body = len(result.body_landmarks) > 0
            has_hands = len(result.left_hand_landmarks) > 0 and len(result.right_hand_landmarks) > 0
            has_any = has_body or has_hands or len(result.face_landmarks) > 0

            if has_any:
                detected_frames += 1
            if has_hands:
                hand_detected_frames += 1

            # Completeness (% of expected keypoints present)
            body_completeness.append(len(result.body_landmarks) / 33 * 100)
            hand_completeness.append(
                (len(result.left_hand_landmarks) + len(result.right_hand_landmarks)) / 42 * 100
            )
            face_completeness.append(len(result.face_landmarks) / 468 * 100)

        if total_frames == 0:
            raise ValueError(f"No frames processed from {video_path}")

        times = np.array(inference_times)
        mean_ms = float(np.mean(times))
        p95_ms = float(np.percentile(times, 95))
        fps = 1000.0 / mean_ms if mean_ms > 0 else 0

        # Model size estimate (MediaPipe Holistic)
        size_map = {0: 8.0, 1: 12.0, 2: 26.0}
        model_size = size_map.get(self._model_complexity, 26.0)

        return BenchmarkResult(
            model_name=f"MediaPipe Holistic (complexity={self._model_complexity})",
            total_frames=total_frames,
            detected_frames=detected_frames,
            hand_detected_frames=hand_detected_frames,
            mean_inference_ms=mean_ms,
            p95_inference_ms=p95_ms,
            fps=fps,
            hand_keypoint_completeness=float(np.mean(hand_completeness)),
            body_keypoint_completeness=float(np.mean(body_completeness)),
            face_keypoint_completeness=float(np.mean(face_completeness)),
            model_size_mb=model_size,
            ios_compatible=True,
            license="Apache-2.0",
            notes="Supports CoreML via MediaPipe Tasks API. Real-time on iPhone/iPad.",
        )

    def draw_landmarks(self, frame: np.ndarray, result: KeypointResult) -> np.ndarray:
        """Draw landmarks on a frame for visualization."""
        annotated = frame.copy()

        # Reconstruct MediaPipe results for drawing utility
        # (simplified — just draw circles at keypoint locations)
        h, w = frame.shape[:2]

        # Draw body
        for x, y, z, v in result.body_landmarks:
            if v > 0.5:
                cx, cy = int(x * w), int(y * h)
                cv2.circle(annotated, (cx, cy), 3, (0, 255, 0), -1)

        # Draw hands
        for hand_lms, color in [(result.left_hand_landmarks, (255, 0, 0)),
                                  (result.right_hand_landmarks, (0, 0, 255))]:
            for x, y, z in hand_lms:
                cx, cy = int(x * w), int(y * h)
                cv2.circle(annotated, (cx, cy), 2, color, -1)

        # Draw face (sparse — every 10th point)
        for i, (x, y, z) in enumerate(result.face_landmarks):
            if i % 10 == 0:
                cx, cy = int(x * w), int(y * h)
                cv2.circle(annotated, (cx, cy), 1, (255, 255, 0), -1)

        return annotated

    def close(self):
        """Release resources."""
        self.holistic.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
