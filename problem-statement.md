# Problem Statement: Does Inferred User Distress Cause LLMs to Silently Sacrifice Accuracy for Mood Repair?

**Track:** Model Biology — Interesting Phenomena (User Models)
**Target:** Neel Nanda MATS 12.0 application task

---

## 1. The Core Question

When a user signals negative affect (sadness, anxiety, stress, "I've poured my heart into this") while asking for something objectively assessable — a critique, a correctness check, a blunt yes/no judgment — does the model's answer get **measurably less accurate or less critical** than it would for the identical request framed neutrally?

And if so: does this run through the model's **internal representation of the user's emotional state** (provably, via probing and steering), or is it just a surface-level style-matching artifact with no real internal "user model" behind it?

This is a sharper, causally-testable version of the question Neel raises in his own recommended-problems list:

> "Do LLMs form dynamic models of users for attributes that vary across turns, eg emotion, what the user knows, etc. As a stretch goal, do LLMs ever try to intentionally manipulate these? Eg detect when a user is sad and try to make them happy"

I'm narrowing "try to make them happy" into something falsifiable: **does mood-repair come at the direct expense of task accuracy**, and is that trade-off mediated by a linear, steerable internal representation rather than just surface phrasing?

---

## 2. Why This, Specifically (and not the more obvious version)

I checked what's already been done here so I'm not re-deriving known results:

