'''
Mit disassembler.

(c) Mit authors 2019-2020

The package is distributed under the MIT/X11 License.

THIS PROGRAM IS PROVIDED AS IS, WITH NO WARRANTY. USE IS AT THE USER’S
RISK.
'''

from .binding import (
    hex0x_word_width, is_aligned, sign_extend, uword_max, word_bytes
)
from .enums import Instructions, ExtraInstructions, TERMINAL_OPCODES
from .enums import Instructions as I

mnemonic = {
    instruction.value: instruction.name
    for instruction in Instructions
}
extra_mnemonic = {
    instruction.value: instruction.name
    for instruction in ExtraInstructions
}


class Disassembler:
    '''
    Represents the state of a disassembler. This class simulates the `pc` and
    `ir` registers. When it reaches a terminal instruction, it continues at
    the next word. The `goto()` method sets a new disassembly address. Each
    call to `__next__()` dissassembles one instruction.

    Public fields:
     - pc - the value of the simulated `pc` register.
     - ir - the value of the simulated `ir` register.
     - end - the `pc` value at which to stop.
    '''
    def __init__(self, state, pc=None, length=None, end=None, ir=0):
        '''
        Disassembles code from the memory of `state`. `pc` and `ir`
        default to the current `pc` and `ir` values of `state`.
        `length` is in words, and defaults to 16. `length` overrides `end`.
        '''
        self.state = state
        self.pc = self.state.pc if pc is None else pc
        self.ir = ir
        assert is_aligned(self.pc)
        self.end = end
        if length is None and end is None:
            length = 16
        if length is not None:
            self.end = self.pc + length * word_bytes
        assert is_aligned(self.end)

    def _fetch(self):
        if self.pc >= self.end:
            raise StopIteration
        word = sign_extend(self.state.M_word[self.pc])
        self.pc += word_bytes
        return word

    def __iter__(self):
        return self

    def _comment(self, opcode):
        comment = None
        if opcode in [I.PUSH, I.PUSHREL]:
            initial_pc = self.pc
            try:
                value = self._fetch()
                unsigned_value = value & uword_max
                if opcode == I.PUSH:
                    comment = f'{unsigned_value:#x}={value}'
                else: # opcode == I.PUSHREL
                    comment = f'{(initial_pc + value) & uword_max:#x}'
            except IndexError:
                comment = 'invalid address!'
        elif opcode & 0x3 in (0x1, 0x2): # PUSHRELI_N
            value = (opcode - I.PUSHRELI_0) >> 2
            if opcode & 0x3 == 0x2: # negative
                value |= ~0x3f
            comment = f'{self.pc + value * word_bytes:#x}'
        elif opcode == I.NEXT and self.ir != 0:
            # Call `self._fetch()` later, not now.
            name = extra_mnemonic.get(
                self.ir,
                f'invalid extra instruction {self.ir:#x}'
            )
            comment = f'{name}'
            self.ir = 0
        elif opcode == I.NEXTFF:
            # Call `self._fetch()` later, not now.
            if self.ir != -1:
                comment = f'trap {self.ir:#x}'
            self.ir = 0
        elif opcode in [I.JUMP, I.JUMPZ, I.CALL] and self.ir != 0:
            # Call `self._fetch()` later, not now.
            comment = f'to {self.pc + self.ir * word_bytes:#x}'
            self.ir = 0
        return '' if comment is None else f' ({comment})'

    def disassemble(self):
        opcode = self.ir & 0xff
        self.ir >>= 8
        try:
            name = mnemonic[opcode].lower()
        except KeyError:
            name = f"undefined opcode {opcode:#x}"
        comment = self._comment(opcode)
        return f'{name}{comment}'

    def __next__(self):
        pc_str = ('{:#0' + str(hex0x_word_width) + 'x}').format(self.pc)
        addr = '.' * len(pc_str)
        if self.ir == 0:
            self.ir = self._fetch()
            addr = pc_str
        return f'{addr}: {self.disassemble()}'

    def goto(self, pc):
        '''
        After calling this method, disassembly will start from `pc`.
        '''
        assert is_aligned(self.pc)
        self.pc = pc
        self.ir = 0
