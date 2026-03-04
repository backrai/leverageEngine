"""
CM (Handshape) Classifier (Task 1.5.1 — Architecture)

Classifies hand keypoints into one of the 101 Cruz Aldrete handshape
configurations. This module provides:

  1. Feature-based classifier: Uses hand_features.py geometric features
     with a lightweight MLP (works without training data via heuristic matching)
  2. Keypoint-based classifier: Trainable 1D-CNN on raw normalized keypoints
     (requires annotated corpus from Task 1.3.2)

The two approaches are complementary:
  - Feature-based: Interpretable, works day-one, ~70-80% accuracy estimated
  - Keypoint-based: Higher ceiling (~85%+ accuracy target), needs training data

Usage:
    # Feature-based (no training required)
    classifier = FeatureBasedCMClassifier()
    predictions = classifier.predict(hand_features)

    # Keypoint-based (after training)
    model = KeypointCMClassifier(num_classes=101)
    model.load("checkpoints/cm_classifier_v1.pt")
    predictions = model.predict(keypoint_array)
"""
import json
import numpy as np
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .hand_features import HandFeatures, extract_hand_features, match_cm


# ── Data Structures ──────────────────────────────────────────────────────────

@dataclass
class CMPrediction:
    """A single CM classification prediction."""
    cm_id: int            # Predicted CM number (1-101)
    confidence: float     # 0-1
    notation: str         # Cruz Aldrete notation string
    example_sign: str     # Example gloss
    alpha_code: Optional[str]  # e.g., "[B]", "[V]"


@dataclass
class CMClassifierResult:
    """Full classifier output with top-k predictions."""
    top_predictions: list[CMPrediction]   # Sorted by confidence
    hand_features: HandFeatures           # Extracted features used for classification
    method: str                           # "feature_based" or "keypoint_based"


# ── Feature-Based Classifier ─────────────────────────────────────────────────

class FeatureBasedCMClassifier:
    """
    Heuristic CM classifier using geometric hand features.

    Matches extracted hand features against the 101 CM inventory
    using weighted scoring on finger states, thumb parameters,
    spread, and contact.

    No training required — works day-one with the CM inventory.
    Expected accuracy: ~70-80% on clean data.
    """

    def __init__(self, top_k: int = 5):
        self.top_k = top_k
        # Pre-load CM inventory for fast matching
        from ..phonology.cm_inventory import CM_INVENTORY
        self._inventory = CM_INVENTORY

    def predict(self, hand_features: HandFeatures) -> CMClassifierResult:
        """
        Classify hand features into a CM.

        Args:
            hand_features: Extracted hand features from hand_features.py

        Returns:
            CMClassifierResult with top-k predictions
        """
        matches = match_cm(hand_features, top_k=self.top_k)

        predictions = []
        for cm_id, score in matches:
            entry = self._get_entry(cm_id)
            predictions.append(CMPrediction(
                cm_id=cm_id,
                confidence=score,
                notation=entry.cruz_aldrete_notation if entry else "?",
                example_sign=entry.example_sign if entry else "?",
                alpha_code=entry.alpha_code if entry else None,
            ))

        return CMClassifierResult(
            top_predictions=predictions,
            hand_features=hand_features,
            method="feature_based",
        )

    def predict_from_landmarks(self, landmarks: list) -> CMClassifierResult:
        """
        Classify directly from 21 hand landmarks.

        Args:
            landmarks: List of 21 (x, y, z) tuples

        Returns:
            CMClassifierResult
        """
        features = extract_hand_features(landmarks)
        return self.predict(features)

    def _get_entry(self, cm_id: int):
        """Get CM inventory entry by ID."""
        for entry in self._inventory:
            if entry.cm_id == cm_id:
                return entry
        return None


# ── Keypoint-Based Classifier (Architecture) ─────────────────────────────────

