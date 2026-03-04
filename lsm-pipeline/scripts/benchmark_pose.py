#!/usr/bin/env python3
"""
Pose Estimation Benchmark Script

Evaluates pose estimation models on LSM video data for Task 1.4.1.
Compares MediaPipe Holistic (at different complexity levels) and
generates a benchmark report.

Usage:
    python scripts/benchmark_pose.py --video path/to/video.mp4
    python scripts/benchmark_pose.py --video-dir data/benchmark_videos/
    python scripts/benchmark_pose.py --demo  # synthetic test

Output:
    - Console report with per-model metrics
    - JSON report at data/benchmarks/pose_benchmark_<timestamp>.json
"""
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np


def run_mediapipe_benchmark(video_path: str, complexity: int = 2, max_frames: int = 300):
    """Run MediaPipe Holistic benchmark."""
    try:
        from src.perception.mediapipe_extractor import MediaPipeExtractor
    except ImportError as e:
        print(f"  ⚠️  Skipping MediaPipe: {e}")
        return None

    print(f"  Running MediaPipe Holistic (complexity={complexity})...")

    with MediaPipeExtractor(model_complexity=complexity) as extractor:
        result = extractor.benchmark_video(video_path, max_frames=max_frames)

    print(f"    → {result.fps:.1f} fps, hands: {result.hand_keypoint_completeness:.1f}%")
    return result


def run_synthetic_benchmark():
    """
    Run a synthetic benchmark using generated hand landmark data.
    Tests the feature extraction pipeline without requiring actual video.
    """
    print("\n🧪 Running synthetic benchmark (no video required)...")
    print("   Testing hand feature extraction pipeline...\n")

    from src.perception.hand_features import (
        extract_hand_features, match_cm, quantize_flexion
    )

    # ── Test 1: Flexion quantization ────────────────────────────────────
    print("  1. Flexion level quantization:")
    test_angles = [0, 15, 45, 90, 120, 150, 180]
    for angle in test_angles:
        level = quantize_flexion(angle)
        print(f"     {angle:3d}° → {level}")

    # ── Test 2: Synthetic hand landmark generation ──────────────────────
    print("\n  2. Synthetic hand feature extraction:")

    # Generate a "flat hand" — all fingers extended (CM#1: 1234+/a+)
    flat_hand = _generate_flat_hand()
    features = extract_hand_features(flat_hand)
    print(f"     Flat hand → index: {features.index_level}, "
          f"middle: {features.middle_level}, "
          f"ring: {features.ring_level}, "
          f"pinky: {features.pinky_level}")
    print(f"     Thumb: {features.thumb_level} ({features.thumb_opposition}), "
          f"spread: {features.spread}")

    # Generate a "fist" — all fingers closed (CM#10: 1234-/a+)
    fist = _generate_fist()
    features_fist = extract_hand_features(fist)
    print(f"     Fist     → index: {features_fist.index_level}, "
          f"middle: {features_fist.middle_level}, "
          f"ring: {features_fist.ring_level}, "
          f"pinky: {features_fist.pinky_level}")

    # Generate index pointing — index extended, others closed (CM#55: 1+/o-)
    pointing = _generate_pointing()
    features_point = extract_hand_features(pointing)
    print(f"     Pointing → index: {features_point.index_level}, "
          f"middle: {features_point.middle_level}, "
          f"ring: {features_point.ring_level}, "
          f"pinky: {features_point.pinky_level}")

    # ── Test 3: CM matching ─────────────────────────────────────────────
    print("\n  3. CM inventory matching:")
    for name, landmarks, expected in [
        ("Flat hand (CM#1)", flat_hand, "1234+/a+"),
        ("Fist (CM#10)", fist, "1234-/a+"),
        ("Pointing (CM#55)", pointing, "1+/o-"),
    ]:
        feats = extract_hand_features(landmarks)
        matches = match_cm(feats, top_k=3)
        print(f"     {name}:")
        for cm_id, score in matches:
            from src.phonology.cm_inventory import get_cm
            cm = get_cm(cm_id)
            marker = "← expected" if cm.cruz_aldrete_notation == expected else ""
            print(f"       CM#{cm_id:3d} ({cm.cruz_aldrete_notation:15s}) "
                  f"score={score:.3f} {cm.example_sign} {marker}")

    print("\n  ✅ Synthetic benchmark complete!")
    return True


