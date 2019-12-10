# Advent of Code 2019, Intcode Machine
# (c) blu3r4y

from abc import ABC, abstractmethod
from enum import IntEnum
from functools import partialmethod
from typing import List, Union

import numpy as np


class Mode(IntEnum):
    POSITION = 0
    IMMEDIATE = 1
    RELATIVE = 2


class Opcode(IntEnum):
    ADD = 1
    MUL = 2
    INPUT = 3
    OUTPUT = 4
    JMP_TRUE = 5
    JMP_FALSE = 6
    LESS_THAN = 7
    EQUALS = 8
    BASE_OFFSET = 9
    HALT = 99


class Instruction(ABC):

    def __init__(self, opcode: int, params: List[int], vm: "IntcodeMachine"):
        """
        Abstract base constructor for an instruction of the IntCode Machine
        @param opcode: The opcode along with its parameter mode specification
        @param params: The parameters for this opcode
        @param vm: Reference to the intcode machine
        """
        self.opcode, self.params = opcode, params
        self.instr = Opcode(self.opcode % 100)
        self.vm = vm

        # decode parameter modes
        self.modes = [0] * self.nparams()
        for i in range(0, self.nparams()):
            self.modes[i] = self.opcode // (10 ** (i + 2)) % 10

    def _get_params(self, nin: int, nout: int) -> Union[int, List[int]]:
        params = []

        for i in range(nin):
            # input parameters are either positional or immediate
            if self.modes[i] == Mode.IMMEDIATE:
                params.append(int(self.params[i]))
            elif self.modes[i] == Mode.POSITION:
                params.append(int(self.vm.memory[self.params[i]]))
            elif self.modes[i] == Mode.RELATIVE:
                params.append(int(self.vm.memory[self.vm.base + self.params[i]]))

        for i in range(nin, nin + nout):
            # output parameters are always memory addresses because they will be written
            if self.modes[i] == Mode.IMMEDIATE:
                raise ValueError(f"unsupported immediate mode for instruction {self.opcode} at ip = {self.vm.ip}")
            if self.modes[i] == Mode.POSITION:
                params.append(self.params[i])
            elif self.modes[i] == Mode.RELATIVE:
                params.append(self.vm.base + self.params[i])

        assert len(params) == nin + nout
        return params if len(params) > 1 else params[0]  # return scalar or list

    @classmethod
    def nparams(cls) -> int:
        """
        @return: Number of parameters
        """
        return cls.length() - 1

    @classmethod
    @abstractmethod
    def length(cls) -> int:
        """
        @return: Instruction length
        """
        pass

    @abstractmethod
    def apply(self) -> int:
        """
        Perform the instruction
        @return: Optional new instruction pointer if not None
        """
        pass


class HaltInstr(Instruction):

    @classmethod
    def length(cls) -> int:
        return 1

    def apply(self) -> int:
        pass  # nop


class HaltInstrInternal(HaltInstr):
    """
    Internal forced halt that is used to pause the execution
    """
    pass


class AddInstr(Instruction):

    @classmethod
    def length(cls) -> int:
        return 4

    def apply(self):
        a, b, c = self._get_params(2, 1)
        self.vm.memory[c] = a + b


class MulInstr(Instruction):

    @classmethod
    def length(cls) -> int:
        return 4

    def apply(self):
        a, b, c = self._get_params(2, 1)
        self.vm.memory[c] = a * b


class InputInstr(Instruction):

    def __init__(self, opcode: int, params: List[int], vm: "IntcodeMachine", value: int):
        super().__init__(opcode, params, vm)
        self.value = value

    @classmethod
    def length(cls) -> int:
        return 2

    def apply(self):
        a = self._get_params(0, 1)
        self.vm.memory[a] = self.value

    @staticmethod
    def build_input_instruction(value: int):
        """
        Factory method that returns an input instruction that will always input the provided value
        @param value: The value to be inputted if this instruction is applied
        @return: An instantiable `InputInstr`
        """

        class InputInstrPartial(InputInstr):
            __init__ = partialmethod(InputInstr.__init__, value=value)

        return InputInstrPartial


class OutputInstr(Instruction):

    def __init__(self, opcode: int, params: List[int], vm: "IntcodeMachine", buffer: list):
        super().__init__(opcode, params, vm)
        self.buffer = buffer

    @classmethod
    def length(cls) -> int:
        return 2

    def apply(self):
        a = self._get_params(1, 0)
        self.buffer.append(a)

    @staticmethod
    def build_output_instruction(buffer: list):
        """
        Factory method that returns an output instruction that will write its output to the supplied buffer
        @param buffer: A list to which output can be appended
        @return: An instantiable `OutputInstr`
        """

        class OutputInstrPartial(OutputInstr):
            __init__ = partialmethod(OutputInstr.__init__, buffer=buffer)

        return OutputInstrPartial