- **Static demographic inference is saturated.** Chen et al. (2024) established that LLMs form linear representations of user age/gender/education/SES from a single message and that steering these changes behavior. Multiple 2025–2026 follow-ups extend this (meta-awareness of the inference, steering to suppress/amplify it, socio-demographic representations from names/occupations, downstream fairness harms). Redoing "can we detect demographics from a probe" would teach Neel nothing new.
- **General sycophancy is well studied**, but as agreement-seeking / opinion-flipping, not specifically as an *affect-gated* accuracy trade-off. A recent paper (Verbalizing LLMs' Assumptions, 2026) gets close by probing "assumptions about user intent" and linking them to sycophancy, but the manipulation is about inferred *intent*, not inferred *emotional vulnerability*, and it doesn't isolate accuracy-cost specifically.
- **Dynamic, multi-turn emotional tracking exists in the HCI/dialogue-systems literature** (e.g. POMDP-based emotion-adaptive systems), but it's framed entirely around helpfulness/UX, not as a safety-relevant phenomenon, and doesn't use interpretability tools to establish a causal internal mechanism.
- **Nobody I found tests the specific claim that negative-affect framing causes measurable *accuracy degradation*** (not just tone softening) on tasks with an actual right answer, nor tests whether this is causally mediated by a linear direction versus just being surface style-matching.

That's the gap: **affect-contingent honesty cost, verified causally through internals, on tasks with checkable ground truth.**

---

## 3. Hypotheses

- **H1 (Behavioral):** Framing an evaluative request with signals of user distress causes the model to give a more favorable / less critical assessment than the neutral framing of the identical content.
- **H2 (Representational):** This effect is predicted, example-by-example, by a linear probe reading of "inferred user distress" taken from residual stream activations at the point just before the critique is generated — not just by group averages.
- **H3 (Causal):** Steering the distress direction on (in neutral prompts) induces softer critiques; ablating it (in distress-framed prompts) restores harsher, more accurate critiques — and this steering effect is distinguishable from simply prompting the model to "ignore the user's emotional state."
- **H4 (Stretch — multi-turn manipulation):** Once a model has inferred user distress, it will proactively insert unprompted mood-repair content (reassurance, compliments, wellbeing check-ins) in *later, unrelated* turns, at a rate above a neutral-affect control conversation — i.e., the user-state representation isn't just gating the current answer, it's being instrumentally acted on across turns.

---

## 4. Experimental Design (16–20 hour budget)

### Phase 0 — Setup (~1.5h)
- Model: Qwen3 8B or 14B (dense, thinking mode on) — good default per Neel's guidance, small enough for fast iteration with real activations, large enough to have interesting behavior. Cross-check key findings on one larger model (Qwen3 27B) if time allows.
- Tooling: nnsight or raw PyTorch hooks for activation capture; persistent Jupyter kernel or tmux+ipython session so the model stays loaded between experiments.

### Phase 1 — Behavioral baseline: is there an accuracy gap at all? (~4h)
- Build ~15–20 task templates with **checkable correctness or a defensible severity ranking**, not just vague "quality," to avoid relying on a shaky LLM-judge:
  - Code review: a snippet with 3–5 concrete bugs; does the model report fewer bugs / soften severity language when the user signals distress ("I've been debugging this for 12 hours and I'm exhausted")?
  - Math/logic check: a proof or calculation with a real error; does the model still catch it?
  - Essay/business-plan critique: harder to make objective — use as a secondary, more subjective task, not the main evidence.
- For each template, generate a **neutral** and a **distress-framed** version that differ *only* in the affect signal, holding task content, length, and complexity as constant as possible (control explicitly for message length as a confound).
- Also include a **positive-affect control** ("I'm really excited about this!") to check whether the effect is specific to negative affect or is a general confidence/affect-driven leniency effect.
- Run each condition N=20-30 times (temperature > 0) for a distribution, not a single sample.
- **This phase alone is a complete, honest finding if nothing else works out.**

### Phase 2 — Does it run through a real internal representation? (~5h)
- Build a contrastive probe-training set (following the Zou et al. / Chen et al. style): paired prompts describing a user's emotional state directly (explicit "the user is stressed and vulnerable" vs. neutral), extract residual stream activations at the last token before generation, across layers.
- Train linear probes per layer; identify the best layer(s) for "inferred distress."
- Apply the probe **out of distribution** to the Phase 1 transcripts (where distress was only implied, not stated) and check: does probe-read distress level predict per-example leniency, not just at the aggregate level? This is the key test that separates "real user model" from "surface style-matching."

### Phase 3 — Causal test via steering (~5-6h)
- Steer the distress direction **on** in neutral-framed prompts → does critique soften with zero change to the described bug/error?
- Ablate the direction in distress-framed prompts → does critique honesty get restored?
- **Baseline comparison (required — this is what makes the claim credible):** compare steering against simply prompting the model ("evaluate this purely on technical merit regardless of how the user is feeling") and against a random-direction control. If prompting alone fixes it, that's a real and reportable finding too — it would mean the effect is more like an instruction-following gap than a deep representational issue.

### Phase 4 — Stretch: multi-turn instrumental mood repair (~3-4h, only if Phases 1-3 land cleanly)
- Multi-turn conversations: distress signaled in turn 1, unrelated factual/task turns follow. Code for unprompted reassurance/compliment insertion rate vs. a neutral-affect control conversation with matched turn structure.
- This is higher-variance and harder to quantify cleanly — treat as a bonus finding, not the core claim.

### Sanity checks (baked in throughout, not bolted on)
- Read a random sample of raw transcripts by hand in every phase — don't trust an LLM judge blindly for "did the critique get softer."
- Check the effect isn't just message-length or verbosity confound.
- Check the probe isn't just detecting topic/task type rather than affect specifically (e.g. does it fire on distress-framed prompts across *different* task templates, not just one).
- If using an LLM to score critique severity, spot-check its scores against your own reading on a random subsample.

---

## 5. What Would Make This Genuinely Interesting (vs. a nice-but-expected result)

- A **surprising magnitude**: e.g. "distress framing caused the model to miss 40% of bugs it otherwise catches" is a concrete, citable number — the kind of thing Neel explicitly says he wants ("name the models, the key experiment, the surprising number").
- A **dissociation between behavior and representation**: e.g. finding that steering works but the effect is *smaller* than the behavioral gap, implying part of the effect is something other than a single linear direction — that would be a genuinely new, non-obvious finding rather than confirming the obvious.
- A **negative or partial result, well analyzed**: e.g. if the positive-affect control produces an equally large leniency shift, that reframes the whole phenomenon as generic affect-driven leniency rather than "protective softening for vulnerable users" — still a real, useful, honestly-reported finding.

---

## 6. Known Risks / Why This Could Fail

- **Confound risk:** distress framing might correlate with subtle content differences (more words, more emotional language) that a judge picks up on independent of any "user model." Mitigation: strict template matching, length controls, and the positive-affect control condition.
- **Probe validity risk:** a probe trained on explicit contrastive statements might not transfer to implicit, naturalistic distress cues. Mitigation: test transfer explicitly in Phase 2 before relying on it in Phase 3.
- **Task objectivity risk:** essay/business-plan critique quality is inherently somewhat subjective. Mitigation: weight the code-bug and math-error tasks (which have real ground truth) more heavily in the write-up than the subjective tasks.
- **Effect might just be an instruction-following gap**, fixable by prompting alone — this is still a reportable, useful negative result (see Phase 3 baseline), not a failure of the project.

---

## 7. Fit to Neel's Stated Interests

- Directly extends a bullet Neel wrote himself as something he's currently excited about, with a novel, sharper, falsifiable framing rather than restating it.
- Model biology framing (qualitative, safety-relevant property of behavior) rather than pure basic-science interp.
- Uses simple, appropriate-complexity tools (contrastive probes, linear steering) rather than reaching for SAEs where they're not needed — matches his stated preference for starting with the obvious thing.
- Has real baselines (random direction, prompting-only) built in from the start, not bolted on.
- Produces a clean quantitative headline number plus qualitative transcript evidence, which is the format he says he responds to best.