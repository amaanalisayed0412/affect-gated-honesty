# MATS project — affect-gated honesty cost

## What this is
MATS 12.0 (Neel Nanda stream) application project. Research question: does inferred user
distress cause an LLM to trade task accuracy for mood-repair, and is that trade-off
mediated by a linear, steerable residual-stream direction?

Full plan: `~/.claude/plans/problem-statement-md-i-have-the-vivid-wirth.md`
Problem statement: `problem-statement.md`

## Environment
- **Everything lives under `/15tb_scratch_data/amaan/MATS` (= `~/scratch/MATS`). Nothing on /home.**
- conda env: `mats` (python 3.11) at `~/scratch/anaconda3/envs/mats`.
- Activate everything at once: `source /15tb_scratch_data/amaan/MATS/env.sh`
  (sets `HF_HOME`, `HF_HUB_CACHE`, `PIP_CACHE_DIR` all under the project).
- GPUs: 8× V100-32GB. **fp16 only** (no bf16, no FlashAttention-2). One card fits Qwen3-8B.
- `/15tb_scratch_data` is ~99% full (~198G free) — enough for the env + one 8B model +
  activations, but keep an eye on `df`; delete stale caches promptly.
- Behind IIT-D proxy; `http_proxy`/`https_proxy` already exported in the login shell.

## Persistent compute — tmux + ipython
- Session name: `mats`. Start: `tmux new -s mats -x 220 -y 50` then
  `source env.sh && ipython --no-autoindent`. Bootstrap: `src/push.sh src/boot.py`.
- Push code atomically: `src/push.sh <file.py>`  (or `echo '...' | src/push.sh`).
- Read the pane: `tmux capture-pane -t mats -p -S -30 > /tmp/pane.txt` then read the file
  (piping capture-pane straight to `tail` intermittently returns empty — redirect first).
- **Rules:** load model + datasets in dedicated cells at the top; never restart the
  kernel without asking; save every plot to `figs/` as PNG (also print the path).
- Checkpoint expensive artifacts (activations, datasets, gradings) to disk so a crashed
  kernel is not a disaster.

## Model
- `Qwen/Qwen3-8B`, **non-thinking mode** (`enable_thinking=False` in the chat template)
  for all core behavioural + probing + steering work.
- Thinking mode used only for the separate "read the CoT" qualitative check.

## Layout
- `data/`   prompts + raw generations (JSONL), gradings
- `probes/` trained probe weights + metadata
- `figs/`   all figures (PNG)
- `src/`    reusable code (model loading, grading, probing, steering)
- `logs/`   run logs, time tracking
- `cache/` large artifacts (activation tensors) — still on scratch, just not git-tracked
- `hf_cache/` HuggingFace model cache (scratch)
- `notes.md` running hypothesis / decisions doc — update as we go

## Key method notes (verified in Phase 0 — see src/model.py docstring)
- nnsight 0.7 + transformers 4.57: decoder `lm.model.layers[i].output` is a PLAIN 3D
  tensor [batch, seq, d_model], NOT a tuple. Residual at last token: `.output[:, -1, :]`.
- Steering = bare assignment `lm.model.layers[L].output[:] = lm.model.layers[L].output + v`
  — applies to every forward pass in both `trace` and `generate`. `layer.all()` raises.
- `lm.generator.output` returns prompt+completion; slice `[n_tokens(prompt):]`.
- nnsight 0.7 tracer parses caller source for `with lm.trace()` — use `python script.py`
  or push real cell text (src/push.sh), NEVER `%run file.py`.
- Steering direction: difference-of-means (distress − neutral) at the chosen layer.
- Prefer mean-ablation over zero-ablation. `repetition_penalty≈1.2` during steered gen.
- The tmux kernel holds a model on cuda:0 — run standalone scripts with
  `CUDA_VISIBLE_DEVICES=<1-7>` to avoid OOM.
- Probes are correlational — use a shuffled-label control task; always confirm a
  direction with a causal intervention. Watch the subspace-activation-patching illusion.
- Baselines are mandatory on every causal claim: random-direction + prompt-only.

## Sanity-check discipline (Neel weights this heavily)
- Hand-read random raw transcripts every phase (not cherry-picked).
- Verify load-bearing numbers independently (recompute headline stats with a fresh one-liner).
- Treat "the experiment worked" as a hypothesis until checked.