def _generate_flat_hand() -> list:
    """Generate 21 landmarks for a flat/extended hand."""
    # Wrist at origin, fingers extending along Y axis
    landmarks = [(0.0, 0.0, 0.0)] * 21

    # Wrist
    landmarks[0] = (0.5, 0.8, 0.0)

    # Thumb — extended along a diagonal
    landmarks[1] = (0.42, 0.75, 0.0)   # CMC
    landmarks[2] = (0.35, 0.70, 0.0)   # MCP
    landmarks[3] = (0.30, 0.65, 0.0)   # IP
    landmarks[4] = (0.25, 0.60, 0.0)   # TIP

    # Index — straight up
    landmarks[5] = (0.44, 0.68, 0.0)   # MCP
    landmarks[6] = (0.43, 0.58, 0.0)   # PIP
    landmarks[7] = (0.42, 0.48, 0.0)   # DIP
    landmarks[8] = (0.41, 0.38, 0.0)   # TIP

    # Middle — straight up
    landmarks[9]  = (0.50, 0.67, 0.0)  # MCP
    landmarks[10] = (0.50, 0.56, 0.0)  # PIP
    landmarks[11] = (0.50, 0.46, 0.0)  # DIP
    landmarks[12] = (0.50, 0.36, 0.0)  # TIP

    # Ring — straight up
    landmarks[13] = (0.56, 0.68, 0.0)  # MCP
    landmarks[14] = (0.56, 0.58, 0.0)  # PIP
    landmarks[15] = (0.56, 0.48, 0.0)  # DIP
    landmarks[16] = (0.56, 0.38, 0.0)  # TIP

    # Pinky — straight up
    landmarks[17] = (0.62, 0.70, 0.0)  # MCP
    landmarks[18] = (0.62, 0.61, 0.0)  # PIP
    landmarks[19] = (0.62, 0.52, 0.0)  # DIP
    landmarks[20] = (0.62, 0.43, 0.0)  # TIP

    return landmarks


def _generate_fist() -> list:
    """Generate 21 landmarks for a closed fist."""
    landmarks = [(0.0, 0.0, 0.0)] * 21

    # Wrist
    landmarks[0] = (0.5, 0.8, 0.0)

    # Thumb — tucked across
    landmarks[1] = (0.42, 0.75, 0.0)
    landmarks[2] = (0.38, 0.72, 0.0)
    landmarks[3] = (0.40, 0.70, 0.0)  # curled back
    landmarks[4] = (0.44, 0.71, 0.0)  # tip near palm

    # Index — fully curled
    landmarks[5] = (0.44, 0.68, 0.0)
    landmarks[6] = (0.44, 0.64, 0.02)
    landmarks[7] = (0.45, 0.68, 0.04)  # curled back
    landmarks[8] = (0.45, 0.72, 0.03)  # tip near palm

    # Middle — fully curled
    landmarks[9]  = (0.50, 0.67, 0.0)
    landmarks[10] = (0.50, 0.63, 0.02)
    landmarks[11] = (0.50, 0.67, 0.04)
    landmarks[12] = (0.50, 0.71, 0.03)

    # Ring — fully curled
    landmarks[13] = (0.56, 0.68, 0.0)
    landmarks[14] = (0.56, 0.64, 0.02)
    landmarks[15] = (0.56, 0.68, 0.04)
    landmarks[16] = (0.56, 0.72, 0.03)

    # Pinky — fully curled
    landmarks[17] = (0.62, 0.70, 0.0)
    landmarks[18] = (0.62, 0.66, 0.02)
    landmarks[19] = (0.62, 0.70, 0.04)
    landmarks[20] = (0.62, 0.74, 0.03)

    return landmarks


