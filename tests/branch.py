# Test the branch instructions and LIT_PC_REL. Also uses instructions tested
# by earlier tests.
# See errors.py for address error handling tests.
# The test program contains an infinite loop, but this is only executed
# once.
#
# (c) SMite authors 1994-2019
#
# The package is distributed under the MIT/X11 License.
#
# THIS PROGRAM IS PROVIDED AS IS, WITH NO WARRANTY. USE IS AT THE USER’S
# RISK.

from smite import *
VM = State(4096)
VM.globalize(globals())


# Test results
correct = []

# Code
goto(0)
correct.append(assembler.effective_pc())
lit(96)
correct.append(assembler.effective_pc())
ass(BRANCH)

goto(96)
correct.append(assembler.effective_pc())
lit_pc_rel(48)
correct.append(assembler.effective_pc())
ass(BRANCH)

goto(48)
correct.append(assembler.effective_pc())
lit_pc_rel(10000)
correct.append(assembler.effective_pc())
ass(BRANCH)

goto(10000)
correct.append(assembler.effective_pc())
lit(1)
correct.append(assembler.effective_pc())
lit(9999)
correct.append(assembler.effective_pc())
ass(BRANCHZ)
correct.append(assembler.effective_pc())
lit(1)
correct.append(assembler.effective_pc())
lit(0)
correct.append(assembler.effective_pc())
ass(BRANCHZ)
correct.append(assembler.effective_pc())
lit(0)
correct.append(assembler.effective_pc())
lit_pc_rel(11000)
correct.append(assembler.effective_pc())
ass(BRANCHZ)

goto(11000)
correct.append(assembler.effective_pc())
lit(0)
correct.append(assembler.effective_pc())
lit_pc_rel(11000 + word_bytes * 8)
correct.append(assembler.effective_pc())
ass(BRANCHZ)

goto(11000 + word_bytes * 8)
correct.append(assembler.effective_pc())
lit_pc_rel(600)
correct.append(assembler.effective_pc())
ass(CALL)

goto(600)
correct.append(assembler.effective_pc())
lit_pc_rel(200)
correct.append(assembler.effective_pc())
ass(CALL)

goto(200)
correct.append(assembler.effective_pc())
lit(304)
correct.append(assembler.effective_pc())
ass(CALL)

goto(304)
correct.append(assembler.effective_pc())
ass(BRANCH)

goto(200 + word_bytes * 2)
correct.append(assembler.effective_pc())
ass(BRANCH)

goto(600 + word_bytes * 2)
correct.append(assembler.effective_pc())
lit(64)
correct.append(assembler.effective_pc())
lit(24)
correct.append(assembler.effective_pc())
lit(0)
correct.append(assembler.effective_pc())
ass(SWAP)
correct.append(assembler.effective_pc())
lit(1)
correct.append(assembler.effective_pc())
ass(DUP)
correct.append(assembler.effective_pc())
lit(size_word)
correct.append(assembler.effective_pc())
ass(STORE)
correct.append(assembler.effective_pc())
lit(size_word)
correct.append(assembler.effective_pc())
ass(LOAD)
correct.append(assembler.effective_pc())
ass(CALL)
correct.append(64 + word_bytes)

# Test
for i, pc in enumerate(correct):
    step(trace=True)
    print("Instruction {}: PC = {} should be {}\n".format(i, PC.get(), pc))
    if pc != PC.get():
        print("Error in branch tests: PC = {:#x}".format(PC.get()))
        sys.exit(1)

print("Branch tests ran OK")
