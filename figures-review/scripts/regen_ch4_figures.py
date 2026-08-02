#!/usr/bin/env python3
"""Re-render three Chapter 4 figures with the audit fixes.

Reads the same aggregate CSVs as
``scion-dqn-sim/src/pipeline/chapter4_seed_figures.py`` and keeps its palette,
markers and LNCS styling, so the redrawn figures drop in beside the others.

p1eval_ceiling
  * the seven-method legend moved out of panel (a), where it sat on top of the
    Random curve, into a shared legend below both panels;
  * y-axis relabelled to the quantity the chapter defines (residual bottleneck
    capacity), in Mbit/s rather than Mbps.

p1eval_probing
  * log x-axis: five of the seven methods sit at exactly 360 ms per selection
    and overplotted each other into an unreadable pile at the old linear scale;
  * per-point labels so each marker is identifiable without the legend;
  * legend moved below the axes.

p1eval_intent_boxplots
  * panel 4's percentage labels staggered so the three 0.48% labels no longer
    touch, and headroom added;
  * goodput axis relabelled as residual bottleneck capacity in Mbit/s.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

COLUMN_WIDTH = 3.5
FULL_WIDTH = 7.0
BAND_ALPHA = 0.18

COLORS = {
    "conditional_concat_2stream": "#0072B2",
    "conditional_concat": "#0072B2",
    "shortest_path": "#E69F00",
    "widest_path": "#009E73",
    "lowest_latency": "#D55E00",
    "ecmp": "#56B4E9",
    "scion_default": "#999999",
    "random": "#CC79A7",
}
MARKERS = {
    "conditional_concat_2stream": "o",
    "conditional_concat": "o",
    "shortest_path": "s",
    "widest_path": "^",
    "lowest_latency": "D",
    "ecmp": "P",
    "scion_default": "X",
    "random": "v",
}
ORDER = ["conditional_concat_2stream", "conditional_concat", "shortest_path",
         "widest_path", "lowest_latency", "ecmp", "scion_default", "random"]
INTENT_COLORS = {
    "bandwidth_max": "#E69F00",
    "delay_averse": "#009E73",
    "loss_averse": "#0072B2",
    "balanced_extreme": "#CC79A7",
}
INTENT_ORDER = ["bandwidth_max", "delay_averse", "loss_averse", "balanced_extreme"]

# The chapter defines "goodput" as residual bottleneck capacity on the chosen
# path (sec:p1design:env); the axis now says so rather than relying on a caption
# to undo the word "achieved".
CAPACITY_LABEL = "Residual bottleneck capacity (Mbit/s)"


def style():
    from matplotlib import rcParams
    rcParams["font.family"] = "serif"
    rcParams["font.serif"] = ["DejaVu Serif"]
    rcParams["font.size"] = 10
    rcParams["axes.labelsize"] = 10
    rcParams["axes.titlesize"] = 11
    rcParams["xtick.labelsize"] = 9
    rcParams["ytick.labelsize"] = 9
    rcParams["legend.fontsize"] = 9
    rcParams["axes.axisbelow"] = True


def read(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def f(row, key):
    try:
        return float(row[key])
    except (KeyError, TypeError, ValueError):
        return float("nan")


# --------------------------------------------------------------- 1. ceiling
def ceiling(csv_path, out):
    rows = read(csv_path)
    by = {}
    for r in rows:
        by.setdefault(r["method"], []).append(r)
    order = [m for m in ORDER if m in by]

    fig, axes = plt.subplots(1, 2, figsize=(FULL_WIDTH + 0.6, COLUMN_WIDTH + 0.35),
                             constrained_layout=True)
    for ax, col, ylabel in ((axes[0], "goodput_mean_mbps", CAPACITY_LABEL),
                            (axes[1], "reward_mean", "Composite reward")):
        for m in order:
            recs = sorted(by[m], key=lambda r: f(r, "congestion_mid_mean"))
            xs = np.array([f(r, "congestion_mid_mean") for r in recs])
            c = COLORS.get(m, "#333333")
            lo = np.array([f(r, f"{col}_ci_lo") for r in recs])
            hi = np.array([f(r, f"{col}_ci_hi") for r in recs])
            ax.fill_between(xs, lo, hi, color=c, alpha=BAND_ALPHA, lw=0, zorder=2)
            ax.plot(xs, [f(r, f"{col}_mean") for r in recs],
                    marker=MARKERS.get(m, "o"), markersize=6, linewidth=2, color=c,
                    markeredgecolor="white", markeredgewidth=0.6, zorder=4,
                    label=recs[0]["method_label"])
        ax.set_xlabel("Realized congestion (mean path utilization)")
        ax.set_ylabel(ylabel)
        ax.grid(alpha=0.3)

    n = int(f(by[order[0]][0], "n"))
    axes[0].set_title(f"{n} decisions per bin per method · bands: 95% CI over "
                      "5 training seeds", fontsize=7.0, color="#333333", loc="left")
    handles, labels = axes[0].get_legend_handles_labels()
    # Below both panels: inside panel (a) this legend covered the Random curve.
    fig.legend(handles, labels, loc="outside lower center", ncol=4, fontsize=8,
               frameon=False)
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


# --------------------------------------------------------------- 2. probing
def probing(csv_path, out):
    rows = {r["method"]: r for r in read(csv_path)}
    order = [m for m in ORDER if m in rows]

    fig, ax = plt.subplots(figsize=(FULL_WIDTH - 1.2, COLUMN_WIDTH + 0.4))
    # Five heuristics sit at exactly 360 ms, so their markers coincide and their
    # labels cannot be placed by a per-marker offset. Each label is given its own
    # anchor point and a leader line back to its marker.
    anchors = {
        "conditional_concat_2stream": (170.0, 9300.0, "left"),
        "widest_path": (4600.0, 9300.0, "right"),
        "ecmp": (760.0, 7250.0, "left"),
        "lowest_latency": (760.0, 6300.0, "left"),
        "scion_default": (760.0, 5350.0, "left"),
        "shortest_path": (760.0, 4400.0, "left"),
        "random": (760.0, 1850.0, "left"),
    }
    for m in order:
        r = rows[m]
        x = f(r, "probe_cost_per_selection_ms_mean")
        y = f(r, "goodput_mean_mbps_mean")
        c = COLORS.get(m, "#333333")
        ax.errorbar(x, y,
                    xerr=[[max(0.0, x - f(r, "probe_cost_per_selection_ms_ci_lo"))],
                          [max(0.0, f(r, "probe_cost_per_selection_ms_ci_hi") - x)]],
                    yerr=[[max(0.0, y - f(r, "goodput_mean_mbps_ci_lo"))],
                          [max(0.0, f(r, "goodput_mean_mbps_ci_hi") - y)]],
                    fmt="none", ecolor=c, elinewidth=1.4, capsize=3, zorder=3)
        ax.scatter(x, y, s=110, color=c, marker=MARKERS.get(m, "o"),
                   edgecolor="white", linewidth=0.9, zorder=4,
                   label=r["method_label"])
        ax_, ay, ha = anchors.get(m, (x * 1.6, y, "left"))
        leader = dict(arrowstyle="-", color=c, lw=0.7,
                      shrinkA=1, shrinkB=6, alpha=0.8)
        ax.annotate(f"{r['method_label']}  {y/1000:.1f} Gbit/s",
                    xy=(x, y), xytext=(ax_, ay), fontsize=7.5, color=c,
                    ha=ha, va="center", arrowprops=leader)
    ax.set_xscale("log")
    ax.set_xlim(95, 26000)
    ax.set_ylim(1000, 10400)
    ax.set_xlabel("Probing cost per selection (ms, log)")
    ax.set_ylabel(CAPACITY_LABEL)
    ax.grid(alpha=0.3, which="both", zorder=0)
    ax.annotate("better", xy=(0.015, 0.995), xytext=(0.115, 0.955),
                xycoords="axes fraction", textcoords="axes fraction",
                fontsize=8, ha="left", va="center", color="#555555",
                arrowprops=dict(arrowstyle="->", color="#555555", lw=1.2))
    ax.set_title("Bars: 95% CI over 5 training seeds. The heuristics are "
                 "deterministic and identical in every seed.",
                 fontsize=6.5, color="#333333", loc="left")
    # No legend: every marker carries its own label, which is what the old
    # legend was for, and the five coincident heuristics need the leader lines
    # to be told apart at all.
    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


# ------------------------------------------------------------- 3. boxplots
def seedvals(row, col):
    raw = row.get(f"{col}_seedvals", "")
    return np.array([float(v) for v in raw.split(";") if v]) if raw else np.array([])


def boxplots(box_csv, summary_csv, out):
    box = {}
    for r in read(box_csv):
        box.setdefault(r["metric"], {})[r["intent"]] = r
    summ = {r["intent"]: r for r in read(summary_csv)}
    labels = [summ[i]["intent_label"] for i in INTENT_ORDER]

    panels = [
        ("latency_ms", "latency_mean_ms", "Chosen latency (ms)",
         "delay_averse", "lower"),
        ("bandwidth_mbps", "goodput_mean_mbps", CAPACITY_LABEL,
         "bandwidth_max", "higher"),
        ("trust", "trust_mean", "Chosen path trust", "delay_averse", "higher"),
        (None, "loss_exposure_pct", "Selections with loss > 0 (%)",
         "loss_averse", "lower"),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(FULL_WIDTH + 0.7, 3.3),
                             constrained_layout=True)
    pos = list(range(1, 5))
    for ax, (metric, scol, ylab, target, better) in zip(axes, panels):
        if metric is None:
            vals = [f(summ[i], f"{scol}_mean") for i in INTENT_ORDER]
            err = np.array([
                [f(summ[i], f"{scol}_mean") - f(summ[i], f"{scol}_ci_lo")
                 for i in INTENT_ORDER],
                [f(summ[i], f"{scol}_ci_hi") - f(summ[i], f"{scol}_mean")
                 for i in INTENT_ORDER]])
            bars = ax.bar(pos, vals, width=0.6, zorder=3)
            for bar, i in zip(bars, INTENT_ORDER):
                bar.set_facecolor(INTENT_COLORS[i])
                bar.set_alpha(0.85)
                bar.set_edgecolor("#000000" if i == target else "#333333")
                bar.set_linewidth(2.2 if i == target else 1.0)
            ax.errorbar(pos, vals, yerr=np.clip(err, 0, None), fmt="none",
                        ecolor="#222222", elinewidth=1.1, capsize=3, zorder=5)
            top = max(v + e for v, e in zip(vals, err[1]))
            # Staggered heights: three of the four values are within 0.3 pp of
            # one another and their labels used to touch.
            for k, (x, v, e) in enumerate(zip(pos, vals, err[1])):
                ax.text(x, v + e + top * (0.05 if k % 2 == 0 else 0.14),
                        f"{v:.2f}%", ha="center", va="bottom", fontsize=7)
            ax.set_ylim(0, top * 1.32)
        else:
            st = []
            for i in INTENT_ORDER:
                r = box[metric][i]
                st.append(dict(med=f(r, "median"), q1=f(r, "q1"), q3=f(r, "q3"),
                               whislo=f(r, "p5"), whishi=f(r, "p95"), fliers=[]))
            bp = ax.bxp(st, positions=pos, patch_artist=True, showfliers=False,
                        widths=0.6, zorder=2)
            for patch, i in zip(bp["boxes"], INTENT_ORDER):
                patch.set_facecolor(INTENT_COLORS[i])
                patch.set_alpha(0.85)
                patch.set_edgecolor("#000000" if i == target else "#333333")
                patch.set_linewidth(2.2 if i == target else 1.0)
            for med in bp["medians"]:
                med.set_color("black")
        for x, i in zip(pos, INTENT_ORDER):
            v = seedvals(summ[i], scol)
            if v.size:
                ax.scatter(np.full(v.size, x), v, color="#111111", marker="_",
                           s=90, linewidths=1.3, zorder=6)
        ax.set_ylabel(ylab, fontsize=8)
        ax.set_title(f"{summ[target]['intent_label']} intent \u2192 {better}",
                     fontsize=8, color="#333333")
        ax.set_xticks(pos)
        ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=8)
        ax.grid(axis="y", alpha=0.3)

    axes[0].text(0.02, 0.02, "\u2014 = per-seed mean (5 seeds)",
                 transform=axes[0].transAxes, fontsize=6.5, va="bottom",
                 color="#333333")
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    style()
    agg = Path(sys.argv[1])
    out = Path(sys.argv[2])
    ceiling(agg / "ceiling_by_congestion_seeds.csv", out / "p1eval_ceiling.png")
    probing(agg / "probing_quality_seeds.csv", out / "p1eval_probing.png")
    boxplots(agg / "intent_selection_boxstats_seeds.csv",
             agg / "intent_selection_summary_seeds.csv",
             out / "p1eval_intent_boxplots.png")
