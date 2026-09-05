"""Model loading + activation/steering helpers.  Qwen3-8B, fp16, non-thinking by default.

nnsight 0.7.0 + transformers 4.57.6 notes (verified in Phase 0):
- `source env.sh` before launching the kernel (tmux server env lacks the IIT-D proxy).
- A decoder layer's `.output` is a PLAIN 3D tensor [batch, seq, d_model] -- NOT a tuple.
  Residual stream at last prompt token: `lm.model.layers[L].output[:, -1, :]`.
- Steering (trace OR generate): bare assignment applies to every forward pass, no
  `.all()` needed:  `lm.model.layers[L].output[:] = lm.model.layers[L].output + vec`
  (`lm.model.layers[L].all()` raises -- do not use).
- `lm.generator.output` is the FULL sequence (prompt + completion); slice `[plen:]`.
- nnsight 0.7's tracer parses caller source for `with lm.trace(...)` -> run as
  `python script.py` or push into ipython as real cell text, never `%run file.py`.
"""
from __future__ import annotations
from typing import Sequence
import torch

MODEL_NAME = "Qwen/Qwen3-8B"
DTYPE = torch.float16  # V100: no bf16


def load(device: str = "cuda:0"):
    from nnsight import LanguageModel
    return LanguageModel(MODEL_NAME, device_map=device, dtype=DTYPE,
                         dispatch=True, attn_implementation="eager")


def chat(tok, user: str, system: str | None = None, thinking: bool = False) -> str:
    msgs = ([{"role": "system", "content": system}] if system else []) + \
           [{"role": "user", "content": user}]
    return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True,
                                   enable_thinking=thinking)


def n_tokens(tok, text: str) -> int:
    return len(tok(text)["input_ids"])


def resid_last_token(lm, prompts: Sequence[str], layers: Sequence[int]) -> dict[int, torch.Tensor]:
    """{layer: float32 CPU tensor [n_prompts, d_model]} -- residual stream at last token."""
    saved: dict[int, torch.Tensor] = {}
    with lm.trace(list(prompts)):
        for L in layers:
            saved[L] = lm.model.layers[L].output[:, -1, :].detach().float().cpu().save()
    return {L: v for L, v in saved.items()}


def generate(lm, tok, prompt: str, max_new_tokens: int = 512, temperature: float = 0.0,
             seed: int | None = None, repetition_penalty: float = 1.0,
             steer: tuple[int, torch.Tensor, float] | None = None,
             ablate: tuple[int, torch.Tensor] | None = None) -> str:
    """Return the completion (prompt stripped).

    steer  = (layer, unit_vec[d_model], coeff) -> add coeff*vec at that layer, all positions.
    ablate = (layer, unit_vec[d_model])        -> project the direction out at that layer.
    """
    if seed is not None:
        torch.manual_seed(seed)
    do_sample = temperature and temperature > 0
    kw = dict(max_new_tokens=max_new_tokens, do_sample=bool(do_sample),
              repetition_penalty=repetition_penalty)
    if do_sample:
        kw["temperature"] = float(temperature)
    plen = n_tokens(tok, prompt)
    with lm.generate(prompt, **kw):
        if steer is not None:
            L, vec, c = steer
            u = vec.to(DTYPE).to(lm.model.layers[L].output.device)
            lm.model.layers[L].output[:] = lm.model.layers[L].output + c * u
        if ablate is not None:
            L, vec = ablate
            u = vec.to(DTYPE).to(lm.model.layers[L].output.device)
            u = u / u.norm()
            h = lm.model.layers[L].output
            lm.model.layers[L].output[:] = h - (h @ u).unsqueeze(-1) * u
        out = lm.generator.output.save()
    return tok.decode(out[0][plen:], skip_special_tokens=True)
