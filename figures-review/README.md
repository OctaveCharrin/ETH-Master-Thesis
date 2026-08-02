# Redrawn figures, for review

Every PNG here is a proposed replacement for the file of the same name in
`figures/`. Nothing in `figures/` has been touched and no `\includegraphics`
path in `sections/` has been changed, so the thesis still builds against the old
figures. To adopt one, copy it over its namesake.

The data behind every figure is unchanged — same runs, same aggregates, same
numbers. Only layout, labelling, and (in two cases noted below) which
aggregation is plotted have changed.

Regeneration scripts are in `scripts/`; each documents its own deltas at the
top. They run against the sibling projects' venv:

```
# Chapter 4 (reads scion-dqn-sim aggregate CSVs)
~/rl-mpquic/.venv/bin/python scripts/regen_ch4_figures.py \
    ~/scion-dqn-sim/evaluation/run_20260722_180329/seeds/aggregate .

# Chapter 5, the two figures from an evaluation run directory
~/rl-mpquic/.venv/bin/python scripts/regen_ch5_eval_figures.py \
    ~/rl-mpquic/runs/ab-prof2-evinteractive-trinteractive/interactive/seed-1000-t1 .

# Chapter 5, the cross-run aggregates
cd ~/rl-mpquic && .venv/bin/python <path>/scripts/regen_ch5_thesis_figures.py \
    qoe-bars --out <path>/p2eval_qoe_bars.png
# also: pathcount [--mode fixed_perpath], intent-sweep --pp runs/sweep6-intent-pp/... --gl ...
```

---

## Figures with a data-visibility bug (these are the ones that matter)