class KeypointCMClassifier:
    """
    Trainable CM classifier using raw normalized keypoints.

    Architecture: 1D-CNN on flattened 21×3 keypoint vectors.
    This is the architecture definition — training requires:
      1. Annotated corpus (Task 1.3.2)
      2. PyTorch or similar framework

    Architecture spec (for implementation with PyTorch):
        Input:  (batch, 63) — flattened 21×3 normalized keypoints
        Layer 1: Linear(63, 128) + ReLU + Dropout(0.3)
        Layer 2: Linear(128, 256) + ReLU + Dropout(0.3)
        Layer 3: Linear(256, 128) + ReLU + Dropout(0.2)
        Output:  Linear(128, 101) + Softmax
        Loss:    CrossEntropyLoss with label smoothing (0.1)
        Optimizer: AdamW(lr=1e-3, weight_decay=1e-4)

    Target metrics:
        - Top-1 accuracy > 85% on test set
        - Top-5 accuracy > 95%
        - Inference < 10ms per frame
    """

    def __init__(self, num_classes: int = 101, checkpoint_path: Optional[str] = None):
        self.num_classes = num_classes
        self._weights = None  # Loaded from checkpoint
        self._checkpoint_path = checkpoint_path

        if checkpoint_path and Path(checkpoint_path).exists():
            self.load(checkpoint_path)

    def predict(self, keypoints: np.ndarray) -> np.ndarray:
        """
        Predict CM class from normalized keypoints.

        Args:
            keypoints: (21, 3) or (batch, 21, 3) normalized keypoints

        Returns:
            (num_classes,) or (batch, num_classes) probability distribution

        Note: Returns uniform distribution if no model is loaded.
        """
        if keypoints.ndim == 2:
            keypoints = keypoints.reshape(1, -1)
        elif keypoints.ndim == 3:
            keypoints = keypoints.reshape(keypoints.shape[0], -1)

        if self._weights is None:
            # No model loaded — return uniform
            batch_size = keypoints.shape[0]
            return np.ones((batch_size, self.num_classes)) / self.num_classes

        # Forward pass with loaded weights (numpy implementation)
        return self._forward(keypoints)

    def _forward(self, x: np.ndarray) -> np.ndarray:
        """Simple forward pass with numpy weights."""
        if self._weights is None:
            return np.ones((x.shape[0], self.num_classes)) / self.num_classes

        # Layer 1
        x = x @ self._weights['w1'] + self._weights['b1']
        x = np.maximum(x, 0)  # ReLU

        # Layer 2
        x = x @ self._weights['w2'] + self._weights['b2']
        x = np.maximum(x, 0)

        # Layer 3
        x = x @ self._weights['w3'] + self._weights['b3']
        x = np.maximum(x, 0)

        # Output
        logits = x @ self._weights['w4'] + self._weights['b4']

        # Softmax
        exp_logits = np.exp(logits - np.max(logits, axis=1, keepdims=True))
        probs = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)

        return probs

    def load(self, path: str):
        """Load model weights from a .npz checkpoint."""
        data = np.load(path)
        self._weights = {k: data[k] for k in data.files}
        self._checkpoint_path = path

    def save(self, path: str):
        """Save model weights to a .npz checkpoint."""
        if self._weights:
            np.savez(path, **self._weights)

    @staticmethod
    def get_architecture_spec() -> dict:
        """Return the architecture specification for PyTorch implementation."""
        return {
            "architecture": "MLP-4Layer",
            "input_dim": 63,  # 21 keypoints × 3 coordinates
            "hidden_dims": [128, 256, 128],
            "output_dim": 101,
            "activation": "ReLU",
            "dropout": [0.3, 0.3, 0.2],
            "loss": "CrossEntropyLoss",
            "label_smoothing": 0.1,
            "optimizer": "AdamW",
            "learning_rate": 1e-3,
            "weight_decay": 1e-4,
            "batch_size": 64,
            "epochs": 100,
            "early_stopping_patience": 10,
            "augmentation": {
                "random_rotation_deg": 15,
                "scale_range": [0.85, 1.15],
                "temporal_jitter_frames": 2,
                "mirror_probability": 0.5,
                "noise_std": 0.01,
            },
            "target_metrics": {
                "top1_accuracy": 0.85,
                "top5_accuracy": 0.95,
                "inference_ms": 10,
            },
        }


# ── Data Augmentation for Training ──────────────────────────────────────────

