# THESIS_MEMORY.md — Master's Thesis Context & Narrative Strategy

> **User / Author:** Octave Charrin (`ocharrin@ethz.ch`)  
> **Institution:** Network Security Group, Department of Computer Science, ETH Zurich  
> **Supervisors:** Prof. Dr. Adrian Perrig, Liwen Xu  
> **Title:** *Intent-Conditioned Reinforcement Learning for Path Selection and Multipath Optimization in SCION*  
> **Submission Date:** August 25, 2026  
> **Role of AI Assistant:** Technical co-writer, LaTeX editor, and narrative reviewer.

---

## 1. Executive Summary & Core Narrative Arc

### The Thesis Core Question
*How should an endpoint choose the best path—or combination of paths—given both the application's intent and the current state of the network?*

### The Central Thesis Statement
On a path-aware Internet (SCION), application intent should not be a static, hand-tuned parameter compiled into network algorithms. Instead, **intent must be a first-class, modulative input** that dynamically reshapes control mechanisms from path selection down to media bitrates.

### Key Narrative Progression
Rather than splitting the work into disconnected parts, the thesis follows a **unified, linear story of intent-driven control across two operational granularities**:

1. **Chapter 3 (Motivating Study — Discrete Single-Path Selection):** Investigates how intent modulates **WHICH** path is chosen for general flows. It introduces permutation-equivariant path scoring and proves that feature-wise linear modulation (FiLM) is mathematically required over naive concatenation. It closes by identifying the *single-path performance ceiling*: when congestion surges or paths churn, choosing even the "optimal" single path fails.
2. **Chapter 4 (Joint Application-Network Multipath Co-Optimization):** Directly addresses the single-path ceiling by expanding control along two continuous axes. Using SCION’s path multiplicity and Multipath QUIC, it co-optimizes **HOW MUCH** traffic is sent on each path (continuous traffic split) and **WHAT** the application produces (video encoding bitrate) using a two-timescale hierarchical SAC agent pair.
3. **Chapter 5 & Beyond (Synthesis & Analysis):** Unifies the findings, proving that FiLM modulation enables zero-shot intent adaptation and that learned multipath scheduling yields maximum value under **network volatility and churn**.

---

## 2. Updated Linear Table of Contents Structure

The thesis has been refactored from a rigid "Part I / Part II" structure into a single, cohesive linear flow[cite: 2]:

- **Abstract & Acknowledgements**[cite: 1, 2]
- **1. Introduction**[cite: 1, 2]
  - 1.1 Motivation & Problem Statement[cite: 1, 2]
  - 1.2 Thesis Contributions[cite: 1, 2]
  - 1.3 Organization[cite: 1, 2]
- **2. Background & Technical Foundations**[cite: 1, 2]
  - 2.1 The SCION Path-Aware Architecture[cite: 1, 2]
  - 2.2 Quality of Experience & Transport Mechanisms (MPQUIC, ABR)[cite: 1, 2]
  - 2.3 Deep RL Machinery (DQN, Dueling, SAC, Permutation Equivariance)[cite: 1, 2]
  - 2.4 Goal-Conditioned Reinforcement Learning & FiLM Modulation
- **3. Problem Statement & Desired Properties**
  - 3.1 Problem Formulation (Single-Path Discrete vs. Multipath Continuous)
  - 3.2 Desired System Properties
  - 3.3 Operating Assumptions & Scope
- **4. Motivating Study: Intent-Conditioned Single-Path Selection**
  - 4.1 Single-Path Selection Framework & State/Action Formulation
  - 4.2 Intent Conditioning via Feature-Wise Linear Modulation (FiLM)
  - 4.3 Implementation & SCION Simulation Environment
  - 4.4 Experimental Evaluation & Intent Alignment
  - 4.5 The Single-Path Performance Ceiling (Bridging to Chapter 5)
- **5. Joint Application-Network Optimization over Multipath**
  - 5.1 System Design: Co-Optimizing Rate and Traffic Splitting
  - 5.2 Two-Timescale Hierarchical Agents (App Agent + Transport Agent)
  - 5.3 Testbed & Backends (NS-3 Packet Simulator vs. Fast Mock Backend)
  - 5.4 Experimental Evaluation & Regimes of Value (Volatility Analysis)
- **6. Discussion & System Synthesis**[cite: 1, 2]
  - 6.1 Synthesis of Findings (Modulative Ingestion & Volatility Drivers)
  - 6.2 System Analysis (Overhead, Scalability, Generalization)
  - 6.3 Deployment Considerations & Trust Assumptions
- **7. Related Work**[cite: 1, 2]
- **8. Conclusion & Future Work**[cite: 1, 2]
- **Bibliography & Appendices**[cite: 1, 2]

---

