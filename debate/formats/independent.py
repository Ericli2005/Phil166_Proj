"""The advocate and critic form their arguments independently."""
def run_round(ask):
    case = ask("advocate")
    objection = ask("critic")
    return ask("judge", advocate=case, critic=objection)
