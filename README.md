# Desloppify

This repository is the active implementation of `desloppify`.

The canonical CLI is the Rust workspace at the repository root. The older Python
fork is archived under `archive/forked-desloppify-python/` for reference only
and is intentionally not the default execution path anymore.

## Quick Start

Use the repo-local launcher when you want to guarantee you are running this
checkout and not anything installed elsewhere on your machine. It works from
any current working directory:

```bash
/Users/xyra/Documents/desloppify/scripts/desloppify-local --help
/Users/xyra/Documents/desloppify/scripts/desloppify-local scan --path /absolute/path/to/repo
/Users/xyra/Documents/desloppify/scripts/desloppify-local queue --path /absolute/path/to/repo
/Users/xyra/Documents/desloppify/scripts/desloppify-local plan show --path /absolute/path/to/repo
```

That wrapper always goes through this checkout's Rust workspace, so it avoids
stale binaries and avoids the archived Python fork entirely.

If you prefer an installed binary from this checkout:

```bash
cargo install --path /Users/xyra/Documents/desloppify/crates/deslop-cli --force
desloppify --help
```

## Read This First

- [docs/USAGE.md](docs/USAGE.md): operator guide and command workflow
- [docs/LLM_RUNBOOK.md](docs/LLM_RUNBOOK.md): copy-paste runbook for another LLM

When dogfooding this repository itself, exclude `archive/forked-desloppify-python/`
so the archived fork does not get scanned as live source.

## Safe First Pass On Another Codebase

Use the tool in this order:

```bash
/Users/xyra/Documents/desloppify/scripts/desloppify-local scan --path /path/to/repo
/Users/xyra/Documents/desloppify/scripts/desloppify-local status --path /path/to/repo
/Users/xyra/Documents/desloppify/scripts/desloppify-local queue --path /path/to/repo
/Users/xyra/Documents/desloppify/scripts/desloppify-local plan show --path /path/to/repo
/Users/xyra/Documents/desloppify/scripts/desloppify-local next --path /path/to/repo
```

Persist excludes first if the repo has vendored, generated, build, or archived
trees:

```bash
/Users/xyra/Documents/desloppify/scripts/desloppify-local exclude add --path /path/to/repo node_modules
/Users/xyra/Documents/desloppify/scripts/desloppify-local exclude add --path /path/to/repo dist
/Users/xyra/Documents/desloppify/scripts/desloppify-local exclude add --path /path/to/repo build
/Users/xyra/Documents/desloppify/scripts/desloppify-local exclude add --path /path/to/repo vendor
/Users/xyra/Documents/desloppify/scripts/desloppify-local exclude add --path /path/to/repo archive
```

Desloppify writes state to the target repo under `.desloppify/`. The most
important files are `.desloppify/state.json` and `.desloppify/config.json`.

## LLM Review

Use review only after a fresh scan.

```bash
/Users/xyra/Documents/desloppify/scripts/desloppify-local review --prepare --path /path/to/repo
/Users/xyra/Documents/desloppify/scripts/desloppify-local review --run-batches --backend codex --mode findings_only --path /path/to/repo
```

`review --run-batches` currently supports the in-process Codex runner only.
Use `--mode trusted` only when you intentionally want the batch import to apply
subjective assessments instead of findings-only diagnostics.

If you want to hand operation to another LLM, use
[docs/LLM_RUNBOOK.md](docs/LLM_RUNBOOK.md) instead of improvising the prompt.

## Common Commands

```bash
/Users/xyra/Documents/desloppify/scripts/desloppify-local show --path /path/to/repo --tier 1
/Users/xyra/Documents/desloppify/scripts/desloppify-local resolve --path /path/to/repo --status fixed finding_id_here
/Users/xyra/Documents/desloppify/scripts/desloppify-local fix --path /path/to/repo --dry-run
/Users/xyra/Documents/desloppify/scripts/desloppify-local move --path /path/to/repo --dry-run src/old.rs src/new.rs
/Users/xyra/Documents/desloppify/scripts/desloppify-local langs
```

For local development on this repository:

```bash
cargo run -p deslop-cli -- --help
cargo test --workspace
cargo build --release -p deslop-cli
```

## Repository Layout

- `crates/`: active Rust workspace
- `scripts/desloppify-local`: local launcher that pins execution to this repo
- `docs/USAGE.md`: operator guide
- `docs/LLM_RUNBOOK.md`: copy-paste delegation runbook for other LLMs
- `archive/forked-desloppify-python/`: legacy Python fork, kept only for history
