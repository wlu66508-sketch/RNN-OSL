#!/usr/bin/env python3
"""Render a plume-only video from pre-generated puff/wind pickle files."""

from __future__ import annotations

import argparse
import glob
import sys
from pathlib import Path

import imageio.v2 as imageio
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
CODE_DIR = REPO_ROOT / "code"
sys.path.insert(0, str(CODE_DIR))

import sim_analysis  # noqa: E402


def choose_dataset(data_dir: Path, requested: str | None) -> str:
    if requested:
        return requested

    preferred = data_dir / "puff_data_constantx20b5_s1.pickle"
    if preferred.exists():
        return "constantx20b5_s1"

    matches = sorted(glob.glob(str(data_dir / "puff_data_constant*.pickle")))
    if not matches:
        raise FileNotFoundError(f"No puff_data_constant*.pickle found in {data_dir}")
    name = Path(matches[0]).name
    return name.removeprefix("puff_data_").removesuffix(".pickle")


def infer_time_window(data_dir: Path, dataset: str, start: float | None, end: float | None, duration: float) -> tuple[float, float]:
    wind_file = data_dir / f"wind_data_{dataset}.pickle"
    if not wind_file.exists():
        raise FileNotFoundError(wind_file)

    wind = pd.read_pickle(wind_file)
    data_min = float(wind["time"].min())
    data_max = float(wind["time"].max())

    end_time = data_max if end is None else float(end)
    start_time = max(data_min, end_time - duration) if start is None else float(start)
    if start_time >= end_time:
        raise ValueError(f"Invalid time window: start={start_time}, end={end_time}")
    return start_time, end_time


def select_frame_times(data_puffs: pd.DataFrame, start: float, end: float, fps: int) -> np.ndarray:
    available = np.sort(data_puffs["time"].unique())
    available = available[(available >= start) & (available <= end)]
    if len(available) == 0:
        raise ValueError("No puff frames in requested time window")

    n_frames = max(1, int(round((end - start) * fps)))
    targets = np.linspace(start, end, n_frames, endpoint=True)
    indices = np.searchsorted(available, targets, side="left")
    indices = np.clip(indices, 0, len(available) - 1)
    left = np.clip(indices - 1, 0, len(available) - 1)
    choose_left = np.abs(available[left] - targets) < np.abs(available[indices] - targets)
    indices[choose_left] = left[choose_left]
    return np.unique(available[indices])


def render_frame(data_puffs: pd.DataFrame, data_wind: pd.DataFrame, t_val: float, args: argparse.Namespace) -> np.ndarray:
    fig, ax = sim_analysis.plot_puffs_and_wind_vectors(
        data_puffs,
        data_wind,
        t_val,
        plotsize=(args.width, args.height),
        show=False,
    )
    ax.set_xlim(args.xlim)
    ax.set_ylim(args.ylim)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(f"{args.dataset}  t={t_val:.2f}s")
    fig.canvas.draw()
    frame = np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy()
    plt.close(fig)
    return frame


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a plume video from RNN_OSL constant plume pickle files.")
    parser.add_argument("--data-dir", default="/mnt/hgfs/Desktop/RNN_OSL", help="Directory with puff_data_*.pickle and wind_data_*.pickle")
    parser.add_argument("--dataset", default=None, help="Dataset suffix, for example constantx20b5_s1")
    parser.add_argument("--output", default=None, help="Output mp4 path. Defaults to this script directory.")
    parser.add_argument("--start", type=float, default=None, help="Start time in seconds. Default: end - duration")
    parser.add_argument("--end", type=float, default=None, help="End time in seconds. Default: latest wind time")
    parser.add_argument("--duration", type=float, default=10.0, help="Seconds to render when --start is omitted")
    parser.add_argument("--fps", type=int, default=15, help="Video frames per second")
    parser.add_argument("--env-dt", type=float, default=0.04, help="Plume data downsampling interval")
    parser.add_argument("--xlim", type=float, nargs=2, default=(-1.0, 12.0), help="Plot x limits")
    parser.add_argument("--ylim", type=float, nargs=2, default=(-1.8, 1.8), help="Plot y limits")
    parser.add_argument("--width", type=float, default=8.0, help="Figure width in inches")
    parser.add_argument("--height", type=float, default=4.0, help="Figure height in inches")
    args = parser.parse_args()

    data_dir = Path(args.data_dir).expanduser().resolve()
    args.dataset = choose_dataset(data_dir, args.dataset)
    start, end = infer_time_window(data_dir, args.dataset, args.start, args.end, args.duration)

    outdir = Path(__file__).resolve().parent
    output = Path(args.output).expanduser().resolve() if args.output else outdir / f"{args.dataset}_plume_{start:.2f}_{end:.2f}.mp4"
    output.parent.mkdir(parents=True, exist_ok=True)

    print(f"Dataset: {args.dataset}")
    print(f"Time window: {start:.2f}s to {end:.2f}s")
    print("Loading plume data...")
    data_puffs, data_wind = sim_analysis.load_plume(
        args.dataset,
        t_val_min=start,
        t_val_max=end,
        env_dt=args.env_dt,
        data_dir=str(data_dir),
    )
    frame_times = select_frame_times(data_puffs, start, end, args.fps)
    print(f"Rendering {len(frame_times)} frames to {output}")

    with imageio.get_writer(output, fps=args.fps, codec="libx264", quality=8, macro_block_size=16) as writer:
        for i, t_val in enumerate(frame_times, start=1):
            writer.append_data(render_frame(data_puffs, data_wind, float(t_val), args))
            if i == 1 or i == len(frame_times) or i % max(1, args.fps) == 0:
                print(f"{i}/{len(frame_times)} frames")

    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