### `p2eval_pathcount_perpath.png` — an error bar was clipped off the axis
The N = 2 point carries a training-seed spread of **0.316**, which the text
quotes as the headline of the whole contrast sweep ("twenty-four times its
nominal 0.013"). The published figure sets its y-limits from the *means*, so the
lower cap at −0.799 fell below the axis and the bar rendered one-sided at about
half its true length — the figure understated exactly the quantity the paragraph
is about. The axis is now bounded by mean ± trainSD.

### `p2eval_pathcount.png` panel (b) — the dotted "fit" is not the fit
`t(N) = a + bN` is a straight line in linear coordinates; this panel is log–log.
The line was drawn from its two endpoints, `(2, 0.493)` and `(6554, 33.3)`,
which on log–log axes renders a **power law through those endpoints**, not the
fitted line. At `N = 96` the drawn line reads 3.70 ms where the fit and the
measurement both read 0.96 — a factor of 3.9. That is why the fit appears to
miss every point it was fitted to. Sampling it on a dense grid puts it back on
the data. The fit itself is fine: `R² = 0.990`, every point within 5 %.

The same two-point call is in `rl-mpquic/scripts/thesis_figures.py`, so the
published figure has the bug at source.

Keep the linear fit — there is a reason for it beyond curve-fitting. The
transport agent scores each path with one shared encoder evaluated `N` times, so
the cost model the architecture *implies* is a fixed part (observation build,
softmax, Python overhead) plus a per-path part: exactly `a + bN`. The fit
measures `a` and `b` rather than choosing a functional form, and the point of
the paragraph — that `a` dominates `bN` over the whole useful range — is a
statement about those two coefficients. A power law or a log fit would have no
such reading.

The legend was also too wide for the panel, because the fit's label was twice
the width of any other entry. The fit is now annotated on the curve and the
legend holds the four measurement series.

### `p1eval_probing.png` — five methods were plotted on top of each other
Shortest-path, lowest-latency, ECMP, the SCION default, and random all cost
exactly 360 ms per selection, so on the old linear x-axis their markers and
labels collapsed into one unreadable cluster while 90 % of the panel was empty.
Now: log x-axis, and each point carries its value on a leader line, with the
legend back at bottom right (as in the published figure) carrying the names.
Also relabelled — see "units and names" below.

**This one needs a `.tex` change too:** the figure is currently included at
`width=0.72\linewidth`, which shrinks the point labels below legibility. Change
it to `width=\linewidth` in `sections/4_single_path.tex`.

### `p2eval_decision_time.png` — legend on a bar, labels on each other
The legend sat on top of the App-only bitrate bar, and the value labels
`0.0148` and `0.0126` overlapped. The legend is now above the axes and the
labels are set vertically. Tick labels are shortened, because at `\linewidth`
the nine full policy names collided into an illegible pile (visible on p. 73 of
the current PDF).

Note the numbers this figure prints: **0.575** for the learned split and
**0.577** for path-only. The text used to say 0.507 ms, which is not a number
any run on disk carries; it now quotes **0.536 ms**, the same statistic pooled
over the nine cells at six paths (`runs/pc-report.json`), which is the pool the
0.713 ms p99 in the same paragraph already came from.

### `p2eval_path_mechanism.png` — legend over the data
The six-path legend sat inside panel (a) and covered path 0's goodput trace over
t ≈ 20–27 s, which is one of the intervals the caption asks the reader to look
at. It is now a shared legend below the panels.

### `p1eval_ceiling.png` — legend over the data
The seven-method legend sat inside the left panel and covered the Random curve
over the middle of the congestion range. It is now shared, below both panels.

### `p2design_arch.tex` / `p2design_arch-1.png` — Figure 5.1 collides with itself
Four collisions, all worse for the `\resizebox`: the "per-path state" label sat
on the Transport agent box and ran off the right edge; "path N (live/dead)" was
wider than its box; "target bitrate" sat on its arrow; and the two reward return
paths shared a lane. The delivery-reward lane now returns over the top of the
path column — its first redraw still rose at `x = 8.15`, which grazed the scorer
box and cut across all three fan-out arrows. The `.tex` here is a standalone preview — to adopt it,
replace the `tikzpicture` inside the `figure` environment in
`sections/5_multipath.tex` and keep the existing `\caption`/`\label`.

---

## Figures changed for consistency only

### `p1eval_intent_boxplots.png` — **changes which run is plotted**
This is the one substantive change. The published figure is the *single-run*
rendering; every other Chapter 4 figure was regenerated at five seeds on
2026-07-31 and this one was not (`figures/` mtimes show it). The version here is
the five-seed rendering the pipeline already produces, plus a CI on the
loss-exposure bars and staggered labels (the three `0.48%` labels touched).

Adopting it changes three numbers in the surrounding prose — see the `\gap` at
the seed-protocol paragraph in `sections/4_single_path.tex`. If you would rather
keep the single-run figure, that `\gap` says what to add to the exception list
instead.

### `p2eval_qoe_bars.png`, `p2eval_pathcount.png`, `p2eval_pathcount_perpath.png`, `p2eval_decision_time.png`, `p2eval_path_mechanism.png` — policy names
The figures said "Hierarchical RL (ours)", "Path agent only", "App agent only",
"Single best", "Random"; Tables 5.1–5.6 say "Learned pair", "Path-only (GCC
rate)", "App-only", "Single best-active path", "Random split". A reader
comparing Figure 5.2 against Table 5.1 had to translate. The figures now use the
table names. (`p2eval_decision_time.png` uses short forms on the tick axis for
space; the mapping is unambiguous.)

### Units
`Mbps` → `Mbit/s` and `kbps` → `kbit/s`, to match the `siunitx` output in the
running text.

### `p1eval_*` y-axis label
"Achieved goodput (Mbps)" → "Residual bottleneck capacity (Mbit/s)".
§4.1.2 spends a paragraph insisting that this quantity is residual bottleneck
capacity and "no number in this chapter should be compared against" a
throughput, and then the axes say "achieved goodput" and the captions spend a
sentence each undoing it. Saying it on the axis lets those caption sentences go:
in `fig:p1eval:probing` ("The axis is labelled 'achieved goodput' but
measures residual bottleneck capacity…") and in `fig:p1eval:ceiling` ("As
throughout the chapter, the left axis is residual bottleneck capacity…").

---

## Not changed

`p1eval_intent_heatmap.png`, `p1eval_zeroshot.png`, `p1eval_pathcount.png`,
`p2eval_regime_map.png`, `p2eval_intent_switch.png`, `p1app_training_curves.png`,
`p2app_training_curves.png` — no overlap, legends clear of data, numbers legible
at print size. Two cosmetic notes if you are touching them anyway:

* `p2eval_regime_map.png` panel (b) prints `` `learned` `` with literal
  backticks in its annotation.
* `p2eval_intent_switch.png` uses red for "specialist" and blue for
  "conditioned", while `p2eval_intent_sweep.png` two pages earlier uses red for
  "per-path" and blue for "global-only". Same colours, different meanings, same
  subsection.
