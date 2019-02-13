#!/usr/bin/python3
'''
Process an instruction trace, and build a specialised interpreter. Unfinished.

For the purposes of this program, a trace is an (ASCII) text file with one "event" per line. Events are therefore newline-free byte strings, and distinct byte strings are distinct events.

The abstraction of events is compatible with traces recorded using "smite --trace". [TODO: Change "smite --trace" behaviour so the values of number literals are suppressed.]

When finished, the program will compute the control-flow structure of an interpreter specialised for the instruction trace. This can be used to compile a version of smite that is fast for programs similar to the instruction trace. (For other programs it is correct and no slower than an unspecialised smite).
'''

import sys, pickle

from events import Event, ALL_EVENTS, EVENT_NAMES

if len(sys.argv) != 2:
    print("Usage: language.py <predictor-filename>", file=sys.stderr)
    sys.exit(1)
predictor_filename = sys.argv[1]

with open(predictor_filename, 'rb') as f:
    # [{event_name: (new_state, count)]
    predictor = pickle.load(f)

# Find all paths through the predictor.

print("Finding paths")

# Total visit count of each state.
# [int]
state_counts = [
    sum(count for _, count in transitions.values())
    for transitions in predictor
]

# Estimated probability distribution over events for each state.
# [{event: (new_state, probability)}]
state_probabilities = [
    {
        event: (
            new_state,
            float(count + 1) / float(state_counts[state] + 64),
        )
        for event, (new_state, count) in transitions.items()
    }
    for state, transitions in enumerate(predictor)
]

# tuple of events (str) -> estimated_count (float)
language = {}

def walk(path, distribution):
    '''
     - path - tuple of event (str).
     - distribution - list of estimated frequency (float).
    '''
    # Check for statistical irrelevance (but keep singleton paths).
    estimated_count = sum(distribution)
    if len(path) > 1 and estimated_count < 300000.: return
    # Okay, we'll keep it.
    language[path] = estimated_count
    # Check for repetition.
    for n in range(1, len(path)//2+1):
        if path[-n:]==path[-2*n:-n]: return
    # For all (state, action) pairs, propagate count to the successor state.
    successors = {event.name: [0.] * len(predictor) for event in ALL_EVENTS}
    for state, estimated_count in enumerate(distribution):
        if estimated_count > 1.:
            probabilities = state_probabilities[state]
            for event, (new_state, probability) in probabilities.items():
                additional_count = estimated_count * probability
                if additional_count >= 1.:
                    successors[event][new_state] += additional_count
    # Recurse down the tree.
    for event, new_distribution in successors.items():
        new_path = path + (event,)
        walk(new_path, new_distribution)

walk((), [float(x) for x in state_counts])

# Sanity checks.

for event in ALL_EVENTS:
    assert (event.name,) in language

for path in language:
    assert path[1:] in language
    assert path[:-1] in language

# For each path, sort the possible next events by probability (decreasing).

print("Choosing guesses")

def successor(path, event):
    # Appends one event to `path` then removes the repeated suffix, if any.
    path += (event.name,)
    for n in range(1, len(path)//2 + 1):
        if path[-n:]==path[-2*n:-n]: return path[:-n]
    return path

# path -> [Event]
path_guesses = {
    path: sorted(
        [
            event
            for event in ALL_EVENTS
            if path + (event.name,) in language
        ],
        key=lambda e: language[successor(path, e)],
        reverse=True,
    )
    for path in language
}

# Generate state space of (path × rejects) with flood fill.

print("Generating control flow graph")

states = [] # List of (path, rejects)
state_index = {} # Inverse of `states`.

# For each state in `states`, there is a transition in `transitions`.
# It can be:
#  - None - return;
#  - int g - goto g;
#  - (Event e, int c, int w) - if (next==e) { e; goto c; } else goto w;
transitions = []

def enqueue(path, rejects):
    '''
    Adds a state if it has not been seen before.
     - path - tuple of event name.
     - rejects - frozenset of event name.
    '''
    state = (path, rejects)
    if state not in state_index:
        state_index[state] = len(state_index)
        states.append(state)
    return state_index[state]

assert enqueue((), frozenset()) == 0 # Root state.

# The work queue is the suffix of `states` that does not yet have transitions.
while len(transitions) < len(states):
    path, rejects = states[len(transitions)]
    for guess in path_guesses[path]:
        if guess.name not in rejects:
            # We have a guess.
            transitions.append((
                guess,
                enqueue(successor(path, guess), frozenset()),
                enqueue(path, rejects.union({guess.name})),
            ))
            break
    else:
        # There is no good guess.
        if path:
            new_path = path[1:]
            transitions.append(enqueue(new_path, rejects))
        else:
            # We have eliminated all possible events.
            # It's an illegal instruction.
            transitions.append(None)

assert len(states) == len(state_index) == len(transitions)

# Tension branches.

print("Tensioning branches")

# We only need labels for the states in which we make a guess.
label_map = {} # state -> label
for state, transition in enumerate(transitions):
    if isinstance(transition, tuple):
        label_map[state] = len(label_map)

def short_circuit(state):
    # Follows gotos, and maps `state` to a label or `None`.
    while isinstance(transitions[state], int):
        state = transitions[state]
    return label_map.get(state)

# List of (guess, label or None, label or None).
labels = [
    (guess.name, short_circuit(c), short_circuit(w))
    for guess, c, w in [
        t
        for t in transitions
        if isinstance(t, tuple)
    ]
]

assert len(label_map) == len(labels)

# Dump to a file.

out_filename = '/tmp/labels.pickle'
with open(out_filename, 'wb') as f:
    # [(event_name (str), if_correct (int?), if_wrong (int?))]
    pickle.dump(labels, file=f)
print('Wrote {}'.format(out_filename))