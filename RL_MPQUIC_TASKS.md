# Task brief for the `rl-mpquic` agent

Three work items for the thesis (`~/thesis-report`, submission 2026-08-25), in priority order.
Item A is new and is the highest-value item. Items B and C are already specified in
`docs/THESIS_BRIEF.md` §9 and `docs/RESULTS.md` §10.5 respectively.

Read `docs/RESULTS.md` §8 (evidence status) and §10 (reporting contract) before starting. The
reporting rules there apply to everything below: **every number cites the artifact it came from,
`trainSD` accompanies every margin, ranking stability is reported per cell and not only on the
mean, and negative results are wanted.** Append your findings to `RESULTS.md` in its existing
style, as new numbered sections.

Figures go to `~/thesis-report/figures/` as PNG, named `p2eval_*.png` / `p2app_*.png` to match
Chapter 4's `p1eval_*` convention. Render at print resolution.

---

## A. Path-count scaling — QoE and decision time vs. live path count

**Why this matters.** The permutation-equivariant path head exists so that one policy serves any
number of paths, with parameter count independent of $N$ and inference linear in $N$. Chapter 5
currently asserts that property **by construction and never measures it**, while Chapter 4 measures
its own version (`fig:p1eval:pathcount`, regret vs. candidate-set size). This is the most visible
evidence asymmetry between the two chapters. The thesis also currently claims the transport agent's
0.507 ms decision cost leaves room for "roughly 200 paths before the frame budget binds", which is
arithmetic, not a measurement — this item is what makes it one, or corrects it.

**No training.** Evaluation only, against checkpoints already on disk.

### A.1 The design trap — read this before building configs

`configs/dynamic.yaml` has a fixed six-entry `topology.paths` list. The obvious sweep — truncate
to 2, extend to 12 — **confounds path count with total capacity**, so QoE would rise with $N$ for
the trivial reason that there is more aggregate bandwidth, and the figure would measure nothing.

Hold **aggregate capacity approximately constant** across the sweep so that $N$ varies the
*granularity* of the allocation decision and not the *amount* of resource. The six-path config
totals 15.5 Mbit/s; construct each $N$ to total the same, preserving the scenario's character
(a low-RTT clean path, a high-latency trap, a congested path, a shared-bottleneck pair where
$N$ allows). Keep `cross_frac` values in the same range. State in the write-up exactly how you
built each config and that aggregate capacity is held fixed — a reader must be able to see the
confound was controlled.

Two further consistency points:
- `dynamics.min_active: 3` is invalid for $N < 3$. Scale it with $N$ (e.g. $\max(1, \lceil N/2 \rceil)$)
  and say so.
- `dynamics.corr_groups: [[4,5]]` indexes paths that do not exist for small $N$. Drop or remap it,
  and note which $N$ have a shared-bottleneck group and which do not, since that changes the
  scenario's difficulty independently of $N$.

If holding capacity constant turns out to distort the scenario badly at the extremes, **say so and
report both sweeps** (fixed-total and fixed-per-path). That is a more useful result than one clean
curve, and the asymmetry between them is itself informative.

### A.2 What to measure

Sweep $N \in \{2, 3, 4, 6, 8, 12\}$ (6 is the nominal config, the anchor point).

For each $N$, over **at least 3 training seeds** (`runs/dyn-s1..s3`, or all six if cheap) × 3
evaluation seeds:

1. **Mean QoE** of the learned pair, with `trainSD`, plus the fixed-rule baselines (`even`,
   `single`, `proportional`, `webrtc`) so the comparison is a ranking and not an absolute.
   Report whether the learned pair still ranks first per cell at each $N$.
2. **Decision time** of the transport agent — mean and **99th percentile** — already recorded per
   call in every `evaluation_results.json` with warm-up discarded. The p99 is the number a
   real-time claim actually rests on and the thesis currently quotes only the mean.
3. Whether the checkpoint **loads and runs at all** at each $N$ without retraining or padding.
   This is the architectural claim; a clean pass is the result.

**Contrast arm, if cheap:** the flat-head checkpoints (`runs/flat-s*`) cannot accept a path count
they were not trained on. Confirming they fail — or must be padded — at $N \neq 6$ is the direct
counterpart of Chapter 4's flat-agent result and strengthens §12 of `RESULTS.md`.

### A.3 Extending the decision-time axis further

Decision time does not need full episodes. If a micro-benchmark is easy — load a `path.pth`, build
synthetic observations at $N \in \{6, 12, 24, 48, 96\}$, time the forward pass with warm-up
discarded — run it and report the fit. That is what settles whether the linear-scaling
extrapolation holds and at what $N$ the 33 ms frame budget actually binds. Report the measured
crossover, or state that it was not reached.

### A.4 The figure

