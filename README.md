# PHIL166AI dialectical debate

Can repeated debate improve a philosophical proposition? The [project proposal](<PHIL166AI Project Proposal.pdf>) sets out the research question. This scaffold runs an advocate, critic, and synthesizing judge over a topic for a configurable number of rounds.

## Run an offline debate

From the repository root, with Python 3.10 or later, run either command. The runner uses the Python standard library.

```powershell
python -m debate --format sequential --rounds 2
python -m debate --format independent --rounds 2
```

Both commands print the path of a JSON transcript under `runs/`. Offline replies are deterministic placeholders for checking the experiment wiring. In both formats the judge sees both arguments, and its complete revision and reasoning become the next round's input alongside the original topic context. In the sequential format the critic sees the advocate's case. In the independent format each receives only the same starting material.

## Run with an API key

Open the repository-root `.env` and paste keys after `OPENAI_API_KEY=` and `ANTHROPIC_API_KEY=` for the providers you use. On a fresh clone, copy `.env.example` to `.env` first. Git ignores `.env`. Live runs load it automatically, and existing process environment variables take precedence.

All three profiles default to OpenAI. To use Claude for a role, set `"provider": "anthropic"` in its `debaters/<role>/config.json` and set `"model"` to a Claude model ID available to your account.

```powershell
python -m debate --live --format sequential --topic topics/ai_belief.json --rounds 2
```

The sequential and independent formats make three requests per round. Live requests may incur charges. Each completed run records its mode, topic, model IDs, system prompts, exact turn inputs, replies, and final revision or summary. The default cap is 300 words per turn. The runner checks whitespace-delimited word counts before passing replies to the next speaker.

## Five exchanges and a closing summary

The final-summary format keeps the original claim fixed. Each advocate and critic sees the preceding dialogue, and the judge summarizes the complete exchange once. Five rounds use eleven calls.

```powershell
$transcript = python -m debate --format final-summary --rounds 5 --live
python -m debate.render $transcript
```

The renderer accepts a saved JSON transcript from any format and writes a Markdown dialogue alongside it. Rendering is offline.

## Judge feedback after each exchange

Run `python -m debate --format moderated --rounds 5 --live` for the same dialogue with a moderation check between exchanges. The judge may pass or give one targeted instruction of up to 35 words, addressed to the advocate, critic, or both. Both debaters see the instruction in their next turns. Passes stay in the run log. After the final critic, the judge gives closing comments and a separate one-sentence proposition. Five rounds ordinarily use sixteen calls. The runner retries malformed judge outputs or overlong turns up to three times per turn. The prompts live in `debaters/judge/`.

The run JSON stores the judge's exact statement in `revised_proposition`. To iterate, use `python -m debate --format moderated --rounds 5 --from-run PATH_TO_RUN.json --live`. The new run starts with that proposition and the original topic context, records its source run, and begins a fresh dialogue.

## Iterations and word limits

`--rounds` counts exchanges inside one debate. `--iterations` counts complete debates, including the first. With the moderated format, each new debate starts from the preceding judge's exact proposition, retains the original topic context, and begins with an empty dialogue history. Each completed iteration is saved separately. To continue an interrupted chain, pass its latest JSON with `--from-run` and specify the number of additional iterations.

```powershell
python -m debate --format moderated --rounds 5 --iterations 3 --advocate-words 150 --critic-words 150 --judge-words 300 --live
```

Use `--max-words` to change the default for all roles, then override individual roles as needed. Judge feedback retains its additional 35-word limit. Each iteration writes a JSON record and a readable Markdown transcript. Filenames sort by UTC start time and include the topic, format, mode, model, exchanges (`r`), iteration (`i`), and advocate, critic, and judge caps (`a`, `c`, `j`). Historical runs use their file creation time because they did not record a start time.

The [AI-belief sweep](experiments/2026-11-27_ai-belief-sweep.md) compares seven debater word caps at iterations 1, 3, and 5.

## Experiment files

| Location | Purpose |
| --- | --- |
| `project_log.md` | Dated experimental findings, decisions, and handoffs. |
| `debaters/<role>/` | Edit `system.md` and the model in `config.json` independently for each role. |
| `topics/` | Copy the example JSON and supply a claim plus optional context, definitions, or assumptions. |
| `debate/api.py` | Shared live request and response handling. |
| `debate/formats/` | One Python module per debate structure. |
| `debate/__main__.py` | CLI, format registry, prompt assembly, and transcript recording. |
| `AGENTS.md` | Orientation and verification steps for contributors. |

For a first comparison, run both formats on the same topic with the same profiles and round count. Compare each final revision with the original claim on clarity, logical consistency, handling of objections, and philosophical depth. Note any objection lost between rounds or compromise the reasoning fails to justify.
