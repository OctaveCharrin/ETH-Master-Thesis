#!/usr/bin/env python3
"""Re-render p2eval_decision_time and p2eval_path_mechanism with the audit fixes.

Fixes applied relative to evaluation/generate_figures.py:

decision time
  * legend moved out of the plotting area (it clipped the tall "App Agent Only"
    bar) and the y-limit raised so the value labels have headroom;
  * value labels alternated in height so "0.0148"/"0.0126" no longer collide,
    and the app-decision bars are labelled too;
  * policy names changed to the ones Chapter 5's tables use.

path mechanism
  * the six-path legend moved below the figure, out of panel (a) where it sat on
    top of path 0's goodput trace;
  * rates relabelled Mbit/s to match the thesis units.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams["font.family"] = "serif"
rcParams["font.serif"] = ["DejaVu Serif"]
rcParams["font.size"] = 10
rcParams["axes.labelsize"] = 10
rcParams["axes.titlesize"] = 11
rcParams["xtick.labelsize"] = 9
rcParams["ytick.labelsize"] = 9
rcParams["legend.fontsize"] = 9
rcParams["figure.titlesize"] = 12
rcParams["axes.axisbelow"] = True

FULL_WIDTH = 7.0

# Names as Chapter 5's tables write them, so figure and table agree.
DISPLAY = {
    "learned": "Learned pair",
    "app_only": "App-only",
    "path_only_gcc": "Path-only (GCC rate)",
    "even": "Even split",
    "single": "Single best-active path",
    "proportional": "Proportional",
    "minrtt": "minRTT (MPQUIC default)",
    "webrtc": "WebRTC (GCC)",
    "random": "Random split",
}
COLORS = {
    "learned": "#1f77b4",
    "app_only": "#17becf",
    "path_only_gcc": "#5b2c9f",
    "even": "#ff7f0e",
    "single": "#2ca02c",
    "proportional": "#d62728",
    "minrtt": "#e377c2",
    "webrtc": "#8c564b",
    "random": "#7f7f7f",
}
ORDER = ["learned", "path_only_gcc", "webrtc", "minrtt", "single",
         "app_only", "proportional", "even", "random"]
# Short tick labels: at \linewidth the nine full names collided into an
# unreadable pile. The full names stay in the caption and the tables.
SHORT = {
    "learned": "Learned pair",
    "app_only": "App-only",
    "path_only_gcc": "Path-only",
    "even": "Even split",
    "single": "Single best",
    "proportional": "Proportional",
    "minrtt": "minRTT",
    "webrtc": "WebRTC",
    "random": "Random",
}


def disp(m):
    return DISPLAY.get(m, m.replace("_", " ").title())


def col(m):
    return COLORS.get(m, "#7f7f7f")


def _rolling(y, w):
    if w <= 1 or y.size < w:
        return y
    k = np.ones(w) / w
    return np.convolve(y, k, mode="same")


def fig_decision_time(summary, distributions, out):
    order = [m for m in ORDER if m in summary]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FULL_WIDTH + 0.6, 3.4),
                                 gridspec_kw={"wspace": 0.28})
    x = np.arange(len(order))
    w = 0.38
    eps = 1e-4
    app = np.array([summary[m]["app_decision_ms"]["mean"] for m in order])
    tra = np.array([summary[m]["path_decision_ms"]["mean"] for m in order])

    a1.bar(x - w / 2, np.maximum(app, eps), w, label="App agent (bitrate)",
           color="#4C72B0")
    a1.bar(x + w / 2, np.maximum(tra, eps), w, label="Transport agent (split)",
           color="#DD8452")
    a1.set_yscale("log")
    a1.set_ylabel("Decision time (ms, log)")
    a1.set_title("(a) Mean inference time per decision")
    a1.set_xticks(x)
    a1.set_xticklabels([SHORT[m] for m in order], rotation=30, ha="right")
    a1.grid(axis="y", alpha=0.3, which="both")
    # Headroom for the labels, and a legend placed above the axes so it cannot
    # sit on a bar (in the previous version it clipped the App-only bar).
    a1.set_ylim(6e-4, 6.0)
    a1.legend(loc="lower center", bbox_to_anchor=(0.5, 1.16), ncol=2,
              fontsize=8, frameon=False)
    # Labels set vertically above each split bar: side by side they collided
    # ("0.0148" ran into "0.0126") at this bar pitch.
    for i, v in enumerate(tra):
        a1.text(i + w / 2, max(v, eps) * 1.35, f"{v:.3g}", ha="center",
                va="bottom", fontsize=7, rotation=90, color="#8a4a1f")

    data = [np.maximum(np.asarray(distributions[m]["path_decision_ms"], float), eps)
            for m in order]
    data = [d if d.size else np.array([eps]) for d in data]
    bp = a2.boxplot(data, widths=0.6, patch_artist=True, showfliers=False)
    for patch, m in zip(bp["boxes"], order):
        patch.set_facecolor(col(m))
        patch.set_alpha(0.7)
    for med in bp["medians"]:
        med.set_color("black")
    a2.set_yscale("log")
    a2.set_ylabel("Split decision time (ms, log)")
    a2.set_title("(b) Per-frame split decision")
    a2.set_xticks(range(1, len(order) + 1))
    a2.set_xticklabels([SHORT[m] for m in order], rotation=30, ha="right")
    a2.grid(axis="y", alpha=0.3, which="both")
    a2.set_ylim(6e-3, 2.0)
    learned_mean = tra[order.index("learned")]
    a2.annotate(f"learned split: {learned_mean:.3f} ms mean\n"
                "frame budget 33.3 ms (off scale)",
                xy=(0.98, 0.955), xycoords="axes fraction", ha="right", va="top",
                fontsize=7, color="#444444")
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


def fig_path_metrics(traces, meta, out):
    tr = traces["learned"]
    t = np.asarray(tr.get("t", []), dtype=float)
    t = t - t[0] if t.size else t
    fps = int(round(meta.get("fps", 30)))

    def _as2d(field):
        arr = np.asarray(tr.get(field, []), dtype=float)
        if arr.size == 0:
            return None
        return arr.reshape(-1, 1) if arr.ndim == 1 else arr

    pthr, psrtt = _as2d("path_throughput_mbps"), _as2d("path_srtt_ms")
    ploss, split = _as2d("path_loss"), _as2d("split")
    n_paths = max(a.shape[1] for a in (pthr, psrtt, ploss, split) if a is not None)
    path_colors = plt.cm.viridis(np.linspace(0.15, 0.85, n_paths))
    paths_meta = meta.get("paths", [])

    def label(i):
        lab = f"Path {i}"
        if i < len(paths_meta) and isinstance(paths_meta[i], dict):
            rate = str(paths_meta[i].get("rate", "")).replace("Mbps", " Mbit/s")
            if rate:
                lab += f" ({rate.strip()})"
        return lab

    panels = [
        (pthr, "Per-path goodput (Mbit/s)", "(a) Path throughput", False),
        (psrtt, "Per-path sRTT (ms)", "(b) Path latency", True),
        (ploss, "Per-path loss", "(c) Path loss", True),
        (split, "Traffic split fraction", "(d) Allocated split", False),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(FULL_WIDTH, 5.3), sharex=True)
    axes = axes.ravel()
    handles = None
    for ax, (data, ylabel, title, smooth) in zip(axes, panels):
        for i in range(data.shape[1]):
            y = data[:, i]
            if smooth:
                y = _rolling(y, fps)
            ax.plot(t[: len(y)], y, color=path_colors[i % n_paths], lw=1.2,
                    label=label(i))
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(alpha=0.3)
        if handles is None:
            handles, labels = ax.get_legend_handles_labels()
    axes[3].set_ylim(0, 1)
    axes[2].set_xlabel("Time (s)")
    axes[3].set_xlabel("Time (s)")
    # Legend below the panels: in the previous version it sat inside panel (a)
    # and covered path 0's goodput trace over t = 20-27 s.
    fig.legend(handles, labels, loc="lower center", ncol=6, fontsize=8,
               frameon=False, bbox_to_anchor=(0.5, -0.015))
    fig.suptitle("Per-path network state and allocation — learned pair")
    fig.tight_layout(rect=(0, 0.05, 1, 0.96))
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    run = sys.argv[1]
    outdir = sys.argv[2]
    d = json.load(open(os.path.join(run, "evaluation_results.json")))
    summary = d["summary"]
    distributions = d.get("distributions", {})
    traces = d.get("traces", {})
    meta = d.get("meta", {})
    fig_decision_time(summary, distributions,
                      os.path.join(outdir, "p2eval_decision_time.png"))
    fig_path_metrics(traces, meta,
                     os.path.join(outdir, "p2eval_path_mechanism.png"))
