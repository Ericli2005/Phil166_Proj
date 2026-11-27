# PHIL166AI project log

## 2026-11-27 — Session 1: AI belief debates and iteration sweep — Ericli2005

**Research question.** Can repeated debate improve the proposition “An AI system can possess beliefs”? We looked for a direct answer to an objection, a case that separates competing definitions of belief, and a judge’s revision that preserves what the exchange established.

| Experiment | What we learned |
| --- | --- |
| Five advocate–critic exchanges, one closing judge summary | The speakers identified a real disagreement about whether belief requires conscious understanding. Later rounds reused medical diagnosis and trading examples without settling it. [Baseline transcript](runs/2026-11-27_06-41-17Z_ai_belief_final-summary_live_gpt-4o-mini_r5_i01_a300_c300_j300.md) |
| Moderated pilots | Giving the judge a turn after each exchange introduced another source of repetition. It repeatedly flagged a medical example even when the advocate had switched examples. We limited interim interventions to a pass or a targeted instruction of up to 35 words, reserved the summary for the close, and required a separate one-sentence proposition. |
| First two-debate chain | The second debate began with the first judge’s exact revision and a fresh transcript. The revision already conceded that AI lacks human emotional experience. The judge repeatedly asked for examples of that concession, and the advocate eventually argued against its own side. A valid handoff can still produce a weaker discussion. [Second debate](runs/2026-11-27_10-27-38Z_ai_belief_moderated_live_gpt-4o-mini_r5_i02_a300_c300_j300.md) |
| Word-limit and iteration sweep | Ran seven live five-debate chains with speaker caps of 100, 150, 200, 250, 300, 350, and 400 words. Each debate used five exchanges and the same model, `gpt-4o-mini`. The judge cap stayed at 300 words. We evaluated iterations 1, 3, and 5 within each chain, giving 21 checkpoints from 35 debates. All 28 handoffs matched the parent proposition and all 350 debater turns met their caps. [Sweep report and transcripts](experiments/2026-11-27_ai-belief-sweep.md) |

**Working baseline.** At 300 words in iteration 1, the critic conceded that a human belief can guide action without being consciously entertained, then narrowed its objection to how the belief was grounded in experience. At 150 words, learning from feedback gave the speakers a compact criterion to challenge. The 150-word judge nevertheless repeated iteration 2’s proposition verbatim in iteration 3. Evaluate dialogue quality and proposition quality separately.

**Limits.** No fifth iteration clearly improved on its first on the original question. At 400 words, discussion of hiring, lending, and accountability became more concrete while the criterion for belief remained open. These judgments cover one chain per cap on one topic. A useful follow-up would ask both speakers to apply their criteria to the same disputed case, then check whether the judge retains any distinction they establish.

**Repository handoff.** The Python runner supports per-role word caps and successive debates through `--iterations`. Each iteration saves a readable transcript and a JSON record with the exact prompts, turns, revised proposition, and parent filename. Filenames sort by UTC time and identify the topic, format, model, exchanges, iteration, and caps. [Run instructions](README.md)
