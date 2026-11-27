"""The critic sees the advocate's case."""
def run_round(ask):
    case = ask("advocate")
    objection = ask("critic", advocate=case)
    return ask("judge", advocate=case, critic=objection)
