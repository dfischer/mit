# Test the VM-generated error codes.
#
# (c) Mit authors 1995-2020
#
# The package is distributed under the MIT/X11 License.
#
# THIS PROGRAM IS PROVIDED AS IS, WITH NO WARRANTY. USE IS AT THE USER’S
# RISK.

import sys

from mit import *
from mit.binding import libmit, libmitfeatures


VM = State(memory_words=4096, stack_words=3)
assembler = Assembler(VM)
lit = assembler.lit
label = assembler.label
ass = assembler.instruction
vars().update(Instruction.__members__)
UNDEFINED = 1 + max(Instruction)

# Test results and data
result = []
invalid_address = VM.M.addr + len(VM.M) + 1000
test = []
test_pc = []

test.append('Try to divide by zero')
test_pc.append(label())
result.append(MitErrorCode.DIVISION_BY_ZERO)
print('Test "{}": pc = {}'.format(test[-1], test_pc[-1]))
lit(1)
lit(0)
ass(DIVMOD)

test.append('Try to read from an invalid stack location')
test_pc.append(label())
result.append(MitErrorCode.INVALID_STACK_READ)
print('Test "{}": pc = {}'.format(test[-1], test_pc[-1]))
ass(DUP)

test.append('Try to load from unaligned address')
test_pc.append(label())
result.append(MitErrorCode.UNALIGNED_ADDRESS)
print('Test "{}": pc = {}'.format(test[-1], test_pc[-1]))
lit(VM.M.addr + 1)
ass(LOAD)

if UNDEFINED < (1 << opcode_bit):
    test.append('Try to execute invalid opcode')
    test_pc.append(label())
    result.append(MitErrorCode.INVALID_OPCODE)
    print('Test "{}": pc = {}'.format(test[-1], test_pc[-1]))
    ass(UNDEFINED)

# Tests
assert(len(test_pc) == len(result))

def step_trace():
    while True:
        VM.trace()

error = 0
def do_tests(run_fn):
    global error
    for i, pc_value in enumerate(test_pc):
        VM.stack_depth = 0 # reset stack pointer

        print('Test "{}"'.format(test[i]))
        VM.ir = 0
        VM.pc = pc_value
        res = 0
        try:
            run_fn()
        except VMError as e:
            res = e.args[0]

        if result[i] != res:
             print('Error in errors tests: test "{}" failed; pc = {}'.format(test[i], VM.pc))
             print("Error code is {}; should be {}".format(res, result[i]))
             error += 1
        print()

print('''
Running tests with single_step
''')
do_tests(step_trace)
print("Running tests with run (optimized)")
do_tests(VM.run)

test.append("Try to write to an invalid stack location (can't do this with virtual code)")
try:
    libmit.mit_store_stack(VM.state, 4, 0)
    ret = 0
except VMError as e:
    ret = e.args[0]
if ret != MitErrorCode.INVALID_STACK_WRITE:
    print('Error in errors test: test "{}" failed; result is {}, should be {}'.format(
        test[-1], ret, MitErrorCode.INVALID_STACK_WRITE,
    ))
    error += 1

if error != 0:
    sys.exit(error)

print("Errors tests ran OK")
