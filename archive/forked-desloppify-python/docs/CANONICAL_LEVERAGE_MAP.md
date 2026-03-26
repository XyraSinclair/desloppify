# Canonical Leverage Map

This document captures the highest-leverage places in `desloppify` to make outcomes more canonical, more reproducible, and more aligned with deep codebase transformation.

## Goal

Upgrade Desloppify from "good prompt+merge heuristics" to a calibrated judgment system with:

- stronger evaluator abstraction,
- better axis quality,
- reproducible scoring semantics,
- and measurable alignment between score movement and real codebase quality.

## P0 Leverage Surfaces (highest ROI)

### 1) Review runner abstraction (decouple judgment engine from Codex/Claude wiring)

Why this is high leverage:
- Current batch execution is tightly bound to `codex` for local runs and `claude` for external flow.
- This is the single best insertion point for `cardinal-harness`.

Primary files:
- `desloppify/app/commands/review/batches.py`
- `desloppify/app/commands/review/batch.py`
- `desloppify/app/commands/review/runner_helpers.py`
- `desloppify/app/commands/review/external.py`
- `desloppify/app/cli_support/parser_groups_admin.py`

Canonical upgrade:
- Introduce a `ReviewJudgeBackend` interface:
  - `prepare(packet, batch, run_context) -> backend_payload`
  - `execute(backend_payload) -> raw_result`
  - `normalize(raw_result) -> canonical_batch_result`
  - `provenance() -> canonical provenance block`
- Implement backends:
  - `codex`
  - `claude`
  - `cardinal` (for multi-judge/cross-axis adjudication)
- Keep CLI stable, but route all runs through backend registry.

### 2) Axis contract and metadata unification (single source of truth for "taste")

Why this is high leverage:
- Subjective quality lives or dies by axis definitions.
- Today, weights and display naming are partially duplicated with legacy fallback behavior.

Primary files:
- `desloppify/languages/_framework/review_data/dimensions.json`
- `desloppify/intelligence/review/dimensions/data.py`
- `desloppify/intelligence/review/dimensions/metadata.py`
- `desloppify/engine/_scoring/policy/core.py`
- `desloppify/engine/_scoring/subjective/core.py`

Canonical upgrade:
- Make `dimensions.json` authoritative for:
  - display names,
  - weights,
  - reset behavior,
  - calibration anchors.
- Remove hardcoded subjective weight fallback maps once schema carries full metadata.
- Version the dimension schema and persist `dimension_schema_version` in state.

### 3) Scoring semantics (replace heuristic constants with calibrated policy)

Why this is high leverage:
- Scoring determines optimizer behavior for every agent loop.
- Constants are currently strong but hand-tuned and brittle across repos/languages.

Primary files:
- `desloppify/engine/_scoring/policy/core.py`
- `desloppify/app/commands/review/batch_scoring.py`
- `desloppify/engine/_state/scoring.py`

Canonical upgrade:
- Move merge/scoring constants to explicit policy config with profile support.
- Add confidence intervals to subjective dimension scores.
- Penalize uncertainty/disagreement directly (not only issue count).
- Replace target-match reset heuristic with reliability-aware anti-gaming checks:
  - repeated anchoring patterns,
  - low evidence density,
  - high score + weak rationale.

### 4) Evidence quality enforcement (reduce hallucinated or weak findings)

Why this is high leverage:
- Better judgments require hard evidence contracts.
- Stronger evidence checks improve trust and reduce noisy churn.

Primary files:
- `desloppify/app/commands/review/batch_core.py`
- `desloppify/intelligence/review/importing/contracts.py`
- `desloppify/intelligence/review/feedback_contract.py`

Canonical upgrade:
- Require evidence references to map to existing files/line spans when possible.
- Add a quality score per finding (specificity, verifiability, actionability).
- Add merge-time dedupe by semantic fingerprint + evidence overlap, not summary text only.

## P1 Leverage Surfaces

### 5) Holistic context and batch design

Why this is high leverage:
- Context quality strongly controls judge performance.
- Current batch slicing is already good and should become more metric-driven.

Primary files:
- `desloppify/intelligence/review/context_holistic/orchestrator.py`
- `desloppify/intelligence/review/prepare.py`
- `desloppify/intelligence/review/prepare_batches.py`

Canonical upgrade:
- Add explicit context budget accounting (token estimates per batch).
- Rank context features by predictive value (which signals produce accepted findings).
- Auto-adapt batch composition to low-confidence dimensions.

### 6) Work queue optimization objective

Why this is high leverage:
- `next` is the behavior shaper for agents doing actual code changes.

Primary files:
- `desloppify/engine/_work_queue/core.py`
- `desloppify/app/commands/next.py`
- `desloppify/engine/planning/scorecard_projection.py`

Canonical upgrade:
- Prioritize by expected strict-score lift per unit effort (not just current severity/tier).
- Add "strategic fixes" mode for root-cause changes that collapse many findings.
- Reduce dimension-display alias logic in queue plumbing by storing canonical dimension keys everywhere.

### 7) Scan command side effects

Why this matters:
- `scan` currently performs best-effort skill auto-update side effects.
- Side effects in core analysis command can surprise CI/automation users.

Primary files:
- `desloppify/app/commands/scan/scan.py`
- `desloppify/app/commands/scan/scan_reporting_llm.py`

Canonical upgrade:
- Gate skill update behind explicit flag (`--auto-update-skill`) or config default-off for CI.

## Cardinal-Harness Integration Blueprint

Use Cardinal as a backend + adjudication layer, not just another runner:

1. Batch generation remains in current review prepare pipeline.
2. Backend executes N independent judges per batch/dimension.
3. Cardinal adjudicates:
   - consensus score,
   - disagreement measure,
   - rationale quality.
4. Import path stores:
   - per-judge raw outputs,
   - adjudicated output,
   - reliability metadata.
5. Scoring uses adjudicated score + reliability-aware penalties.

Minimal integration points:
- backend registration and selection in review runner flow.
- canonical provenance extension in import policy.
- dimension score payload extension for reliability metadata.

## Suggested Execution Order

1. Extract runner backend interface and migrate current Codex/Claude paths with no behavior change.
2. Add Cardinal backend behind feature flag.
3. Move subjective metadata/weights fully into `dimensions.json` and delete fallback maps.
4. Upgrade merge/scoring to include disagreement/reliability.
5. Add calibration pack (`golden` review fixtures + expected adjudications) and CI eval gate.

