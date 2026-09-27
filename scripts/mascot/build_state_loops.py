"""Render matching, seamless 4:3 loops from COPIE's white-background poses.

Each clip begins and ends on the same animated idle pose. The middle of the
clip reveals its named state with small, state-specific motion. The original
PNG files are read only; generated MP4 files go into ``videos/`` beside them.

Run: python scripts/mascot/build_state_loops.py
"""

from __future__ import annotations

import argparse
import math
import subprocess
from pathlib import Path

import cv2
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = ROOT / "assets" / "mascot" / "states" / "white-4x3"
OUTPUT_DIR = INPUT_DIR / "videos"
STATES = (
    "front-laptop",
    "idle",
    "listening",
    "no-answer",
    "responding",
    "skill-guide",
    "success",
    "thinking",
)
WIDTH, HEIGHT = 1280, 960
FPS = 24
FRAMES = 96  # 4 seconds; frame 0 and frame 95 match exactly.


def load_pose(state: str) -> np.ndarray:
    path = INPUT_DIR / f"copie-{state}.png"
    with Image.open(path) as source:
        # Maintain the same scale and anchor for every pose. Do not crop a pose.
        fitted = ImageOps.contain(source.convert("RGB"), (WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (WIDTH, HEIGHT), "white")
    canvas.paste(fitted, ((WIDTH - fitted.width) // 2, (HEIGHT - fitted.height) // 2))
    return np.asarray(canvas).copy()


def smoothstep(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def action_weight(t: float) -> float:
    # Shared idle lead/tail gives every clip the same cut point in a playlist.
    return smoothstep((t - 0.55) / 0.35) * (1.0 - smoothstep((t - 3.10) / 0.35))


def move(frame: np.ndarray, angle: float = 0.0, zoom: float = 1.0,
         x: float = 0.0, y: float = 0.0) -> np.ndarray:
    matrix = cv2.getRotationMatrix2D((WIDTH / 2, HEIGHT * 0.58), angle, zoom)
    matrix[0, 2] += x
    matrix[1, 2] += y
    return cv2.warpAffine(
        frame, matrix, (WIDTH, HEIGHT), flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255),
    )


def idle_frame(image: np.ndarray, index: int) -> np.ndarray:
    phase = 2.0 * math.pi * index / (FRAMES - 1)
    return move(image, zoom=1.0 + 0.003 * math.sin(phase), y=-2.0 * math.sin(phase))


def action_frame(image: np.ndarray, state: str, t: float) -> np.ndarray:
    u = max(0.0, min(1.0, (t - 0.90) / 2.20))
    wave = math.sin(2.0 * math.pi * u)
    if state == "front-laptop":
        return move(image, zoom=1.0 + 0.004 * wave, y=-2.0 * math.sin(6.0 * math.pi * u))
    if state == "listening":
        return move(image, angle=1.1 * wave, x=2.0 * wave, y=-3.0 * math.sin(math.pi * u))
    if state == "no-answer":
        return move(image, angle=1.4 * wave, y=3.0 * math.sin(math.pi * u))
    if state == "responding":
        return move(image, angle=0.6 * wave, x=2.0 * wave, y=-4.0 * math.sin(2.0 * math.pi * u))
    if state == "skill-guide":
        return move(image, angle=0.7 * wave, zoom=1.0 + 0.005 * math.sin(math.pi * u))
    if state == "success":
        bounce = abs(math.sin(2.0 * math.pi * u))
        return move(image, angle=0.8 * wave, zoom=1.0 + 0.009 * bounce, y=-12.0 * bounce)
    if state == "thinking":
        return move(image, angle=1.0 * wave, x=3.0 * wave, y=2.0 * math.sin(math.pi * u))
    raise ValueError(f"Unknown action: {state}")


def motion_fields(idle: np.ndarray, action: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Estimate the movement between two poses for a short shape transition."""
    estimator = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    small_size = (WIDTH // 2, HEIGHT // 2)
    first = cv2.cvtColor(cv2.resize(idle, small_size), cv2.COLOR_RGB2GRAY)
    second = cv2.cvtColor(cv2.resize(action, small_size), cv2.COLOR_RGB2GRAY)
    forward = estimator.calc(first, second, None)
    backward = estimator.calc(second, first, None)
    return (
        cv2.resize(forward, (WIDTH, HEIGHT)) * 2.0,
        cv2.resize(backward, (WIDTH, HEIGHT)) * 2.0,
    )


def between(idle: np.ndarray, action: np.ndarray,
            fields: tuple[np.ndarray, np.ndarray], weight: float) -> np.ndarray:
    """Move matching image details before dissolving between the two poses."""
    y, x = np.mgrid[:HEIGHT, :WIDTH].astype(np.float32)
    forward, backward = fields
    old = cv2.remap(
        idle, x - weight * forward[:, :, 0], y - weight * forward[:, :, 1],
        cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255),
    )
    new = cv2.remap(
        action, x - (1.0 - weight) * backward[:, :, 0],
        y - (1.0 - weight) * backward[:, :, 1], cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255),
    )
    return cv2.addWeighted(old, 1.0 - weight, new, weight, 0)


def encode(state: str, idle: np.ndarray, action: np.ndarray) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    destination = OUTPUT_DIR / f"copie-{state}-loop.mp4"
    command = [
        imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WIDTH}x{HEIGHT}",
        "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264",
        "-preset", "medium", "-qp", "18", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(destination),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    fields = None if state == "idle" else motion_fields(idle, action)
    try:
        assert process.stdin is not None
        for index in range(FRAMES):
            base = idle_frame(idle, index)
            if state == "idle":
                frame = base
            else:
                t = 4.0 * index / (FRAMES - 1)
                weight = action_weight(t)
                if weight <= 0.0:
                    frame = base
                elif weight < 1.0:
                    assert fields is not None
                    frame = between(base, action, fields, weight)
                else:
                    frame = action_frame(action, state, t)
            process.stdin.write(frame.tobytes())
    finally:
        if process.stdin is not None:
            process.stdin.close()
    if process.wait() != 0:
        raise RuntimeError(f"Video encoding failed: {destination}")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=STATES, help="Render one state for inspection")
    args = parser.parse_args()
    idle = load_pose("idle")
    for state in ((args.only,) if args.only else STATES):
        action = idle if state == "idle" else load_pose(state)
        print(encode(state, idle, action), flush=True)


if __name__ == "__main__":
    main()
