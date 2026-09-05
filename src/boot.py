# Kernel bootstrap. Push once at session start:  src/push.sh src/boot.py
import time, torch, numpy as np
from nnsight import LanguageModel

MODEL = "Qwen/Qwen3-8B"
_t = time.time()
lm = LanguageModel(MODEL, device_map="cuda:0", dtype=torch.float16,
                   dispatch=True, attn_implementation="eager")
tok = lm.tokenizer
NL, DM = lm.config.num_hidden_layers, lm.config.hidden_size
print(f"[boot] {MODEL} loaded in {time.time()-_t:.0f}s | layers={NL} d_model={DM}")


def chat(user, system=None, thinking=False):
    msgs = ([{"role": "system", "content": system}] if system else []) + \
           [{"role": "user", "content": user}]
    return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True,
                                   enable_thinking=thinking)


def ntok(text):
    return len(tok(text)["input_ids"])
