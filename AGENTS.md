# Agent orientation

Start with README.md for commands and the proposal PDF for the research aims. Check the current branch and working tree before editing. Preserve other contributors' changes and identify the files your task touches when handing off.

- For prompt or model experiments, edit the relevant folder under debaters/. When comparing structures, keep the role profiles and topic fixed.
- For a new debate structure, add a module under debate/formats/ with run_round(ask) and register it in FORMATS in debate/__main__.py. Call ask(role, **arguments) with exactly the earlier turns that role should see. Return the text to carry into the next round.
- Keep provider calls in debate/api.py. The runner owns profile loading, mode selection and transcript capture. Credentials belong in the local ignored .env or process environment. Use .env.example when inspecting or documenting the key names.
- For final-summary, check that both speakers see the prior dialogue and the judge appears only after the final critic. The judge uses debaters/judge/summary.md. The runner appends the shared word limit to each role's system prompt.
- Verify changed formats with a two-round offline run. Inspect the JSON to confirm speaker order, which arguments each role received, and that round two starts from round one's revision. Report whether verification used mock or live responses.
- Generated transcripts live under the ignored runs/ directory. Share the format, topic, round count, and profile changes in experiment handoffs so teammates can reproduce the setup.
- For iteration experiments, verify each child starts from its parent's revised proposition with fresh dialogue history. Check word limits against the role-specific values in the JSON. Record which iteration checkpoints share the same chain when comparing results.
