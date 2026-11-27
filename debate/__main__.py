import argparse
import json
import re
from pathlib import Path
from datetime import datetime, timezone

from .api import KEY_NAMES, generate, load_keys
from .formats import final_summary, independent, moderated, sequential
from .render import render

ROOT = Path(__file__).resolve().parents[1]
FORMATS = {"sequential": sequential, "independent": independent,
           "final-summary": final_summary, "moderated": moderated}
WORD_LIMIT = 300


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def transcript_stem(started, topic_name, record):
    limits = record["word_limits"]
    models = list(dict.fromkeys(p["model"] for p in record["profiles"].values()))
    # Full topic text and per-role provider/model mappings live in the JSON.
    def slug(value):
        return re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip(".-")[:48] or "topic"

    return (f"{started:%Y-%m-%d_%H-%M-%SZ}_{slug(topic_name)}_{record['format']}_"
            f"{record['mode']}_{slug('+'.join(models))}_r{len(record['rounds'])}_"
            f"i{record['iteration']:02d}_a{limits['advocate']}_c{limits['critic']}_j{limits['judge']}")


def judge_format_error(role, reply):
    if role not in ("judge_feedback", "judge_proposition"):
        return
    if role == "judge_feedback" and reply == "PASS":
        return
    # Ask for plain punctuation so sentence boundaries can be checked locally.
    sentence = re.fullmatch(r"[^.!?\r\n]+[.]", reply)
    if role == "judge_feedback":
        if not (sentence and len(reply.split()) <= 35
                and re.match(r"^(Advocate|Critic|Both), ", reply)):
            return "Return exactly PASS or one instruction under 36 words starting with Advocate, Critic, or Both, and ending with a period. Omit the recap."
    elif not sentence:
        return "Write only one standalone declarative claim ending with a period. Spell out abbreviations and omit headings and explanations."