def _generate_pointing() -> list:
    """Generate 21 landmarks for index pointing (CM#55: 1+/o-)."""
    landmarks = list(_generate_fist())  # start from fist

    # Extend index finger only
    landmarks[5] = (0.44, 0.68, 0.0)   # MCP
    landmarks[6] = (0.43, 0.58, 0.0)   # PIP
    landmarks[7] = (0.42, 0.48, 0.0)   # DIP
    landmarks[8] = (0.41, 0.38, 0.0)   # TIP

    # Thumb opposed (rotated across)
    landmarks[1] = (0.42, 0.75, 0.0)
    landmarks[2] = (0.45, 0.72, 0.03)
    landmarks[3] = (0.48, 0.70, 0.04)
    landmarks[4] = (0.50, 0.69, 0.03)

    return landmarks


def generate_report(results: list, output_path: Path):
    """Generate JSON benchmark report."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "task": "1.4.1 — Pose Estimation Evaluation",
        "models": [],
    }

    for r in results:
        if r is None:
            continue
        report["models"].append({
            "name": r.model_name,
            "total_frames": r.total_frames,
            "detected_frames": r.detected_frames,
            "hand_detected_frames": r.hand_detected_frames,
            "mean_inference_ms": round(r.mean_inference_ms, 2),
            "p95_inference_ms": round(r.p95_inference_ms, 2),
            "fps": round(r.fps, 1),
            "hand_keypoint_completeness": round(r.hand_keypoint_completeness, 2),
            "body_keypoint_completeness": round(r.body_keypoint_completeness, 2),
            "face_keypoint_completeness": round(r.face_keypoint_completeness, 2),
            "model_size_mb": r.model_size_mb,
            "ios_compatible": r.ios_compatible,
            "license": r.license,
            "notes": r.notes,
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Report saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Pose Estimation Benchmark for LSM Pipeline")
    parser.add_argument("--video", type=str, help="Path to a single video file")
    parser.add_argument("--video-dir", type=str, help="Path to directory of video files")
    parser.add_argument("--max-frames", type=int, default=300, help="Max frames per video")
    parser.add_argument("--demo", action="store_true", help="Run synthetic demo (no video needed)")
    parser.add_argument("--output", type=str, default=None, help="Output JSON path")
    args = parser.parse_args()

    print("═" * 60)
    print("  LSM Pipeline — Pose Estimation Benchmark (Task 1.4.1)")
    print("═" * 60)

    if args.demo:
        run_synthetic_benchmark()
        return

    if not args.video and not args.video_dir:
        print("No video specified. Running synthetic demo...\n")
        run_synthetic_benchmark()
        return

    # Collect video files
    videos = []
    if args.video:
        videos.append(Path(args.video))
    if args.video_dir:
        vdir = Path(args.video_dir)
        videos.extend(sorted(vdir.glob("*.mp4")))
        videos.extend(sorted(vdir.glob("*.mov")))
        videos.extend(sorted(vdir.glob("*.avi")))

    if not videos:
        print("❌ No video files found")
        sys.exit(1)

    print(f"\n📹 Found {len(videos)} video(s)")

    all_results = []
    for video in videos:
        print(f"\n{'─'*60}")
        print(f"Video: {video.name}")
        print(f"{'─'*60}")

        # MediaPipe at different complexity levels
        for complexity in [1, 2]:
            result = run_mediapipe_benchmark(str(video), complexity, args.max_frames)
            if result:
                all_results.append(result)
                print(result.summary())

    # Generate report
    if all_results:
        output = Path(args.output) if args.output else (
            Path("data/benchmarks") /
            f"pose_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        generate_report(all_results, output)

    # Print summary comparison
    if len(all_results) > 1:
        print(f"\n{'═'*60}")
        print("  COMPARISON SUMMARY")
        print(f"{'═'*60}")
        print(f"{'Model':<40} {'FPS':>6} {'Hands%':>7} {'iOS':>4}")
        print(f"{'─'*40} {'─'*6} {'─'*7} {'─'*4}")
        for r in sorted(all_results, key=lambda x: x.hand_keypoint_completeness, reverse=True):
            print(f"{r.model_name:<40} {r.fps:>6.1f} {r.hand_keypoint_completeness:>6.1f}% "
                  f"{'✅' if r.ios_compatible else '❌':>4}")


if __name__ == "__main__":
    main()
