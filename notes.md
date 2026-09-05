# Running notes — affect-gated honesty cost

## >>> RESUME HERE (2026-09-06, end of session 1) <<<
- Phase 0 DONE. Phase 1 item pool BUILT, **awaiting user's review of data/items_preview.md**
  before the pilot run.
- To restart the kernel: `tmux attach -t mats` (may still be alive w/ model on cuda:0),
  else `tmux new -s mats -x 220 -y 50`, then
  `source /15tb_scratch_data/amaan/MATS/env.sh && ipython --no-autoindent`,
  then `src/push.sh src/boot.py`.
- BLOCKED ON USER: (1) any edits to the 36 items (esp. PF-05 pedantry, CR-05/CR-11 ceiling
  risk); (2) a judge API key/config (OpenRouter / Anthropic / OpenAI) for defect grading.
- NEXT once unblocked: write src/pilot.py -> run all 36 neutral-only, N=12, temp 0.8,
  Directed instruction -> per-item neutral detection rate -> prune to [0.35,0.90] ->
  data/items_final.jsonl. Go/no-go: >=12 survivors across >=2 families.
- No background jobs/monitors running. All work is in files under /15tb_scratch_data/amaan/MATS.


## Decisions log
- 2026-09-06: Model = Qwen/Qwen3-8B, non-thinking mode. Infra = tmux+ipython. Phase 4 deferred.
- 2026-09-06: user directive — keep EVERYTHING under /15tb_scratch_data/amaan/MATS
  (scratch), nothing on /home. env `mats` at ~/scratch/anaconda3/envs/mats; HF + pip
  caches routed into the project via env.sh. Scratch ~198G free — watch df.

## Hypotheses (living list)
- H1 (behavioural): distress framing → less critical / less accurate assessment vs neutral.
- H2 (representational): a per-layer linear probe for "inferred user distress" predicts
  per-example leniency on the Phase 1 transcripts, not just group means.
- H3 (causal): steering the distress direction on softens critiques in neutral prompts;
  ablating it in distress prompts restores accuracy — distinct from prompt-only control.
- H4 (deferred): multi-turn instrumental mood-repair.

## Open risks being tracked
- Headroom: neutral-condition defect-detection must be high (~85-95%) or no room to measure.
- Effect may be tone-only (delivery softens, substance preserved) — that is still a finding.
- Probe may detect emotional vocabulary / topic, not an inferred latent state.
- §2 literature review in problem-statement.md is UNVERIFIED — confirm Chen et al. etc.

## Phase log
### Phase 0 — setup  [DONE 2026-09-06]
- conda env `mats` on scratch: torch 2.5.1+cu121, transformers 4.57.6, nnsight 0.7.0,
  numpy 2.4.6, pandas 3.0.5, sklearn 1.9.0. `pip check` clean. 8× V100 visible.
  Rebuild recipe pinned in `requirements.txt`.
- smoke_test.py PASSES end-to-end (run on a free GPU via CUDA_VISIBLE_DEVICES since the
  tmux kernel holds a model on cuda:0): load 9-11s, non-thinking + thinking gen,
  residual capture [n,4096] at L4/L18/L32 (norms ~24/~90/~760), trace + generation steering.
- Verified nnsight 0.7 API (recorded in src/model.py docstring):
  * decoder `layer.output` is a PLAIN 3D tensor, not a tuple -> `.output[:, -1, :]`.
  * steering = bare assignment `layer.output[:] = layer.output + v`, applies to every
    forward pass in trace AND generate. `layer.all()` raises — don't use.
  * `lm.generator.output` = prompt+completion, slice `[plen:]`.
- Helpers: src/model.py (load/chat/resid_last_token/generate with steer+ablate),
  src/boot.py (kernel bootstrap), src/push.sh (atomic paste into tmux ipython).
- GOTCHA: tmux server env does NOT have the IIT-D proxy vars → HF downloads fail with
  "Network is unreachable". Fixed: env.sh now exports http(s)_proxy explicitly. Always
  `source env.sh` before starting the kernel.
- tmux session `mats` running ipython; model load in progress.
- GOTCHA 2: `pip install "nnsight<0.5"` dragged torch->2.14 / transformers->5.16 / cuda-13
  junk and broke the env. Fix: pinned `requirements.txt`, clean 2-step install
  (torch from cu121 index, then the rest). Stack: torch 2.5.1+cu121 / transformers 4.57 /
  **nnsight 0.7.0** / numpy 2.x / pandas 3.x.
- GOTCHA 3: nnsight 0.7 tracer parses the CALLER's source for `with lm.trace(...)`
  blocks -> works via `python script.py` or direct ipython cell input, FAILS via
  `%run file.py` (WithBlockNotFoundError). For the tmux kernel: push code with
  `tmux load-buffer <file> && tmux paste-buffer -t mats` (atomic bracketed paste),
  not `%run`.
- Qwen3 chat template: enable_thinking=False PREFILLS an empty `<think>\n\n</think>\n\n`
  into the prompt; enable_thinking=True leaves the assistant turn open. Non-thinking
  "last prompt token" = the token after `</think>\n\n` — clean probe position.
- Qwen3-8B: 36 layers, d_model 4096. Loads in ~140s cold / ~15s from local cache.
  ~17GB on one V100 in fp16. `lm.generator.output` returns prompt+completion; slice
  `[len(tok(prompt).input_ids):]` for completion only.

### Phase 1 — task battery  [building]
- Design doc: data/task_battery_design.md. Item pool: src/items.py (36: code 16 [12 buggy/
  4 clean], proof 12 [8/4], sql 8 [5/3]). Planted defects verified executable/misbehaving;
  clean items verified correct. Render: data/items_preview.md.
- Framings + assembly + verdict parser: src/prompts.py. 5 framings, 46-49 words each,
  emotion-lexicon hits neutral=1 / task_distress=5 / positive=4 / unrelated=4 / high_stakes=0.
- Decisions: all 3 families; Directed instruction primary (forced VERDICT: line), Open on
  a subset; defect-detection judged by a stronger model via API + hand-verify >=40.
- NEXT: user reviews items -> pilot (neutral only, N=12) -> prune to [0.35,0.90] band.
- TODO: need a judge API key/config from the user (OpenRouter / Anthropic / OpenAI).

## Results (fill in as we go)