`~/thesis-report/figures/p2eval_pathcount.png`, two panels sharing the $N$ axis (log scale):

- **(a)** Mean QoE vs. $N$, learned pair plus baselines, error bars = `trainSD`.
- **(b)** Transport-agent decision time vs. $N$, mean and p99, with a horizontal line at the
  33 ms frame budget and the axis extended far enough to show the margin.

Report back the numbers in text as well as the figure — the thesis quotes numbers inline and needs
them independently of the plot.

---

## B. The remaining Chapter 5 figures

Two are already done and in the thesis (`p2eval_path_mechanism.png` from `figure10_path_metrics`,
`p2eval_decision_time.png` from `figure4_decision_time`, both from
`runs/ab-prof2-evinteractive-trinteractive/interactive/seed-1000-t1`). These remain, in priority
order:

| Target file | Content | Source |
|---|---|---|
| `p2eval_qoe_bars.png` | Grouped bar or slope chart of mean QoE by policy × intent, error bars = `trainSD` | The three `runs/ab-prof2-ev*-tr*/ab_summary.json` **three-seed aggregates** — *not* `figure1_qoe` of a single cell, which would understate the evidence behind the table it replaces. Needs a small new plotting script. |
| `p2eval_intent_sweep.png` | Bitrate / VMAF / latency vs. $\lambda$ for both conditioned arms, anchors marked, extrapolation flanks shaded | `scripts/intent_sweep.py` over `runs/ab-intent6-{pp,gl}-*`. Counterpart to Chapter 4's `fig:p1eval:zeroshot`. |
| `p2app_training_curves.png` | Per-episode QoE / loss / VMAF per intent, **including the collapsed attention-pool seed** | `history` array in every `runs/*/stats.json`. Appendix figure. The collapsed seed is the point: a training curve is the most direct evidence that a `trainSD` is a collapse rather than noise. |
| `p2eval_regime_map.png` | 2-D map: headroom heterogeneity (rows) × intent (columns), cell value = app-only recovery ratio | Lowest priority, and the only one needing new evaluation runs. Nine reference points exist in `docs/TUNING_DYNAMICS.md` §4 to seed the grid; held-out configs are `configs/dynamic_ood_{harsh,mild}.yaml`. Specified as W4 in `docs/THESIS_BRIEF.md` §6. **Skip if time is short** — say so rather than shipping a thin version. |

Fix the label collision in `figure4_decision_time` while you are in the plotting code: panel (b)'s
y-axis label overlaps panel (a)'s tick labels. Regenerate `p2eval_decision_time.png` after fixing.

---

## C. The `obs_norm: fixed` conditioning arm

**Schedule: wait for the NS-3-native training arm (D5) to finish before launching.** As of
2026-07-30 `runs/ns3train-s2` is running (seed 2 of the D5 arm, ~4 h/seed, strictly sequential,
load ~16.5 on a 16-core box). Mock and NS-3 do not collide on the shared-memory segment, but they
compete for CPU, and launching now would both slow D5 and invalidate the ~4 h/seed NS-3 training
cost the thesis quotes. Poll for completion, then launch.

**What it answers.** Chapter 5 reports per-path intent conditioning losing to global-only
conditioning on *every* axis measured — QoE at two of three intents, behavioral divergence,
interpolation smoothness — and offers **no explanation**. The prime suspect is documented: breaker 3
of `RESULTS.md` §10.2, the observation normalizer that carries the intent into the per-path rows
under Variant A. Under `perpath` the intent reaches each path row twice (once broadcast, once as a
$4\times$ rescaling of that row's sRTT column), and the network must reconcile two correlated
channels. `intent.obs_norm: fixed` closes that channel exactly (row span 0.000, row G of §10.2).

**Run:** 3 seeds, `configs/dynamic_intent.yaml` with `intent.obs_norm: fixed`, matched to the
existing arms' budget. Then `scripts/ab_eval.py` against the existing `runs/ab-intent6-pp-*` arm on
the same cells, and `scripts/intent_probe.py` for divergence.

**Both outcomes are publishable and the thesis wants whichever is true:**
- *Shortfall closes* → the leak is the mechanism, the chapter gains an explanation for its own
  negative result, and per-path conditioning is vindicated as a design principle rather than
  defended only on guarantees.
- *Shortfall persists* → the leak is **not** the explanation, and the cost is attributable to the
  30 extra input dimensions. That is a cleaner statement than the current silence.

Report which, with `trainSD` and per-cell ranking, and flag it against `RESULTS.md` §10.5, which
currently lists this as unmeasured.

---

## Not in scope for this repo

The Chapter 4 re-run (intent-alignment matrix, zero-shot sweep, path-count study, probing
comparison, ceiling figure at 5 training seeds) belongs to the **single-path SCION codebase**,
which is not in this repository and not on this machine. Do not attempt it here.
