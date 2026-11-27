"""Render a recorded debate as a Markdown dialogue."""
import argparse
import json
from pathlib import Path


def render(record):
    topic = record["topic"]
    lines = [f"# {topic['claim']}", "", f"{record['format']} · {record['mode']}", ""]
    if topic.get("context"):
        lines.extend([topic["context"], ""])
    for exchange in record["rounds"]:
        lines.extend([f"## Round {exchange['number']}", ""])
        for turn in exchange["turns"]:
            label = turn["role"].capitalize()
            if turn["role"] == "judge_feedback":
                label = "Judge feedback"
            if turn["role"] == "judge_proposition":
                label = "Judge’s revised proposition"
            if label == "Judge" and "final_summary" in record:
                label = "Judge’s final summary"
            lines.extend([f"### {label}", "", turn["output"], ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transcript", type=Path, help="Run JSON to render")
    args = parser.parse_args()
    target = args.transcript.with_suffix(".md")
    if target == args.transcript:
        parser.error("Supply the JSON transcript.")
    record = json.loads(args.transcript.read_text(encoding="utf-8"))
    target.write_text(render(record), encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()