def augment_keypoints(
    keypoints: np.ndarray,
    rotation_deg: float = 15.0,
    scale_range: tuple = (0.85, 1.15),
    noise_std: float = 0.01,
    mirror: bool = False,
) -> np.ndarray:
    """
    Augment hand keypoints for training data expansion.

    Args:
        keypoints: (21, 3) normalized keypoints
        rotation_deg: Max random rotation in degrees
        scale_range: (min, max) random scale factor
        noise_std: Gaussian noise standard deviation
        mirror: If True, mirror left↔right

    Returns:
        Augmented (21, 3) keypoints
    """
    pts = keypoints.copy()

    # Random rotation around Z axis
    angle = np.radians(np.random.uniform(-rotation_deg, rotation_deg))
    cos_a, sin_a = np.cos(angle), np.sin(angle)
    rotation_matrix = np.array([
        [cos_a, -sin_a, 0],
        [sin_a,  cos_a, 0],
        [0,      0,     1],
    ])
    pts = pts @ rotation_matrix.T

    # Random scale
    scale = np.random.uniform(*scale_range)
    pts *= scale

    # Gaussian noise
    pts += np.random.normal(0, noise_std, pts.shape)

    # Mirror (flip X axis)
    if mirror:
        pts[:, 0] *= -1

    return pts


# ── Ensemble Classifier ─────────────────────────────────────────────────────

class EnsembleCMClassifier:
    """
    Ensemble classifier combining feature-based and keypoint-based approaches.

    Strategy:
      - If keypoint model is loaded: weighted average of both
      - If no keypoint model: fall back to feature-based only
    """

    def __init__(
        self,
        keypoint_checkpoint: Optional[str] = None,
        feature_weight: float = 0.4,
        keypoint_weight: float = 0.6,
        top_k: int = 5,
    ):
        self.feature_classifier = FeatureBasedCMClassifier(top_k=top_k)
        self.keypoint_classifier = KeypointCMClassifier(
            checkpoint_path=keypoint_checkpoint
        )
        self.feature_weight = feature_weight
        self.keypoint_weight = keypoint_weight
        self.top_k = top_k
        self._has_keypoint_model = (
            keypoint_checkpoint is not None and
            Path(keypoint_checkpoint).exists() if keypoint_checkpoint else False
        )

    def predict(self, landmarks: list) -> CMClassifierResult:
        """
        Classify from raw 21-landmark list using ensemble.

        Args:
            landmarks: List of 21 (x, y, z) tuples

        Returns:
            CMClassifierResult with ensemble predictions
        """
        # Feature-based prediction
        features = extract_hand_features(landmarks)
        feature_result = self.feature_classifier.predict(features)

        if not self._has_keypoint_model:
            return feature_result

        # Keypoint-based prediction
        kp_array = np.array(landmarks, dtype=np.float32)
        kp_probs = self.keypoint_classifier.predict(kp_array)

        # Combine: feature scores + keypoint probabilities
        from ..phonology.cm_inventory import CM_INVENTORY

        combined_scores = {}
        for pred in feature_result.top_predictions:
            combined_scores[pred.cm_id] = self.feature_weight * pred.confidence

        for cm_idx in range(min(len(kp_probs[0]), 101)):
            cm_id = cm_idx + 1  # 1-indexed
            kp_score = float(kp_probs[0, cm_idx]) * self.keypoint_weight
            combined_scores[cm_id] = combined_scores.get(cm_id, 0) + kp_score

        # Sort and take top-k
        sorted_cms = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

        predictions = []
        for cm_id, score in sorted_cms[:self.top_k]:
            entry = self.feature_classifier._get_entry(cm_id)
            predictions.append(CMPrediction(
                cm_id=cm_id,
                confidence=score,
                notation=entry.cruz_aldrete_notation if entry else "?",
                example_sign=entry.example_sign if entry else "?",
                alpha_code=entry.alpha_code if entry else None,
            ))

        return CMClassifierResult(
            top_predictions=predictions,
            hand_features=features,
            method="ensemble" if self._has_keypoint_model else "feature_based",
        )
