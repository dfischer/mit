// Declaration of mit_state.
//
// (c) Mit authors 2019-2020
//
// The package is distributed under the MIT/X11 License.
//
// THIS PROGRAM IS PROVIDED AS IS, WITH NO WARRANTY. USE IS AT THE USER’S
// RISK.

#ifndef MIT_STATE
#define MIT_STATE


struct mit_state {
#define R(reg, type, return_type) type reg;
#include "mit/registers.h"
#undef R
    mit_fn *run_fn;
    void *extra_state;
};

#endif