class JmpTrueInstr(Instruction):

    @classmethod
    def length(cls) -> int:
        return 3

    def apply(self):
        a, b = self._get_params(2, 0)
        if a != 0:
            return b  # ip := b


class JmpFalseInstr(Instruction):

    @classmethod
    def length(cls) -> int:
        return 3

    def apply(self):
        a, b = self._get_params(2, 0)
        if a == 0:
            return b  # ip := b


class LessThanInstr(Instruction):

    @classmethod
    def length(cls) -> int:
        return 4

    def apply(self):
        a, b, c = self._get_params(2, 1)
        self.vm.memory[c] = int(a < b)


class EqualsInstr(Instruction):

    @classmethod
    def length(cls) -> int:
        return 4

    def apply(self):
        a, b, c = self._get_params(2, 1)
        self.vm.memory[c] = int(a == b)


class BaseOffsetInstr(Instruction):

    @classmethod
    def length(cls) -> int:
        return 2

    def apply(self):
        a = self._get_params(1, 0)
        self.vm.base += a


class IntcodeMachine(object):

    def __init__(self, memory: Union[np.ndarray, str], inputs: List[int] = None):
        """
        Create a new IntCode virtual machine with a given program and data memory and an optional input buffer
        @param memory: Program and data memory
        @param inputs: Input buffer for input instructions
        """

        self.memory = memory if isinstance(memory, np.ndarray) else self.parse_memory(memory)  # program and data
        self.ip = 0  # instruction pointer
        self.base = 0  # relative base
        self.done = False  # are we finished yet?
        self.inputs = inputs if inputs is not None else []  # input buffer
        self.outputs = []  # output buffer

        # increase memory size
        self.memory = np.pad(self.memory, (0, int(1E4)), "constant")

        # opcode to instruction mapping
        self._mapping = {
            Opcode.HALT: HaltInstr,
            Opcode.ADD: AddInstr,
            Opcode.MUL: MulInstr,
            Opcode.INPUT: None,  # created dynamically
            Opcode.OUTPUT: OutputInstr.build_output_instruction(self.outputs),
            Opcode.JMP_TRUE: JmpTrueInstr,
            Opcode.JMP_FALSE: JmpFalseInstr,
            Opcode.LESS_THAN: LessThanInstr,
            Opcode.EQUALS: EqualsInstr,
            Opcode.BASE_OFFSET: BaseOffsetInstr
        }

    def execute(self, inputs: List[int] = None, nopause=False) -> int:
        """
        Interpret the instructions and finally return the last output value
        @param inputs: Fill the input buffer with these values
        @param nopause: Avoid forced halts due to missing inputs
        @return: The last value that was written by an output instruction
        """

        if inputs is not None:
            self.inputs.extend(inputs)

        while self.ip < len(self.memory):
            instr = self._parse_instruction()
            if isinstance(instr, HaltInstr):
                self.done = type(instr) == HaltInstr  # we are only done on "real" halt instructions
                break

            result = instr.apply()

            # increase ip by instruction length by default - or set it to the instruction result
            self.ip = self.ip + instr.length() if result is None else result

        if nopause and not self.done:
            raise RuntimeError(f"vm execution stopped at ip = {self.ip} because the input buffer was empty")

        return self.get_output()

    def get_output(self, n=1) -> Union[None, int, List[int]]:
        """
        Retrieve the last n (default: 1) output values
        @param n: Number of outputs to retrieve (default: 1)
        """
        if len(self.outputs) == 0:
            return None
        return self.outputs[-n:] if n > 1 else self.outputs[-1]

    def _parse_instruction(self) -> Instruction:
        opcode = self.memory[self.ip]
        instrcode = opcode % 100
        if instrcode not in self._mapping:
            raise ValueError(f"unknown opcode {opcode} at ip = {self.ip}")

        # build input instructions dynamically or halt if no input is available
        if instrcode == Opcode.INPUT:
            cls = InputInstr.build_input_instruction(self.inputs.pop(0)) \
                if len(self.inputs) > 0 else HaltInstrInternal
        else:
            cls = self._mapping[instrcode]

        # initialize instruction
        params = self.memory[self.ip + 1:self.ip + cls.length()].tolist()
        instr = cls(opcode, params, self)
        return instr

    @staticmethod
    def parse_memory(text: str) -> np.ndarray:
        """
        Parse a program from its string representation
        @param text: A comma-separated list of memory values
        @return: A memory array
        """
        return np.array(list(map(int, text.split(","))), dtype=np.int64)