def run(args, iteration=1):
    started = datetime.now(timezone.utc)
    if args.live:
        load_keys(ROOT / ".env")
    if args.from_run:
        previous = read_json(args.from_run)
        if not previous.get("revised_proposition"):
            raise ValueError("The selected run has no recorded revised proposition.")
        topic = {**previous["topic"], "claim": previous["revised_proposition"]}
        topic_name = previous.get("topic_name") or previous["topic"]["claim"]
        iteration = previous.get("iteration", iteration - 1) + 1
    else:
        topic = read_json(args.topic)
        topic_name = args.topic.stem
    claim = topic["claim"]
    context = topic.get("context", "")
    if not isinstance(claim, str) or not claim.strip() or not isinstance(context, str):
        raise ValueError("Topic requires a nonempty claim and optional text context.")
    profiles = {}
    limits = {role: getattr(args, role + "_words") or args.max_words
              for role in ("advocate", "critic", "judge")}
    summarize_at_end = args.format in ("final-summary", "moderated")
    roles = ["advocate", "critic", "judge"]
    if args.format == "moderated":
        roles.extend(["judge_feedback", "judge_proposition"])
    for role in roles:
        folder = ROOT / "debaters" / ("judge" if role.startswith("judge_") else role)
        config = read_json(folder / "config.json")
        model = config["model"]
        provider = config.get("provider", "openai")
        if provider not in KEY_NAMES:
            raise ValueError(f"Choose openai or anthropic as provider for {role}.")
        filename = "summary.md" if summarize_at_end and role == "judge" else "system.md"
        if role == "judge_feedback":
            filename = "feedback.md"
        if role == "judge_proposition":
            filename = "proposition.md"
        prompt = (folder / filename).read_text(encoding="utf-8").strip()
        if not isinstance(model, str) or not model.strip() or not prompt:
            raise ValueError(f"Check the model and system prompt for {role}.")
        if args.format == "moderated" and role in ("advocate", "critic"):
            prompt += ("\nTake the judge's feedback seriously. On your next turn, answer any "
                       "question or repetition flag addressed to you or both speakers. If the "
                       "judge misread you, explain where. Engage your opponent's actual criterion "
                       "and say what you concede or why their inference fails.")
        prompt += f"\nUse at most {limits[role.split('_')[0]]} words in your response."
        profiles[role] = {"provider": provider, "model": model, "system": prompt}

    record = {"format": args.format, "mode": "live" if args.live else "mock",
              "started_at": started.isoformat(), "iteration": iteration, "word_limits": limits,
              "topic_name": topic_name, "topic": topic, "profiles": profiles, "rounds": []}
    history = []
    if args.from_run:
        record["source_run"] = args.from_run.name
    for number in range(1, args.rounds + 1):
        turns = []

        def ask(role, **arguments):
            message = json.dumps({"claim_and_reasoning": claim, "context": context,
                                  "arguments": arguments}, ensure_ascii=False)
            limit = limits[role.split("_")[0]]
            for attempt in range(4):
                if args.live:
                    reply = generate(**profiles[role], message=message)
                elif role == "judge_feedback":
                    reply = "PASS"
                elif role == "judge_proposition":
                    reply = "Mock."
                else:
                    reply = f"[Mock-{role}-{number}]"
                error = judge_format_error(role, reply)
                if len(reply.split()) > limit:
                    error = f"Your reply exceeded {limit} words. Aim for {max(1, limit * 2 // 3)} words, retaining the required response format."
                if not error:
                    break
                if attempt == 3:
                    raise ValueError(f"{role} failed in round {number}: {error}")
                message = json.dumps({"claim_and_reasoning": claim, "context": context,
                                      "arguments": arguments, "format_correction": error})
            turns.append({"role": role, "input": message, "output": reply})
            if role == "judge_proposition":
                record["revised_proposition"] = reply
            return reply

        round_record = {"number": number, "starting_claim": claim, "turns": turns}
        if summarize_at_end:
            summary = FORMATS[args.format].run_exchange(ask, history, number == args.rounds)
            if summary is not None:
                record["final_summary"] = summary
        else:
            claim = FORMATS[args.format].run_round(ask)
            round_record["revision"] = claim
            record["final_revision"] = claim
        record["rounds"].append(round_record)
    directory = ROOT / "runs"
    directory.mkdir(exist_ok=True)
    name = transcript_stem(started, topic_name, record)
    path = directory / (name + ".json")
    duplicate = 1
    while True:
        try:
            out = path.open("x", encoding="utf-8")
            break
        except FileExistsError:
            duplicate += 1
            path = directory / f"{name}_{duplicate}.json"
    with out:
        json.dump(record, out, indent=2, ensure_ascii=False)
    path.with_suffix(".md").write_text(render(record), encoding="utf-8")
    return path


def main():
    parser = argparse.ArgumentParser(description="Run a PHIL166AI debate.")
    parser.add_argument("--format", choices=FORMATS, default="sequential")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--topic", type=Path, default=ROOT / "topics/ai_belief.json")
    source.add_argument("--from-run", type=Path, help="Debate a prior run's revised proposition.")
    parser.add_argument("--rounds", type=int, default=2)
    parser.add_argument("--iterations", type=int, default=1, help="Number of successive debates.")
    parser.add_argument("--max-words", type=int, default=WORD_LIMIT, help="Default per-turn word cap.")
    for role in ("advocate", "critic", "judge"):
        parser.add_argument(f"--{role}-words", type=int, help=f"Override the {role}'s word cap.")
    parser.add_argument("--live", action="store_true", help="Send requests to each role's provider.")
    args = parser.parse_args()
    if args.rounds < 1:
        parser.error("--rounds must be positive")
    if args.iterations < 1 or any(n is not None and n < 1 for n in (
            args.max_words, args.advocate_words, args.critic_words, args.judge_words)):
        parser.error("Iteration counts and word limits must be positive.")
    if args.iterations > 1 and args.format != "moderated":
        parser.error("Multiple iterations require the moderated format's revised proposition.")
    try:
        for iteration in range(1, args.iterations + 1):
            args.from_run = run(args, iteration)
            print(args.from_run, flush=True)
    except (ValueError, RuntimeError, OSError, KeyError, IndexError) as error:
        parser.exit(1, f"Debate failed: {error}\n")


if __name__ == "__main__":
    main()
