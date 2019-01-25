// Encode and decode instructions.
//
// (c) Reuben Thomas 2018
//
// The package is distributed under the GNU Public License version 3, or,
// at your option, any later version.
//
// THIS PROGRAM IS PROVIDED AS IS, WITH NO WARRANTY. USE IS AT THE USER‘S
// RISK.

#include "config.h"

#include <stddef.h>
#include <unistd.h>

#include "smite.h"
#include "aux.h"
#include "opcodes.h"


#define _ENCODE_INSTRUCTION(NAME, TYPE, HANDLE, STORE)                  \
    {                                                                   \
        size_t len = 0;                                                 \
        smite_BYTE b;                                                         \
        int exception;                                                  \
                                                                        \
        /* Continuation bytes */                                        \
        for (int bits = smite_find_msbit(v) + 1; bits > INSTRUCTION_CHUNK_BIT; bits -= INSTRUCTION_CHUNK_BIT) { \
            b = (smite_BYTE)(v & INSTRUCTION_CHUNK_MASK) | INSTRUCTION_CONTINUATION_BIT; \
            if ((exception = STORE(b)) != 0)                            \
                return (ptrdiff_t)exception;                            \
            len++;                                                      \
            v = ARSHIFT(v, INSTRUCTION_CHUNK_BIT);                      \
        }                                                               \
                                                                        \
        /* Set action bit if needed */                                  \
        if (type == INSTRUCTION_ACTION)                                 \
            v |= INSTRUCTION_ACTION_BIT;                                \
                                                                        \
        /* Last (or only) byte */                                       \
        b = (smite_BYTE)v;                                                    \
        if ((exception = STORE(b)))                                     \
            return (ptrdiff_t)exception;                                \
        len++;                                                          \
                                                                        \
        return len;                                                     \
    }

#define ENCODE_INSTRUCTION(NAME, TYPE, HANDLE, STORE)                   \
    ptrdiff_t NAME(TYPE HANDLE, enum instruction_type type, smite_WORD v)     \
    _ENCODE_INSTRUCTION(NAME, TYPE, HANDLE, STORE)

#define STATEFUL_ENCODE_INSTRUCTION(NAME, TYPE, HANDLE, STORE)          \
    ptrdiff_t NAME(smite_state *S, TYPE HANDLE, enum instruction_type type, smite_WORD v) \
    _ENCODE_INSTRUCTION(NAME, TYPE, HANDLE, STORE)

#define STORE_FILE(b) (-(write(fd, &b, 1) != 1))
ENCODE_INSTRUCTION(smite_encode_instruction_file, int, fd, STORE_FILE)

#define STORE_VIRTUAL(b) (smite_store_byte(S, addr++, (b)))
STATEFUL_ENCODE_INSTRUCTION(smite_encode_instruction, smite_UWORD, addr, STORE_VIRTUAL)

#define _DECODE_INSTRUCTION(NAME, TYPE, HANDLE, LOAD)                   \
    {                                                                   \
        unsigned bits = 0;                                              \
        smite_WORD n = 0;                                               \
        smite_BYTE b;                                                   \
        int exception;                                                  \
        int type = INSTRUCTION_NUMBER;                                  \
                                                                        \
        /* Continuation bytes */                                        \
        for (exception = LOAD(b);                                       \
             exception == 0 && bits <= smite_word_bit - INSTRUCTION_CHUNK_BIT && \
                 (b & ~INSTRUCTION_CHUNK_MASK) == INSTRUCTION_CONTINUATION_BIT; \
             exception = LOAD(b)) {                                     \
            n |= (smite_WORD)(b & INSTRUCTION_CHUNK_MASK) << bits;      \
            bits += INSTRUCTION_CHUNK_BIT;                              \
        }                                                               \
        if (bits > smite_word_bit)                                      \
            return -1;                                                  \
        if (exception != 0)                                             \
            return exception;                                           \
                                                                        \
        /* Check for action opcode */                                   \
        if ((b & ~INSTRUCTION_CHUNK_MASK) == INSTRUCTION_ACTION_BIT) {  \
            type = INSTRUCTION_ACTION;                                  \
            b &= INSTRUCTION_CHUNK_MASK;                                \
        }  else if (smite_word_bit - bits < smite_byte_bit)             \
            b &= (1 << (smite_word_bit - bits)) - 1;                    \
                                                                        \
        /* Final (or only) byte */                                      \
        n |= (smite_UWORD)b << bits;                                    \
        bits += smite_byte_bit;                                         \
        if (type == INSTRUCTION_NUMBER && bits < smite_word_bit)        \
            n = ARSHIFT((smite_UWORD)n << (smite_word_bit - bits), smite_word_bit - bits); \
        *val = n;                                                       \
        return type;                                                    \
    }

#define DECODE_INSTRUCTION(NAME, TYPE, HANDLE, LOAD)                    \
    int NAME(TYPE HANDLE, smite_WORD *val)                              \
    _DECODE_INSTRUCTION(NAME, TYPE, HANDLE, LOAD)

#define STATEFUL_DECODE_INSTRUCTION(NAME, TYPE, HANDLE, LOAD)           \
    int NAME(smite_state *S, TYPE HANDLE, smite_WORD *val)              \
    _DECODE_INSTRUCTION(NAME, TYPE, HANDLE, LOAD)

#define LOAD_FILE(b) (-(read(fd, &b, 1) != 1))
DECODE_INSTRUCTION(smite_decode_instruction_file, int, fd, LOAD_FILE)

#define LOAD_VIRTUAL(b) (smite_load_byte(S, (*addr)++, &(b)))
STATEFUL_DECODE_INSTRUCTION(smite_decode_instruction, smite_UWORD *, addr, LOAD_VIRTUAL)
