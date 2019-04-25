# VM definition
#
# (c) SMite authors 1994-2019
#
# The package is distributed under the MIT/X11 License.
#
# THIS PROGRAM IS PROVIDED AS IS, WITH NO WARRANTY. USE IS AT THE USER’S
# RISK.

from enum import Enum, IntEnum, unique
from .instruction_gen import Instruction

class Register:
    '''VM register descriptor.'''
    def __init__(self, ty=None, uty=None, read_only=False):
        self.ty = ty or "smite_UWORD"
        self.uty = uty or self.ty
        self.read_only = read_only

@unique
class Registers(Enum):
    '''VM registers.'''
    PC = Register()
    I = Register()
    BAD = Register()
    STACK_DEPTH = Register()

@unique
class Instructions(Enum):
    '''VM instruction instructions.'''
    NEXT = Instruction(0x00, [], [], '''\
        NEXT;'''
    )

    BRANCH = Instruction(0x01, ['addr'], [], '''\
        S->PC = (smite_UWORD)addr;
        NEXT;
    ''')

    BRANCHZ = Instruction(0x02, ['flag', 'addr'], [], '''\
        if (flag == 0) {
            S->PC = (smite_UWORD)addr;
            NEXT;
        }
    ''')

    CALL = Instruction(0x03, ['addr'], ['ret_addr'], '''\
        ret_addr = S->PC;
        S->PC = (smite_UWORD)addr;
        NEXT;
    ''')

    POP = Instruction(0x04, ['ITEMS:', 'COUNT'], [], '')

    DUP = Instruction(0x05, ['x', 'ITEMS:', 'COUNT'], ['x', 'ITEMS:', 'x'], '')

    SWAP = Instruction(0x06, ['x', 'ITEMS', 'y', 'COUNT'], ['y', 'ITEMS', 'x'], '')

    NOT = Instruction(0x08, ['x'], ['r'], '''\
        r = ~x;
    ''')

    AND = Instruction(0x09, ['x', 'y'], ['r'], '''\
        r = x & y;
    ''')

    OR = Instruction(0x0a, ['x', 'y'], ['r'], '''\
        r = x | y;
    ''')

    XOR = Instruction(0x0b, ['x', 'y'], ['r'], '''\
        r = x ^ y;
    ''')

    LSHIFT = Instruction(0x0c, ['x', 'n'], ['r'], '''\
        r = n < (smite_WORD)smite_word_bit ? x << n : 0;
    ''')

    RSHIFT = Instruction(0x0d, ['x', 'n'], ['r'], '''\
        r = n < (smite_WORD)smite_word_bit ? (smite_WORD)((smite_UWORD)x >> n) : 0;
    ''')

    ARSHIFT = Instruction(0x0e, ['x', 'n'], ['r'], '''\
        r = ARSHIFT(x, n);
    ''')

    SIGN_EXTEND = Instruction(0x0f, ['n1', 'size'], ['n2'], '''\
        n2 = n1 << (WORD_BYTES - (1 << size)) * smite_BYTE_BIT;
        n2 = ARSHIFT(n2, (WORD_BYTES - (1 << size)) * smite_BYTE_BIT);
    ''')

    EQ = Instruction(0x10, ['a', 'b'], ['flag'], '''\
        flag = a == b;
    ''')

    LT = Instruction(0x11, ['a', 'b'], ['flag'], '''\
        flag = a < b;
    ''')

    ULT = Instruction(0x12, ['a', 'b'], ['flag'], '''\
        flag = (smite_UWORD)a < (smite_UWORD)b;
    ''')

    NEGATE = Instruction(0x13, ['a'], ['r'], '''\
        r = -a;
    ''')

    ADD = Instruction(0x14, ['a', 'b'], ['r'], '''\
        r = a + b;
    ''')

    MUL = Instruction(0x15, ['a', 'b'], ['r'], '''\
        r = a * b;
    ''')

    DIVMOD = Instruction(0x16, ['a', 'b'], ['q', 'r'], '''\
        if (b == 0)
          RAISE(SMITE_ERR_DIVISION_BY_ZERO);
        q = a / b;
        r = a % b;
    ''')

    UDIVMOD = Instruction(0x17, ['a', 'b'], ['q', 'r'], '''\
        if (b == 0)
          RAISE(SMITE_ERR_DIVISION_BY_ZERO);
        q = (smite_WORD)((smite_UWORD)a / (smite_UWORD)b);
        r = (smite_WORD)((smite_UWORD)a % (smite_UWORD)b);
    ''')

    LOAD = Instruction(0x18, ['addr', 'size'], ['x'], '''\
        int ret = load(S, addr, size, &x);
        if (ret != 0)
            RAISE(ret);
    ''')

    STORE = Instruction(0x19, ['x', 'addr', 'size'], [], '''\
        int ret = store(S, addr, size, x);
        if (ret != 0)
            RAISE(ret);
    ''')

    LIT = Instruction(0x1a, [], ['n'], '''\
        int ret = load(S, S->PC, smite_SIZE_WORD, &n);
        if (ret != 0)
            RAISE(ret);
        S->PC += WORD_BYTES;
    ''')

    LIT_PC_REL = Instruction(0x1b, [], ['n'], '''\
        int ret = load(S, S->PC, smite_SIZE_WORD, &n);
        if (ret != 0)
            RAISE(ret);
        n += S->PC;
        S->PC += WORD_BYTES;
    ''')

    LIT_0 = Instruction(0x1c, [], ['zero'], '''\
        zero = 0;
    ''')

    LIT_1 = Instruction(0x1d, [], ['one'], '''\
        one = 1;
    ''')

    EXT = Instruction(0x1e, None, None, '''\
        smite_ext(S);
    ''')

    HALT = Instruction(0x1f, [], [], '''\
        RAISE(SMITE_ERR_HALT);
    ''')
