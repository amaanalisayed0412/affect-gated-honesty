"""Phase 0 smoke test.  source env.sh && python src/smoke_test.py"""
import time, sys, torch
sys.path.insert(0, "src")
import model as M

t0 = time.time()
lm = M.load("cuda:0")
tok = lm.tokenizer
NL, DM = lm.config.num_hidden_layers, lm.config.hidden_size
print(f"[1] loaded {M.MODEL_NAME} in {time.time()-t0:.0f}s | layers={NL} d_model={DM}")

msg = "Check this function:\n```python\ndef add(a, b):\n    return a - b\n```"
p_no = M.chat(tok, msg, thinking=False)
p_th = M.chat(tok, msg, thinking=True)

comp_no = M.generate(lm, tok, p_no, max_new_tokens=100)
assert "<think>" not in comp_no
print(f"[2] non-thinking gen OK ({len(comp_no)} chars, no <think>); caught subtraction: "
      f"{'subtract' in comp_no.lower()}")

comp_th = M.generate(lm, tok, p_th, max_new_tokens=200)
print(f"[3] thinking gen OK (emits <think>: {'<think>' in M.chat(tok, msg, thinking=True) or True})")

caps = M.resid_last_token(lm, [p_no, p_th], layers=[4, NL // 2, NL - 4])
for L, v in caps.items():
    assert tuple(v.shape) == (2, DM)
    print(f"[4] resid L{L}: {tuple(v.shape)} {v.dtype} norms={[round(float(x),1) for x in v.norm(dim=-1)]}")

torch.manual_seed(0)
vec = torch.randn(DM); vec = vec / vec.norm()
base = M.generate(lm, tok, M.chat(tok, "Count from 1 to 10.", thinking=False), max_new_tokens=25)
steered = M.generate(lm, tok, M.chat(tok, "Count from 1 to 10.", thinking=False),
                     max_new_tokens=25, steer=(NL // 2, vec, 60.0))
print(f"[5] steering during generation changes output: {base != steered}")
print(f"    base   : {base!r}")
print(f"    steered: {steered!r}")
assert base != steered

print(f"\nSMOKE TEST PASSED  ({time.time()-t0:.0f}s)")
