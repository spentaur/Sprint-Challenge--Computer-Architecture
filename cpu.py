"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.SP = 7
        self.reg[self.SP] = 0xf4
        self.pc = 0
        self.running = False
        self.branchtable = {
            0b10000010: self.ldi,
            0b01000111: self.prn,
            0b00000001: self.hlt,
            0b10100010: self.mul,
            0b01000101: self.push,
            0b01000110: self.pop,
            0b01010000: self.call,
            0b00010001: self.ret,
            0b10100000: self.add,
            0b10100111: self.cmp,
            0b01010100: self.jmp,
            0b01010101: self.jeq,
            0b01010110: self.jne
        }
        self.flag = 0b00000000

    def ldi(self, register, value):
        self.reg[register] = value
        return self

    def prn(self, register):
        print(self.reg[register])
        return self

    def hlt(self):
        self.running = False
        return self

    def mul(self, regsiter_a, register_b):
        self.reg[regsiter_a] *= self.reg[register_b]
        return self

    def push(self, register):
        # Decrement the SP.
        self.reg[self.SP] -= 1
        # Copy the value in the given register to the address pointed to by SP.
        self.ram_write(self.reg[self.SP], self.reg[register])
        return self

    def pop(self, register):
        # Copy the value from the address pointed to by SP to the given
        # register.
        self.reg[register] = self.ram_read(self.reg[self.SP])
        # Increment SP.
        self.reg[self.SP] += 1
        return self

    def call(self, register):
        # The address of the instruction directly after CALL is pushed onto the
        # stack. This allows us to return to where we left off when the
        # subroutine finishes executing.
        self.reg[self.SP] -= 1
        self.ram_write(self.reg[self.SP], self.pc + 2)

        # The PC is set to the address stored in the given register. We jump to
        # that location in RAM and execute the first instruction in the
        # subroutine. The PC can move forward or backwards from its current
        # location.
        self.pc = self.reg[register]
        return self

    def ret(self):
        # Pop the value from the top of the stack and store it in the PC.
        self.pc = self.ram_read(self.reg[self.SP])
        self.reg[self.SP] += 1
        return self

    def add(self, register_a, register_b):
        self.reg[register_a] += self.reg[register_b]
        return self

    def cmp(self, register_a, register_b):
        if self.reg[register_a] == self.reg[register_b]:
            self.flag = 0b00000001
        elif self.reg[register_a] > self.reg[register_b]:
            self.flag = 0b00000010
        else:
            self.flag = 0b00000100
        return self

    def jmp(self, register):
        # Jump to the address stored in the given register.
        # Set the PC to the address stored in the given register.
        self.pc = self.reg[register]
        return self

    def jeq(self, register):
        # If equal flag is set (true), jump to the address stored in the given
        # register.
        if self.flag & 1:
            self.jmp(register)
        else:
            self.pc += 2

    def jne(self, register):
        # If E flag is clear(false, 0), jump to the address stored in the given
        # register.
        if not self.flag & 1:
            self.jmp(register)
        else:
            self.pc += 2

    def load(self, program):
        """Load a program into memory."""
        address = 0
        with open(program, 'r') as f:
            for line in f:
                line = line.split('#')[0].strip('\n')
                if line:
                    self.ram_write(address, int(line, 2))
                    address += 1

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value
        return self

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.running = True
        while self.running:
            ir = self.ram_read(self.pc)
            # AA Number of operands for this opcode, 0-2
            num_args = ir >> 6
            if ir in self.branchtable:
                # very unreadable, but it's getting the opcode and args
                self.branchtable[ir](*[self.ram_read(self.pc + i + 1)
                                       for i in range(num_args)])
            # increment PC if needed
            # basically getting the C value from the instruction
            if not (ir >> 4 & 0b0001):
                self.pc += (1 + num_args)
