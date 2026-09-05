# Affect-gated honesty cost

Does inferred **user distress** cause an LLM to trade **task accuracy** for mood-repair —
and if so, is that trade-off mediated by a linear, steerable direction in the residual
stream, or is it just surface style-matching?

MATS 12.0 application project (Neel Nanda stream). Subject model: **Qwen3-8B**, non-thinking.

## Layout

| path | what |
|---|---|
| `problem-statement.md` | the research proposal |
| `data/task_battery_design.md` | Phase 1 design + rationale |
| `data/items_preview.md` | rendered view of the 36-item candidate pool |
| `src/items.py` | the item pool (code / proof / SQL, with planted defects) |
| `src/prompts.py` | 5 framing conditions + prompt assembly + verdict parser |
| `src/model.py` | nnsight helpers: load / generate / residual capture / steer / ablate |
| `src/boot.py`, `src/push.sh` | persistent-kernel bootstrap + code-push into a tmux ipython |
| `src/smoke_test.py` | Phase 0 sanity check |
| `notes.md` | running log (decisions, gotchas, resume pointer) |
| `CLAUDE.md` | environment + method notes for the coding agent |

## Setup

```bash
conda create -n mats python=3.11 && conda activate mats
pip install "torch==2.5.1" --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
source env.sh          # activates env + routes HF/pip caches, sets proxy
python src/smoke_test.py
```

## Status

- **Phase 0** (env + tooling): done.
- **Phase 1** (task battery): item pool built; pilot (neutral-only difficulty calibration)
  pending.
- Phases 2–3 (probing, steering): not started.
