"""Invite optional judge feedback after each public exchange."""
from .final_summary import debate_pair


def run_exchange(ask, history, last):
    debate_pair(ask, history)
    if not last:
        feedback = ask("judge_feedback", transcript=history)
        if feedback != "PASS":
            history.append({"role": "judge_feedback", "output": feedback})
        return
    summary = ask("judge", transcript=history)
    history.append({"role": "judge", "output": summary})
    ask("judge_proposition", transcript=history)
    return summary
