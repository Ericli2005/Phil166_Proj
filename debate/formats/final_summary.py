"""Alternate speakers with full public history, then summarize once."""


def debate_pair(ask, history):
    for role in ("advocate", "critic"):
        reply = ask(role, transcript=history)
        history.append({"role": role, "output": reply})


def run_exchange(ask, history, last):
    debate_pair(ask, history)
    if last:
        return ask("judge", transcript=history)
