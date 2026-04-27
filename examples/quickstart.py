"""Quickstart for scitex_capture.

Inspects display info and builds an animated GIF from synthetic frames.
We avoid taking a real screenshot because that requires a graphical session.
"""

import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

import scitex_capture as scap


def main() -> int:
    # Headless-safe: report what monitors and windows the host sees.
    info = scap.get_display_info()
    monitors = info.get("Monitors", {}).get("Count", 0)
    windows = info.get("Windows", {}).get("VisibleCount", 0)
    print(f"Detected {monitors} monitor(s), {windows} visible window(s).")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        # Generate 6 synthetic 120x120 frames with a moving vertical bar
        frame_paths = []
        for i in range(6):
            arr = np.full((120, 120, 3), 30, dtype=np.uint8)
            x = 10 + i * 18
            arr[:, x : x + 8, 0] = 255  # red bar
            p = tmp / f"frame_{i:02d}.png"
            Image.fromarray(arr).save(p)
            frame_paths.append(str(p))

        out = tmp / "demo.gif"
        result = scap.create_gif_from_files(frame_paths, str(out), duration=200)
        assert out.exists() and out.stat().st_size > 0
        print(
            f"Built GIF: {result} ({out.stat().st_size} bytes from {len(frame_paths)} frames)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
