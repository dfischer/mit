'''
Library for reading and processing profile files.

(c) 2019-2020 Mit authors

The package is distributed under the MIT/X11 License.

THIS PROGRAM IS PROVIDED AS IS, WITH NO WARRANTY. USE IS AT THE USER’S
RISK.
'''

import json, random

from spec import Instruction
from path import Path


class Label:
    '''
    Represents a label of the interpreter that we profiled.
     - index - int - the index of this Label in `profile`.
     - path - Path - the canonical path to this Label.
     - guess - Instruction - the guessed continuation.
     - correct_state - int - the index of the Label to jump to if `guess` is
       correct, or `-1` for the fallback label.
     - wrong_state - int - the index of the Label to jump to if `guess` is
       wrong, or `-1` for the fallback label.
     - correct_count - int - the number of times `guess` was correct.
     - wrong_count - int - the number of times `guess` was wrong.
     - total_count - int - `correct_count + wrong_count`.
    '''
    def __init__(
        self,
        index,
        path,
        guess,
        correct_state,
        wrong_state,
        correct_count,
        wrong_count,
    ):
        assert isinstance(path, Path)
        assert isinstance(guess, Instruction)
        self.index = index
        self.path = path
        self.guess = guess
        self.correct_state = correct_state
        self.wrong_state = wrong_state
        self.correct_count = correct_count
        self.wrong_count = wrong_count
        self.total_count = correct_count + wrong_count

    def __repr__(self):
        return 'Label({}, {!r}, {!r}, {}, {}, {}, {})'.format(
            self.index,
            self.path,
            self.guess,
            self.correct_state,
            self.wrong_state,
            self.correct_count,
            self.wrong_count,
        )


def load(filename):
    '''
    Load a profile data file, and initialize `profile` and `ROOT_LABEL`.
    '''
    global profile, ROOT_LABEL
    with open(filename) as h:
        profile = [
            Label(
                index,
                Path(tuple(
                    Instruction[name]
                    for name in profile['path'].split()
                )),
                Instruction[profile['guess']],
                profile['correct_state'],
                profile['wrong_state'],
                profile['correct_count'],
                profile['wrong_count'],
            )
            for index, profile in enumerate(json.load(h))
        ]
    ROOT_LABEL = get_label(0) if len(profile) > 0 else None


def get_label(index):
    if index == -1:
        return None
    else:
        return profile[index]


def random_trace():
    label = ROOT_LABEL
    while True:
        if label is None:
            # Fallback interpreter is modelled as uniformly random.
            yield random.choice(list(Instruction))
            label = ROOT_LABEL
        elif random.randrange(label.total_count) < label.correct_count:
            # Model a correct guess.
            yield label.guess
            label = get_label(label.correct_state)
        else:
            # Model a wrong guess.
            label = get_label(label.wrong_state)


def counts():
    '''
    Returns a dict from Instruction to count.
    '''
    # Read trace, computing opcode counts
    counts = {instruction: 0 for instruction in Instruction}
    for label in profile:
        counts[label.guess] += label.correct_count
    return counts
