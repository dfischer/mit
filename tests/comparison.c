// Test the comparison operators. We only test simple cases here, assuming
// that the C compiler's comparison routines will work for other cases.
//
// (c) Reuben Thomas 1994-2018
//
// The package is distributed under the GNU Public License version 3, or,
// at your option, any later version.
//
// THIS PROGRAM IS PROVIDED AS IS, WITH NO WARRANTY. USE IS AT THE USER‘S
// RISK.

#include "tests.h"


int exception = 0;
WORD temp;

WORD correct[] = { 0, 1, 0, 1, 1, 0, 0, 1, 0, 0};


static void stack1(void)
{
    SP = S0;	// empty the stack

    PUSH(-4); PUSH(3);
    PUSH(2); PUSH(2);
    PUSH(1); PUSH(3);
    PUSH(3); PUSH(1);
}

static void stack2(void)
{
    SP = S0;	// empty the stack

    PUSH(1); PUSH(-1);
    PUSH(237); PUSH(237);
}

static void step(unsigned start, unsigned end)
{
    if (end > start)
        for (unsigned i = start; i < end; i++) {
            single_step();
            printf("I = %s\n", disass(INSTRUCTION_ACTION, I));
            printf("Result: %d; correct result: %d\n\n", LOAD_WORD(SP),
                   correct[i]);
            if (correct[i] != LOAD_WORD(SP)) {
                printf("Error in comparison tests: PC = %"PRIu32"\n", PC);
                exit(1);
            }
            (void)POP;	// drop result of comparison
        }
}

int main(void)
{
    init((WORD *)malloc(1024), 256);

    start_ass(PC);
    ass_action(O_LT); ass_action(O_LT); ass_action(O_LT); ass_action(O_LT);
    ass_action(O_EQ); ass_action(O_EQ);
    ass_action(O_ULT); ass_action(O_ULT); ass_action(O_ULT); ass_action(O_ULT);

    stack1();       // set up the stack with four standard pairs to compare
    step(0, 4);     // do the < tests
    stack2();       // set up the stack with two standard pairs to compare
    step(4, 6);     // do the = tests
    stack1();       // set up the stack with four standard pairs to compare
    step(6, 10);    // do the U< tests

    assert(exception == 0);
    printf("Comparison tests ran OK\n");
    return 0;
}
