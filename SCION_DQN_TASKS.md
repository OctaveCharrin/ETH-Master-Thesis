# Task brief for the `scion-dqn-sim` agent

One work item for the thesis (`~/thesis-report`, Chapter 4, submission 2026-08-25). It is cheap —
these agents train in 1–3 minutes each — and it is the highest-value credibility purchase available
anywhere in the document.

## The problem

Chapter 4 reports its conditioning **ablation** over five training seeds with confidence intervals
(`tab:p1eval:seeds`), and that part is solid. Every *other* quantitative result in the chapter is
read from a **single reference training run**:

| Thesis result | Section / float | Producing script |
|---|---|---|
| Intent-alignment matrix $R(\text{told}, \text{scored})$ | `sec:p1eval:intent`, `tab:p1eval:heatmap`, `fig:p1eval:heatmap` | `eval_intent_alignment.py` |
| Per-intent chosen-path metric distributions | `fig:p1eval:boxplots` | `eval_intent_alignment.py` |
| Zero-shot intent interpolation sweep | `sec:p1eval:zeroshot`, `fig:p1eval:zeroshot` | `eval_intent_interpolation.py` |
| Path-count scaling + order invariance | `sec:p1eval:dynamic`, `fig:p1eval:pathcount` | `eval_pathcount_scaling.py` |
| Probing overhead vs. heuristics | `sec:p1eval:overhead`, `tab:p1eval:probing`, `fig:p1eval:probing` | `eval_probing_ceiling.py` |
| Single-path congestion ceiling | `sec:p1eval:ceiling`, `fig:p1eval:ceiling` | `eval_probing_ceiling.py` |

This matters more than it normally would, because **Chapter 5 of the same thesis makes single-run
reporting its central methodological cautionary tale**: four results there were reported from one
training run and did not survive being run three times, and the chapter argues in print that the
spread over *training* seeds exceeds the confidence interval over *evaluation* seeds by an order of
magnitude on this class of problem. An examiner who reads that and then notices Chapter 4's protocol
will ask about it, and "we ran out of time" is not a usable answer when the runs cost minutes.

## What to do

Re-run each of the six results above **across the five training seeds that already exist**, and
report mean with 95% confidence interval over seeds — matching the protocol and presentation of
`tab:p1eval:seeds`, which is the template.

`run_seed_sweep.sh` already builds `<run>/seeds/seed{1..5}/` with per-seed checkpoints, and
`analyze_seed_variance.py` already aggregates the *ablation* across them. The work is to point the
four per-result scripts at each seed's checkpoints and aggregate the same way.

### Four things to check before you start

1. **`run_seed_sweep.sh` is stale relative to the thesis.** It trains FiLM
   (`04_train_conditional_dqn.py`), which the thesis **dropped** on 2026-07-26 — measured as tying
   within seed noise at more parameters. Its header comment still quotes FiLM numbers as the
   load-bearing comparison. The thesis's four rungs are **Flat DQN**, **Scoring DQN (unconditioned)**,
   **Value-Concat**, and **Two-Stream-Concat**. Bring the sweep in line, and do not reintroduce FiLM
   into any reported result.
2. **The sweep may not cover all four rungs.** As written it trains three conditional variants only,
   yet `tab:p1eval:seeds` reports seed intervals for Flat DQN and the unconditioned scoring agent
   too. Find out where those came from. If they are not in `seeds/`, extend the sweep so all four
   rungs are seeded identically — the ladder's value is that it isolates one change at a time, and
   that only holds if every rung gets the same treatment.
3. **Hold the environment fixed across seeds.** The existing protocol reseeds only torch/numpy/random
   while the environment's pair, hour and profile streams stay fixed, so every seed sees an identical
   stream of training contexts and only the learning process varies. Preserve that and state it.
4. **Evaluate on the identical contexts.** All five seeds must be graded on the same 10752 held-out
   decision contexts (32 pairs × 336 hours, last 14 days) the chapter already uses, so the numbers
   are comparable to the ones in the draft.

### What to report

For each of the six results, the aggregate over five seeds **and** whether the claim the thesis
currently makes from it survives. Be specific about survival, because several of these claims are
quantitatively sharp:

- Does the intent-alignment diagonal still win **all four columns**? The Low-Loss column spans only
  0.011 in the reference run, so this is the one most likely to move.
- Is the zero-shot Spearman still $\rho = -1.000$, and does the "no single step carries more than
  24.7% of the span" claim hold per seed? Report the per-seed range for both.
- Is order invariance still **exactly** 100.0000% across all 32256 permutation trials per agent?
  An exactness claim must hold for every seed or be restated.
- Does the learned selector still beat every heuristic on three of four intents, and stay within
  0.0015 of lowest-latency on the fourth?
- Does the ceiling still descend by ~24% (9.1 → 6.9 Gbit/s) from light to heavy congestion, with
  reward staying flat (0.898 → 0.889)?

**Report reversals loudly.** The thesis has an established, in-print practice of reporting
retractions as results rather than quietly correcting them — Chapter 5 §5.4.9 is built on it. If a
claim does not survive five seeds, that is a wanted finding, not a failure. Say which claim, by how
much, and against what spread.

### Figures

Regenerate the five affected figures with seed spread shown — error bars or per-seed traces —
rather than as single-run curves. Keep the existing filenames so the thesis picks them up
unchanged:

`p1eval_intent_heatmap.png`, `p1eval_intent_boxplots.png`, `p1eval_zeroshot.png`,
`p1eval_pathcount.png`, `p1eval_probing.png`, `p1eval_ceiling.png` → `~/thesis-report/figures/`.

For the heatmap, note the thesis caption already flags that column-relative coloring hides very
different column ranges; if seed spread makes any column's diagonal non-significant, that must be
visible in the figure and not only in the text.

## Second, smaller item

While you are in the ablation data: `tab:p1eval:ablation` reports parameter counts (Flat DQN
85.3k, Scoring DQN 36.2k, Value-Concat 36.9k, Two-Stream-Concat 37.5k). **Confirm these are current
and correct.** The thesis is about to make a deployability point from them — that the better
architecture is also less than half the size of the one it replaces — and that sentence should not
rest on a stale number.

## Out of scope

Chapter 5's work (multipath, NS-3, intent conditioning over continuous allocations) lives in
`~/rl-mpquic` and is briefed separately in `~/thesis-report/RL_MPQUIC_TASKS.md`. Nothing here
touches it.
