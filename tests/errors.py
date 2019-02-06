# Test the VM-generated error codes (HALT).
#
# (c) Reuben Thomas 1995-2019
#
# The package is distributed under the GNU Public License version 3, or,
# at your option, any later version.
#
# THIS PROGRAM IS PROVIDED AS IS, WITH NO WARRANTY. USE IS AT THE USER‘S
# RISK.

from smite import *
size = 4096
VM = State(size)
VM.globalize(globals())


# Test results and data
answer = 42
result = [answer, -10, -9, -9, -23, -256]
invalid_address = size * word_size + 1000
test = []

print("Test 1: PC = {}".format(VM.here))
# Test arbitrary halt code
test.append(VM.here)
number(answer)
action(HALT)

print("Test 2: PC = {}".format(VM.here))
test.append(VM.here)
number(1)
number(0)
action(DIVMOD)
number(1)
action(POP)

print("Test 3: PC = {}".format(VM.here))
# Allow execution to run off the end of a memory area
# (test 2 has set MEMORY - 1 to all zeroes)
test.append(VM.here)
number(MEMORY.get() - 1)
action(BRANCH)

print("Test 4: PC = {}".format(VM.here))
# Fetch from an invalid address
test.append(VM.here)
number(invalid_address)
action(LOAD)

print("Test 5: PC = {}".format(VM.here))
test.append(VM.here)
number(1)
action(LOAD)

print("Test 6: PC = {}".format(VM.here))
# Test invalid opcode
test.append(VM.here)
action(UNDEFINED)


assert(len(test) == len(result))


# Test
error = 0
for i in range(len(test)):
    SDEPTH.set(0)    # reset stack pointer

    print("Test {}".format(i + 1))
    PC.set(test[i])
    res = run()

    if result[i] != res:
         print("Error in exceptions tests: test {} failed; PC = {}".format(i + 1, PC.get()))
         print("Return code is {}; should be {}".format(res, result[i]))
         error += 1
    print()

if error != 0:
    sys.exit(error)

print("Exceptions tests ran OK")