## 3. Core Contributions & Key Technical Insights

### Contribution 1: FiLM Modulation vs. Concatenation (Chapter 4)
* **The Insight:** In comparison-based action selection (e.g., `argmax` over per-path $Q$-values), simply appending an intent vector $w$ to global state inputs fails. Additive, symmetric signals shift all path scores equally and cancel out during comparison.
* **The Solution:** Feature-wise Linear Modulation (FiLM) applies affine transformations $\tilde{f}_i = (1+\gamma)\odot f_i + \beta$ to path-specific features. Multiplicative modulation changes the relative weight of path attributes (e.g., amplifying latency vs. goodput), allowing a single model to re-rank paths dynamically.

### Contribution 2: Permutation-Equivariant Scoring Head (Chapters 4 & 5)
* **The Insight:** Fixed-action heads (standard DQN) cannot handle dynamic source-destination pairs where path count $N$ changes over time.
* **The Solution:** A shared scoring network evaluates each `(global_context, path_i)` pair independently. Masking invalid/absent paths ensures invariance to path ordering and scalability across variable topologies without retraining.

### Contribution 3: Two-Timescale Hierarchical Co-Optimization (Chapter 5)
* **The Architecture:**
  * **Application Agent (Slow, 1s cadence):** Horizon-agnostic SAC agent adapting target video bitrate ($300–6000\text{ kbit/s}$) to maximize overall QoE.
  * **Transport Agent (Fast, ~33ms frame cadence):** Continuous SAC agent outputting a continuous traffic split $(w_1, \dots, w_N)$ via softmax across active paths.
* **The Coupling:** The transport agent observes the application's target bitrate. The application agent is rewarded for full QoE (VMAF, latency, jitter, loss), while the transport agent is rewarded for frame delivery efficiency.

### Contribution 4: Regimes of Value / Volatility Finding (Chapter 5)
* **The Key Empirical Result:** In static, stable networks, learned multipath scheduling adds minimal value over a simple application-only rate adaptation.
* **The Turning Point:** Under high network volatility, path churn, and bursty congestion, application-only control collapses. Joint rate and multipath traffic splitting is *decisive* for sustaining real-time media QoE.

---

## 4. Evaluation Requirements & Benchmark Matrix

When writing or reviewing evaluation chapters, the AI agent should ensure the following experiments and data points are highlighted:

### Single-Path Selection Experiments
1. **Ablation Table (Table 4.1):** Comparing `Flat DQN`, `Conditional-Concat`, and `Conditional-FiLM` across 5 reward profiles (`Balanced`, `Throughput`, `Latency`, `Trust`, `Low Probe`). Demonstrating near-zero behavioral shift in `Concat` vs. strong shift in `FiLM`.
2. **Intent Alignment Matrix (Figure 4.1):** Heatmap showing $R(intent_{eval}, intent_{profile})$ with dominant diagonal entries.
3. **Single-Path Performance Ceiling (Figure 4.3):** Goodput/QoE curve under increasing link utilization showing single-path degradation under congestion.

### Multipath Co-Optimization Experiments
1. **QoE Comparison Table (Table 5.1):** Mean QoE for `Learned Pair` vs. `App-Only`, `Single-Best Path`, `Proportional`, and `Even Split` across Static (4-path) and Dynamic (6-path) scenarios.
2. **Dynamics Trace:** Within-episode timeseries proving the transport agent reallocates traffic away from churning/bursting paths.

---

## 5. Writing Style & Formatting Guidelines for AI Assistant

When redacting or editing text for this thesis, adhere strictly to the following formatting and stylistic rules:

1. **Tone:** Authentic, rigorous, scholarly, yet direct and readable. Tone should reflect an ETH Zurich Master's graduate in computer science.
2. **LaTeX Usage Rules:**
   * **Only** use LaTeX for formal math/science equations, variables, or set notations (e.g., $Q(s,a)$, $\pi(a|s,g)$, or display equations).
   * **Never** use LaTeX for standard text formatting, regular prose, simple numbers, or simple units (e.g., write **100 ms**, **30 fps**, **20%**, **300–6000 kbit/s** in plain text/Markdown bold).
   * Use inline `$math$` and display block `$$math$$` notation appropriately.
3. **Terminology Consistency:**
   * Use **SCION**, **ISD**, **PCB**, **hop field**, **up/core/down segment**.
   * Use **FiLM (Feature-wise Linear Modulation)**.
   * Use **Multipath QUIC (MPQUIC)**.
   * Use **QoE (Quality of Experience)** and **VMAF**.
4. **Transition Style:** Maintain strong narrative bridge sentences between sections. Always highlight *why* a technical choice was made (e.g., why FiLM was picked over concatenation, why two timescales were chosen instead of one monolithic agent).