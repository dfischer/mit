# Test the stack operators.
#
# (c) Reuben Thomas 1994-2019
#
# The package is distributed under the GNU Public License version 3, or,
# at your option, any later version.
#
# THIS PROGRAM IS PROVIDED AS IS, WITH NO WARRANTY. USE IS AT THE USER’S
# RISK.

from smite import *
VM = State()
VM.globalize(globals())


# Test results
correct = [
    [],
    [1],
    [1, 2],
    [1, 2, 3],
    [1, 2, 3, 0],
    [1, 2, 3, 3],
    [1, 2, 3, 3, 1],
    [1, 2, 3],
    [1, 2, 3, 1],
    [1, 3, 2],
    [1, 3, 2, 1],
    [1, 3, 2, 3],
    [1, 3, 2, 3, 1],
    [1, 3, 3, 2],
    [1, 3, 3, 2, 1],
    [1, 3, 3],
    [1, 3, 3, 0],
    [1, 3, 3, 3],
    [1, 3, 3, 3, 4],
    [],
    [2],
    [2, 1],
    [2, 1, 0],
    [2, 1, 1],
    [2, 1, 2],
    [2, 1, 2, 0],
    [2, 1, 2, 2],
    [2, 1, 2, 2, 0],
    [2, 1, 2, 2, 2],
    [2, 1, 2, 2, 2, 3],
    [2, 2, 2, 2, 1],
    [2, 2, 2, 2, 1, -2],
    [2, 2, 1, 2, 2],
]

# Test code
number(1)
number(2)
number(3)
number(0)
action(DUP)
number(1)
action(POP)
number(1)
action(SWAP)
number(1)
action(DUP)
number(1)
action(SWAP)
number(1)
action(POP)
number(0)
action(DUP)
action(GET_STACK_DEPTH)
action(POP)
number(2)
number(1)
number(0)
action(DUP)
action(DUP)
number(0)
action(DUP)
number(0)
action(DUP)
number(3)
action(ROTATE)
number(-2)
action(ROTATE)

# Test
for i in range(len(correct)):
    print("Data stack: {}".format(S))
    print("Correct stack: {}\n".format(correct[i]))
    if str(correct[i]) != str(S):
        print("Error in stack tests: PC = {:#x}".format(PC.get()))
        sys.exit(1)
    step()
    print("I = {}".format(disassemble_instruction(ITYPE.get(), I.get())))

print("Stack tests ran OK")
