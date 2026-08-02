#!/usr/bin/env python3
"""Chapter-5 thesis figures that no single ``evaluation_results.json`` can render.

``evaluation/generate_figures.py`` renders one evaluation directory. The figures
here aggregate *across* runs -- across training seeds, across intents, across
path counts -- which is what the reporting contract (``docs/RESULTS.md`` §10)
asks for: a margin without its `trainSD` is not a result.

Subcommands (each writes a print-resolution PNG to ``--out``):

* ``qoe-bars``       -- mean QoE by policy x intent, error bars = trainSD, from the
                        three diagonal ``runs/ab-prof2-ev*-tr*/ab_summary.json``
                        three-seed aggregates. Replaces the 8-row table of §3.2.
* ``training-curves`` -- per-episode QoE / loss / VMAF per intent from every
                        ``runs/*/stats.json`` history, one line per training seed,
                        plus the attention-pool arm whose third seed collapsed.
* ``intent-sweep``   -- bitrate / VMAF / latency vs lambda for both conditioned
                        arms, from ``runs/sweep-*/intent_sweep.json``.
* ``pathcount``      -- QoE and decision time vs live path count, from the
                        ``runs/pc-*`` sweep + ``runs/pc-decision-bench.json``.
* ``regime-map``     -- the W4 2-D map: network regime x intent, cell value = the
                        app-only/learned recovery ratio, from ``runs/w4-*``.

    uv run --extra viz python scripts/thesis_figures.py qoe-bars \
        --out ~/thesis-report/figures/p2eval_qoe_bars.png
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os
import statistics
import sys
from typing import Dict, List, Optional, Sequence

import numpy as np

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import rcParams
    from matplotlib.lines import Line2D
except ImportError:  # pragma: no cover
    sys.exit("matplotlib is required: uv sync --extra viz")

_ROOT = "/home/ubuntu/rl-mpquic"

# Match evaluation/generate_figures.py's LNCS-ish serif styling so the p2eval_*
# figures are visually one family in the thesis.
rcParams["font.family"] = "serif"
rcParams["font.serif"] = ["Times New Roman", "DejaVu Serif", "serif"]
rcParams["font.size"] = 9
rcParams["axes.labelsize"] = 9
rcParams["axes.titlesize"] = 10
rcParams["xtick.labelsize"] = 8
rcParams["ytick.labelsize"] = 8
rcParams["legend.fontsize"] = 8
rcParams["axes.axisbelow"] = True

COLUMN_WIDTH = 3.5
FULL_WIDTH = 7.0
DPI = 400  # print resolution

DISPLAY = {
    # Names as Chapter 5's tables write them, so figure and table agree.
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
# Intent axis, ordered by how strict the deadline is (180 / 400 / 800 ms).
INTENTS = ["interactive", "presenter", "passive"]
INTENT_COLOR = {"interactive": "#1b4f72", "presenter": "#2e86c1", "passive": "#a9cce3"}
SEED_COLOR = ["#1f77b4", "#2ca02c", "#d62728", "#9467bd", "#ff7f0e", "#8c564b"]


def disp(p: str) -> str:
    return DISPLAY.get(p, p.replace("_", " "))


def _save(fig, out: str) -> None:
    out = os.path.expanduser(out)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}")


def _load(path: str):
    with open(os.path.expanduser(path)) as fh:
        return json.load(fh)


# --------------------------------------------------------------------------- #
# p2eval_qoe_bars -- QoE by policy x intent, trainSD error bars
# --------------------------------------------------------------------------- #

def cmd_qoe_bars(args) -> None:
    """Grouped bars: mean QoE per policy, one bar per intent, yerr = trainSD.

    Source is the *diagonal* of D2b -- each role's own specialists graded under
    that role -- i.e. the three-seed aggregate behind §3.2's table, not the
    single evaluation cell ``figure1_qoe`` would draw.
    """
    data: Dict[str, Dict[str, Dict[str, float]]] = {}
    for intent in INTENTS:
        d = _load(f"{args.runs}/ab-prof2-ev{intent}-tr{intent}/ab_summary.json")
        arm = d["sets"][intent]
        data[intent] = {
            p: {"mean": v["qoe"]["mean"], "tsd": v["qoe"].get("train_std", 0.0)}
            for p, v in arm.items()
        }
        n_ck = d["meta"]["train_checkpoints"][intent]
        n_cells = arm["learned"]["qoe"]["n"]
        print(f"{intent}: {n_ck} training seeds x {len(d['meta']['seeds'])} eval "
              f"seeds = {n_cells} cells")

    # Order policies by their mean over the three intents, best first.
    policies = sorted(
        data["interactive"],
        key=lambda p: statistics.fmean(data[i][p]["mean"] for i in INTENTS),
        reverse=True,
    )
    x = np.arange(len(policies))
    w = 0.26
    fig, ax = plt.subplots(figsize=(FULL_WIDTH, 3.1))
    for k, intent in enumerate(INTENTS):
        means = [data[intent][p]["mean"] for p in policies]
        errs = [data[intent][p]["tsd"] for p in policies]
        ax.bar(
            x + (k - 1) * w, means, w, yerr=errs, capsize=2.2,
            label=f"{intent}", color=INTENT_COLOR[intent],
            edgecolor="black",
            linewidth=[1.5 if p == "learned" else 0.5 for p in policies],
            error_kw={"elinewidth": 0.9, "capthick": 0.9, "ecolor": "#333333"},
        )
    ax.set_xticks(x)
    ax.set_xticklabels([disp(p) for p in policies], rotation=22, ha="right")
    ax.set_ylabel("Mean QoE")
    ax.set_title(
        "QoE by policy and intent (3 training x 3 evaluation seeds; bars = trainSD)"
    )
    ax.legend(title="Evaluation intent", ncol=3, frameon=True, loc="upper right")
    ax.grid(axis="y", alpha=0.3)
    ax.axhline(0.0, color="black", linewidth=0.6)
    ax.set_ylim(min(0.0, min(data[i][p]["mean"] for i in INTENTS for p in policies)) - 0.02,
                max(data[i][p]["mean"] for i in INTENTS for p in policies) + 0.16)
    _save(fig, args.out)


# --------------------------------------------------------------------------- #
# p2app_training_curves -- per-episode learning curves, one line per seed
# --------------------------------------------------------------------------- #

_CURVE_ROWS = [
    ("app_reward_mean", "App QoE"),
    ("loss_mean", "Loss fraction"),
    ("vmaf_mean", "VMAF"),
]


def _history(run_dir: str) -> List[dict]:
    return _load(os.path.join(run_dir, "stats.json"))["history"]


def _smooth(y: Sequence[float], w: int) -> np.ndarray:
    y = np.asarray(y, dtype=float)
    if w <= 1 or y.size < w:
        return y
    k = np.ones(w) / w
    pad = np.r_[np.full(w // 2, y[0]), y, np.full(w - 1 - w // 2, y[-1])]
    return np.convolve(pad, k, mode="valid")


def cmd_training_curves(args) -> None:
    """3 metrics x 4 arms; one line per training seed, collapsed seeds flagged.

    The fourth column is the attention-pool arm, whose third seed collapsed --
    that is the point of the figure. §5 reports the arm as "not significant with
    trainSD 0.151"; a training curve is the only artifact that shows the 0.151 is
    one run failing rather than three runs disagreeing mildly.
    """
    columns = [(f"{i}", f"{args.runs}/prof2-{i}-s{{s}}", (1, 2, 3), i) for i in INTENTS]
    columns.append(("attention pool", f"{args.runs}/dyn-attn-s{{s}}", (1, 2, 3),
                    "attn"))

    fig, axes = plt.subplots(
        len(_CURVE_ROWS), len(columns),
        figsize=(FULL_WIDTH, 5.4), sharex=True,
        gridspec_kw={"hspace": 0.22, "wspace": 0.28},
    )
    collapsed: List[str] = []
    finals: Dict[str, List[float]] = {}
    for c, (title, pattern, seeds, key) in enumerate(columns):
        # A seed counts as collapsed when its final-10-episode QoE is more than
        # 25% below the arm's best seed -- a threshold, stated, not an eyeball.
        finals[key] = []
        for s in seeds:
            h = _history(pattern.format(s=s))
            finals[key].append(statistics.fmean(
                e["app_reward_mean"] for e in h[-10:]))
        best = max(finals[key])
        for r, (field, ylabel) in enumerate(_CURVE_ROWS):
            ax = axes[r][c]
            for i, s in enumerate(seeds):
                h = _history(pattern.format(s=s))
                y = _smooth([e[field] for e in h], args.smooth)
                bad = finals[key][i] < 0.75 * best
                ax.plot(
                    [e["episode"] for e in h], y,
                    color="#d62728" if bad else SEED_COLOR[i],
                    linewidth=1.5 if bad else 1.0,
                    linestyle="-" if not bad else (0, (4, 1.2)),
                    label=f"seed {s}" + (" (collapsed)" if bad else ""),
                )
                if bad and f"{key}-s{s}" not in collapsed:
                    collapsed.append(f"{key}-s{s}")
            ax.grid(alpha=0.3)
            if c == 0:
                ax.set_ylabel(ylabel)
            if r == 0:
                ax.set_title(title)
            if r == len(_CURVE_ROWS) - 1:
                ax.set_xlabel("Episode")
            # Share the y-range across the three intent columns so the columns
            # are comparable; the attention column keeps its own.
            ax.margins(x=0.02)
    # One legend per column on the top row; give that row extra room underneath
    # so the box does not land on a curve (the collapsed seed dives exactly
    # where a "lower right" legend would otherwise sit).
    for c in range(len(columns)):
        ax = axes[0][c]
        lo, hi = ax.get_ylim()
        ax.set_ylim(lo - 0.45 * (hi - lo), hi)
        ax.legend(fontsize=6.2, loc="lower right", frameon=True, framealpha=0.95,
                  handlelength=1.6, borderpad=0.3, labelspacing=0.25)
    for r in range(len(_CURVE_ROWS)):
        lo = min(axes[r][c].get_ylim()[0] for c in range(len(INTENTS)))
        hi = max(axes[r][c].get_ylim()[1] for c in range(len(INTENTS)))
        for c in range(len(INTENTS)):
            axes[r][c].set_ylim(lo, hi)
    fig.suptitle(
        f"Per-episode training curves ({args.smooth}-episode moving average), "
        "one line per training seed", y=0.995)
    for key, vals in finals.items():
        print(f"{key}: final-10-episode QoE per seed = "
              + ", ".join(f"{v:.3f}" for v in vals)
              + f"  (trainSD {statistics.stdev(vals):.3f})")
    print("collapsed seeds flagged:", collapsed or "none")
    _save(fig, args.out)


# --------------------------------------------------------------------------- #
# p2eval_intent_sweep -- metric vs lambda for both conditioned arms
# --------------------------------------------------------------------------- #

_SWEEP_ROWS = [
    ("bitrate_kbps", "Bitrate (kbit/s)"),
    ("vmaf", "VMAF"),
    ("latency_ms", "Latency (ms)"),
]
ARM_STYLE = {
    "pp": ("per-path", "#d62728", "-", "o"),
    "gl": ("global-only", "#1f77b4", "-", "s"),
}


def cmd_intent_sweep(args) -> None:
    """Learned metric vs lambda for both arms + the mechanical control.

    The shaded flanks are lambda < 0 and lambda > 1: the only genuinely unseen
    points under ``anchor_frac: 0.5`` (the interior region *was* sampled during
    training, so it is in-distribution -- see ``docs/RESULTS.md`` §10.4.5).
    """
    arms = {}
    for tag, path in (("pp", args.pp), ("gl", args.gl)):
        arms[tag] = _load(path)
    meta = arms["pp"]["meta"]
    anchors = (meta["from_anchor"], meta["to_anchor"])

    fig, axes = plt.subplots(len(_SWEEP_ROWS), 1, figsize=(COLUMN_WIDTH + 1.4, 5.8),
                             sharex=True, gridspec_kw={"hspace": 0.14})
    for r, (metric, ylabel) in enumerate(_SWEEP_ROWS):
        ax = axes[r]
        for tag, d in arms.items():
            lam = [p["lambda"] for p in d["points"]]
            y = np.array([p["learned"][metric] for p in d["points"]], dtype=float)
            sd = np.array([p.get("learned_trainSD", {}).get(metric, 0.0)
                           for p in d["points"]], dtype=float)
            label, color, ls, mk = ARM_STYLE[tag]
            ax.fill_between(lam, y - sd, y + sd, color=color, alpha=0.14,
                            linewidth=0)
            ax.plot(lam, y, ls, color=color, marker=mk, markersize=3.2,
                    linewidth=1.3, label=label)
        # Mechanical control (the intent-blind webrtc baseline run through the
        # same rollouts; drawn once -- it is the same policy in both arms).
        lam = [p["lambda"] for p in arms["gl"]["points"]]
        ctl = [p.get("webrtc", {}).get(metric) for p in arms["gl"]["points"]]
        if all(v is not None for v in ctl):
            ax.plot(lam, ctl, color="#7f7f7f", linestyle=(0, (3, 1.5)),
                    linewidth=1.1, marker="^", markersize=2.6,
                    label="webrtc control (intent-blind)")
        ax.set_ylabel(ylabel)
        ax.grid(alpha=0.3)
        lo, hi = min(lam), max(lam)
        if lo < 0:
            ax.axvspan(lo, 0.0, color="#000000", alpha=0.055, linewidth=0)
        if hi > 1:
            ax.axvspan(1.0, hi, color="#000000", alpha=0.055, linewidth=0)
        for a in (0.0, 1.0):
            ax.axvline(a, color="black", linewidth=0.7, linestyle=":")
        ax.set_xlim(lo - 0.03, hi + 0.03)
        if r == 0:
            # Headroom so the legend never lands on the trainSD bands.
            ylo, yhi = ax.get_ylim()
            ax.set_ylim(ylo, yhi + 0.34 * (yhi - ylo))
            ax.legend(loc="upper left", frameon=True, framealpha=0.95, fontsize=7.5)
            for a, name in zip((0.0, 1.0), anchors):
                ax.annotate(f"{name}\n(trained anchor)", (a, 1.02),
                            xycoords=("data", "axes fraction"), ha="center",
                            fontsize=7, linespacing=0.95)
    axes[-1].set_xlabel(
        rf"$\lambda$:  {anchors[0]} $\rightarrow$ {anchors[1]}"
        "\n(shaded flanks = unseen extrapolation; bands = trainSD)")
    fig.suptitle(
        f"Intent interpolation, {meta['training_seeds']} training seeds", y=0.955)
    for tag, d in arms.items():
        for metric, _ in _SWEEP_ROWS:
            c = d["curves"][metric]["learned"]
            print(f"{tag} {metric}: rho={c['spearman_rho']:+.3f} "
                  f"adapt x{c.get('adaptation_margin', float('nan')):.1f} "
                  f"span={c['span']:.4g} "
                  f"max_step={c['max_step_fraction']:.3f}")
    _save(fig, args.out)


# --------------------------------------------------------------------------- #
# p2eval_pathcount -- QoE and decision time vs live path count
# --------------------------------------------------------------------------- #

PC_POLICIES = ["learned", "webrtc", "single", "proportional", "even"]
PC_COLOR = {
    "learned": "#1f77b4", "webrtc": "#8c564b", "single": "#2ca02c",
    "proportional": "#d62728", "even": "#ff7f0e",
}
PC_MARK = {"learned": "o", "webrtc": "s", "single": "^", "proportional": "v",
           "even": "D"}


def _pc_rows(runs: str, mode: str, counts: Sequence[int], report: str):
    """Per-N policy aggregates, plus the in-episode decision-time statistics.

    The decision-time entries come from ``scripts/pathcount_report.py``'s output
    (pooled per-call ``path_decision_ms`` over the nine cells), because
    ``ab_summary.json`` carries neither the raw calls nor a p99.
    """
    rep = {r["num_paths"]: r for r in _load(report).get(mode, [])}
    rows = {}
    for n in counts:
        path = f"{runs}/pc-{mode}-n{n:02d}/ab_summary.json"
        if not os.path.exists(os.path.expanduser(path)) or n not in rep:
            continue
        rows[n] = dict(_load(path)["sets"]["learned"])
        rows[n]["__dec_mean__"] = rep[n]["path_decision_ms"]["mean"]
        rows[n]["__dec_p99__"] = rep[n]["path_decision_ms"]["p99"]
    return rows


def cmd_pathcount(args) -> None:
    """(a) QoE vs N with trainSD bars; (b) decision time vs N against the budget."""
    counts = args.counts
    rows = _pc_rows(args.runs, args.mode, counts, args.report)
    fixed_total = args.mode == "fixed_total"
    # Decision time is a property of the host and the path count, not of the
    # capacity the sweep hands the policy, so panel (b) would be identical in
    # both modes. The contrast sweep therefore renders panel (a) alone.
    bench = _load(args.bench) if fixed_total else None

    if fixed_total:
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(FULL_WIDTH, 3.1),
                                     gridspec_kw={"wspace": 0.26})
    else:
        fig, a1 = plt.subplots(1, 1, figsize=(COLUMN_WIDTH, 3.1))
        a2 = None

    ns = sorted(rows)
    for p in PC_POLICIES:
        if not all(p in rows[n] for n in ns):
            continue
        y = [rows[n][p]["qoe"]["mean"] for n in ns]
        e = [rows[n][p]["qoe"].get("train_std", 0.0) for n in ns]
        a1.errorbar(ns, y, yerr=e, color=PC_COLOR[p], marker=PC_MARK[p],
                    markersize=4 if p != "learned" else 5,
                    linewidth=1.6 if p == "learned" else 1.0,
                    capsize=2.2, elinewidth=0.9, label=disp(p),
                    zorder=3 if p == "learned" else 2)
    a1.set_xscale("log")
    a1.set_xticks(ns)
    a1.set_xticklabels([str(n) for n in ns])
    a1.minorticks_off()
    a1.set_xlabel("Path count $N$ (aggregate capacity held fixed)" if fixed_total
                  else "Path count $N$ (per-path capacity held fixed)")
    a1.set_ylabel("Mean QoE")
    a1.set_title("(a) QoE vs. path count" if fixed_total
                 else "QoE vs. path count, capacity scaling with $N$")
    a1.grid(alpha=0.3)
    # Room under the lowest curve for a 3-column legend, so it never lands on data.
    # Bound the axis by the error bars, not by the means: at N=2 in the
    # fixed-per-path sweep the trainSD is 0.316 and the lower cap fell off the
    # bottom of the old axis, so the bar looked one-sided.
    lo = min(rows[n][p]["qoe"]["mean"] - rows[n][p]["qoe"].get("train_std", 0.0)
             for n in ns for p in PC_POLICIES if p in rows[n])
    hi = max(rows[n][p]["qoe"]["mean"] + rows[n][p]["qoe"].get("train_std", 0.0)
             for n in ns for p in PC_POLICIES if p in rows[n])
    # Reserve less dead space when the legend can sit on the right: in the
    # fixed-per-path sweep the lower-left legend covered the N=2 error bar.
    pad = 0.42 if fixed_total else 0.10
    a1.set_ylim(lo - pad * (hi - lo), hi + 0.06 * (hi - lo))
    a1.legend(fontsize=6.8, loc="lower left" if fixed_total else "lower right",
              ncol=2, handlelength=1.5,
              columnspacing=1.0, borderpad=0.35, framealpha=0.95)

    if a2 is None:
        _save(fig, args.out)
        return

    bn = [r["n"] for r in bench["rows"]]
    fit = bench["fit"]["mean_ms"]
    budget = bench["meta"]["budget_ms"]
    cross = fit["crossover_n"] or max(bn)
    # The fitted line is drawn all the way out to the budget crossing: the panel
    # exists to show the margin, and the margin is three orders of magnitude.
    xs = np.array([min(bn), cross])
    a2.plot(xs, fit["intercept_ms"] + fit["slope_ms_per_path"] * xs,
            color="#1f77b4", linewidth=0.9, linestyle=":", zorder=1,
            label=(f"fit ${fit['intercept_ms']:.3f}+{fit['slope_ms_per_path']:.4f}N$"
                   f", $R^2$={fit['r2']:.3f}"))
    a2.plot(bn, [r["mean_ms"] for r in bench["rows"]], color="#1f77b4",
            marker="o", markersize=4, linewidth=1.4, zorder=3,
            label="micro-benchmark, mean")
    a2.plot(bn, [r["p99_ms"] for r in bench["rows"]], color="#d62728",
            marker="^", markersize=4, linewidth=1.4, linestyle="--", zorder=3,
            label="micro-benchmark, p99")
    # The same statistic measured inside full evaluation episodes, as a check
    # that the isolated benchmark is not measuring something else.
    a2.plot(ns, [rows[n]["__dec_mean__"] for n in ns], color="#1f77b4",
            marker="o", markersize=5, markerfacecolor="none", linestyle="none",
            markeredgewidth=1.1, zorder=4, label="in-episode, mean")
    a2.plot(ns, [rows[n]["__dec_p99__"] for n in ns], color="#d62728",
            marker="^", markersize=5, markerfacecolor="none", linestyle="none",
            markeredgewidth=1.1, zorder=4, label="in-episode, p99")
    a2.axhline(budget, color="black", linewidth=1.0, zorder=2)
    a2.annotate(f"{budget:.1f} ms frame budget (30 fps)",
                (0.015, budget), xycoords=("axes fraction", "data"),
                xytext=(0, 3), textcoords="offset points",
                fontsize=7.5, ha="left")
    a2.annotate(f"fit reaches budget\nat $N\\approx{cross:.0f}$",
                (cross, budget), xytext=(-4, -22), textcoords="offset points",
                fontsize=7, ha="right", color="#1f77b4")
    a2.set_xscale("log")
    a2.set_yscale("log")
    a2.set_xlabel("Path count $N$")
    a2.set_ylabel("Transport-agent decision time (ms, log)")
    a2.set_title("(b) Decision time vs. path count")
    a2.grid(alpha=0.3, which="both")
    a2.legend(fontsize=6.4, loc="upper left", ncol=2, handlelength=1.5,
              borderpad=0.35, labelspacing=0.3, columnspacing=1.0,
              framealpha=0.95)
    a2.set_ylim(top=budget * 6.0)
    _save(fig, args.out)


# --------------------------------------------------------------------------- #
# p2eval_regime_map -- app_only/learned recovery ratio over regime x intent
# --------------------------------------------------------------------------- #

REGIME_ROWS = ["r0_mild", "r1_mildnom", "r2_nominal", "r3_nomharsh", "r4_harsh"]
REGIME_LABEL = {
    "r0_mild": "mild (held-out)", "r1_mildnom": "mild\u2013nominal",
    "r2_nominal": "nominal", "r3_nomharsh": "nominal\u2013harsh",
    "r4_harsh": "harsh (held-out)",
}


def _regime_cells(runs: str):
    """{row: {intent: {...}}} — per-cell QoE plus the per-cell ranking count."""
    out: Dict[str, Dict[str, Dict[str, float]]] = {}
    for row in REGIME_ROWS:
        for intent in INTENTS:
            d_path = f"{runs}/w4-{row}-{intent}"
            summ = os.path.expanduser(f"{d_path}/ab_summary.json")
            if not os.path.exists(summ):
                continue
            arm = _load(summ)["sets"][intent]
            # Per-cell ranking, recounted from the cell JSONs: ab_summary carries a
            # stable/unstable verdict but not the count, and §10's contract asks for
            # the count.
            first = total = 0
            for cell in sorted(glob.glob(os.path.expanduser(f"{d_path}/{intent}/seed-*"))):
                rp = os.path.join(cell, "evaluation_results.json")
                if not os.path.exists(rp):
                    continue
                summary = _load(rp)["summary"]
                total += 1
                if max(summary, key=lambda k: summary[k]["qoe"]["mean"]) == "learned":
                    first += 1
            learned = arm["learned"]["qoe"]["mean"]
            app = arm["app_only"]["qoe"]["mean"]
            out.setdefault(row, {})[intent] = {
                # The scheduler's absolute contribution. A *ratio* (app_only/learned)
                # is the natural cell value only while both QoE means are positive;
                # in the harsh rows `learned` itself drops below the even-split floor
                # and every ratio form blows up (see docs/RESULTS.md §16.1). The gap
                # is defined everywhere and is the quantity the map is about.
                "contribution": learned - app,
                "ratio": app / learned if learned > 0 else float("nan"),
                "learned": learned,
                "learned_sd": arm["learned"]["qoe"].get("train_std", 0.0),
                "app_only": app,
                "app_only_sd": arm["app_only"]["qoe"].get("train_std", 0.0),
                "webrtc": arm["webrtc"]["qoe"]["mean"],
                "even": arm["even"]["qoe"]["mean"],
                "even_loss": arm["even"]["loss"]["mean"],
                "first": first,
                "cells": total,
            }
    return out


def cmd_regime_map(args) -> None:
    """(a) regime x intent heatmap of the scheduler's contribution, (b) the
    interaction on a measured difficulty axis.

    The row coordinate is **measured, not modelled**: the `even` baseline's mean
    loss in that cell, i.e. the direct observation of "does an even split
    overdrive the weakest live path". THESIS_BRIEF §6 suggests a
    residual-capacity formula; that would be an estimate, and this file does not
    report estimates.
    """
    cells = _regime_cells(args.runs)
    rows = [r for r in REGIME_ROWS if r in cells and len(cells[r]) == len(INTENTS)]
    if not rows:
        raise SystemExit("no complete regime rows found -- is the w4 sweep finished?")

    grid = np.array([[cells[r][i]["contribution"] for i in INTENTS] for r in rows])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FULL_WIDTH, 3.5),
                                 gridspec_kw={"wspace": 0.34,
                                              "width_ratios": [1, 1.05]})

    im = a1.imshow(grid, cmap="magma", aspect="auto", vmin=0.0, vmax=grid.max())
    a1.set_xticks(range(len(INTENTS)))
    a1.set_xticklabels(INTENTS, rotation=18, ha="right")
    a1.set_yticks(range(len(rows)))
    a1.set_yticklabels([REGIME_LABEL[r] for r in rows])
    for y, r in enumerate(rows):
        for x, i in enumerate(INTENTS):
            c = cells[r][i]
            broke = c["first"] < c["cells"]
            a1.text(x, y, f"{c['contribution']:.2f}" + ("*" if broke else ""),
                    ha="center", va="center", fontsize=8,
                    color="white" if c["contribution"] < 0.55 * grid.max() else "black")
    a1.set_title("(a) Scheduler contribution\n(learned \u2212 app-only QoE)")
    a1.set_xlabel("Intent (deadline 180 / 400 / 800 ms)")
    a1.set_ylabel("Network regime \u2192 harsher")
    fig.colorbar(im, ax=a1, fraction=0.046, pad=0.04)

    for i in INTENTS:
        xs = [cells[r][i]["even_loss"] for r in rows]
        ys = [cells[r][i]["contribution"] for r in rows]
        a2.plot(xs, ys, linewidth=1.4, color=INTENT_COLOR[i], label=i, zorder=2)
        for r, x, y in zip(rows, xs, ys):
            c = cells[r][i]
            full = c["first"] == c["cells"]
            a2.plot([x], [y], marker="o", markersize=4.6, zorder=3,
                    color=INTENT_COLOR[i],
                    markerfacecolor=INTENT_COLOR[i] if full else "white",
                    markeredgewidth=1.1)
    a2.set_xlabel("Even-split loss fraction (measured difficulty) \u2192")
    a2.set_ylabel("learned \u2212 app-only QoE")
    a2.set_title("(b) The two axes are not separable")
    a2.grid(alpha=0.3)
    a2.legend(title="Intent", fontsize=7.5, title_fontsize=7.5, loc="upper left")
    a2.annotate("hollow marker / *: `learned` no longer\nranks first in every cell",
                (0.98, 0.03), xycoords="axes fraction", ha="right", va="bottom",
                fontsize=6.8, color="#444444")
    _save(fig, args.out)

    print(f"{'row':<18}{'even loss':>10}" + "".join(f"{i:>14}" for i in INTENTS))
    for r in rows:
        el = statistics.fmean(cells[r][i]["even_loss"] for i in INTENTS)
        print(f"{REGIME_LABEL[r]:<18}{el:>10.4f}"
              + "".join(f"{cells[r][i]['contribution']:>14.3f}" for i in INTENTS))
    print("\nper cell: learned [trainSD] | app_only [trainSD] | webrtc | even | "
          "ratio | learned-first")
    for r in rows:
        for i in INTENTS:
            c = cells[r][i]
            print(f"  {r:<12}{i:<13}{c['learned']:+.4f} [{c['learned_sd']:.3f}] | "
                  f"{c['app_only']:+.4f} [{c['app_only_sd']:.3f}] | {c['webrtc']:+.4f} | "
                  f"{c['even']:+.4f} | {c['ratio']:+.3f} | {c['first']}/{c['cells']}")


# --------------------------------------------------------------------------- #
# p2eval_intent_switch -- changing the intent mid-call
# --------------------------------------------------------------------------- #

SWITCH_ARMS = ["conditioned", "specialist", "oracle"]
SWITCH_LABEL = {
    "conditioned": "Conditioned (one policy, intent as input)",
    "specialist": "Specialist for the pre-switch intent",
    "oracle": "Specialist for the post-switch intent",
}
SWITCH_COLOR = {"conditioned": "#1f77b4", "specialist": "#d62728", "oracle": "#7f7f7f"}
SWITCH_STYLE = {"conditioned": "-", "specialist": "-", "oracle": "--"}


def cmd_intent_switch(args) -> None:
    """Two columns (one per direction) x two rows (bitrate, latency vs deadline)."""
    docs = [(_load(p), p) for p in args.runs_json]
    fig, axes = plt.subplots(2, len(docs), figsize=(FULL_WIDTH, 4.2),
                             sharex=True, squeeze=False,
                             gridspec_kw={"hspace": 0.18, "wspace": 0.22})

    for col, (doc, src) in enumerate(docs):
        key = next(iter(doc["directions"]))
        arms = doc["directions"][key]
        fps = doc["meta"]["fps"]
        pre, post = key.split("->")

        a_top, a_bot = axes[0][col], axes[1][col]
        for arm in SWITCH_ARMS:
            if arm not in arms:
                continue
            tr = arms[arm]["mean_trace"]
            # x in seconds relative to the switch, which is what a reader prices.
            xs = [f / fps for f in tr["frame"]]
            kw = dict(color=SWITCH_COLOR[arm], linestyle=SWITCH_STYLE[arm],
                      linewidth=1.3, label=SWITCH_LABEL[arm])
            a_top.plot(xs, tr["bitrate_kbps"], **kw)
            a_bot.plot(xs, tr["latency_ms"], **kw)

        # The deadline is the thing that actually moves at the switch.
        tr0 = arms["conditioned"]["mean_trace"]
        xs = [f / fps for f in tr0["frame"]]
        a_bot.plot(xs, tr0["deadline_ms"], color="black", linewidth=1.0,
                   linestyle=":", label="Frame deadline (the intent)")

        for ax in (a_top, a_bot):
            ax.axvline(0.0, color="black", linewidth=0.9, alpha=0.6)
            ax.grid(alpha=0.3)
        a_top.set_title(f"({chr(97 + col)}) {pre} $\\rightarrow$ {post}"
                        + ("  (deadline relaxes)" if "passive" in post
                           else "  (deadline tightens)"), fontsize=9)
        a_bot.set_xlabel("Time relative to the intent switch (s)")
        if col == 0:
            a_top.set_ylabel("Target bitrate (kbit/s)")
            a_bot.set_ylabel("Delivered latency (ms)")

        # Post-switch QoE goes in the caption, not on the axes: at these y-ranges
        # any in-figure box lands on the traces in one panel or the other.
        for arm in SWITCH_ARMS:
            if arm in arms:
                a = arms[arm]
                print(f"  [{key}] {arm:12s} post-switch QoE {a['post_qoe']:+.4f} "
                      f"[trainSD {a['post_qoe_train_sd']:.3f}]")

    handles, labels = axes[0][0].get_legend_handles_labels()
    h2, l2 = axes[1][0].get_legend_handles_labels()
    for h, l in zip(h2, l2):
        if l not in labels:
            handles.append(h)
            labels.append(l)
    fig.legend(handles, labels, loc="lower center", ncol=2, fontsize=7.2,
               frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.subplots_adjust(bottom=0.22)
    _save(fig, args.out)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--runs", default=os.path.join(_ROOT, "runs"))
    sub = p.add_subparsers(dest="cmd", required=True)

    q = sub.add_parser("qoe-bars")
    q.add_argument("--out", default="~/thesis-report/figures/p2eval_qoe_bars.png")
    q.set_defaults(func=cmd_qoe_bars)

    t = sub.add_parser("training-curves")
    t.add_argument("--smooth", type=int, default=5)
    t.add_argument("--out", default="~/thesis-report/figures/p2app_training_curves.png")
    t.set_defaults(func=cmd_training_curves)

    s = sub.add_parser("intent-sweep")
    s.add_argument("--pp", default="runs/sweep-intent-pp/intent_sweep.json")
    s.add_argument("--gl", default="runs/sweep-intent-gl/intent_sweep.json")
    s.add_argument("--out", default="~/thesis-report/figures/p2eval_intent_sweep.png")
    s.set_defaults(func=cmd_intent_sweep)

    c = sub.add_parser("pathcount")
    c.add_argument("--mode", default="fixed_total",
                   choices=["fixed_total", "fixed_perpath"])
    c.add_argument("--counts", type=int, nargs="+", default=[2, 3, 4, 6, 8, 12])
    c.add_argument("--bench", default="runs/pc-decision-bench.json")
    c.add_argument("--report", default="runs/pc-report.json")
    c.add_argument("--out", default="~/thesis-report/figures/p2eval_pathcount.png")
    c.set_defaults(func=cmd_pathcount)

    g = sub.add_parser("regime-map")
    g.add_argument("--out", default="~/thesis-report/figures/p2eval_regime_map.png")
    g.set_defaults(func=cmd_regime_map)

    w = sub.add_parser("intent-switch")
    w.add_argument("--runs-json", nargs="+",
                   default=["runs/intent-switch-i2p.json",
                            "runs/intent-switch-p2i.json"],
                   help="one intent_switch.py report per direction, in plot order")
    w.add_argument("--out", default="~/thesis-report/figures/p2eval_intent_switch.png")
    w.set_defaults(func=cmd_intent_switch)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
