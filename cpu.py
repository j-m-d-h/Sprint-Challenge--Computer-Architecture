"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.SP = 7
        self.IS = 6
        self.IM = 5
        self.FL = 0b00000000
        self.register = [0] * 8
        self.register[self.SP] = 0xF4
        self.ram = [0] * 256
        self.pc = 0

        self.alu_table = {
            162:'MUL',
            167:'CMP'
        }

        self.instruction_table = {
            0:self.NOP,
            1:self.HALT,
            69:self.PUSH,
            70:self.POP,
            71:self.PRN,
            130:self.LDI,
            84:self.JMP,
            85:self.JEQ,
            86:self.JNE,
        }

    def ram_read(self, address):
        """Read the data in memory at the given address."""
        return self.ram[address]

    def ram_write(self, data, address):
        """Write the given data into memory at the given address."""
        self.ram[address] = data

    def load(self):
        """Load a program into memory."""

        address = 0
        program = []

        with open(sys.argv[1], 'r') as file:
            for line in file:
                string1 = line.split("#")[0].strip()
                if string1 == '':
                    continue
                program.append(int(string1,2))
        for instruction in program:
            self.ram_write(instruction, address)
            address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.register[reg_a] += self.register[reg_b]
            self.pc += 3
        elif op == 'AND':
            self.register[reg_a] = self.register[reg_a] & self.register[reg_b]
            self.pc += 3
        elif op == 'SUB':
            self.register[reg_a] -= self.register[reg_b]
            self.pc += 3
        elif op == "INC":
            self.register[reg_a] += 1
            self.pc += 2
        elif op == "DEC":
            self.register[reg_a] -= 1
            self.pc += 2
        elif op == "MUL":
            self.register[reg_a] *= self.register[reg_b]
            self.pc += 3
        elif op == "CMP":
            if self.register[reg_a] < self.register[reg_b]:
                self.FL = 0b00000100
            elif self.register[reg_a] > self.register[reg_b]:
                self.FL = 0b00000010
            else:
                self.FL = 0b00000001
            self.pc += 3
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.register[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.on = True
        while self.on:
            instruction = self.ram_read(self.pc)
            if instruction in self.alu_table:
                self.alu(self.alu_table[instruction],
                self.ram_read(self.pc+1), self.ram_read(self.pc+2))
            elif instruction in self.instruction_table:
                self.instruction_table[instruction]()
            else:
                print(f'Error: invalid instruction {instruction} at {self.pc}')
                break
        sys.exit(1)

    def HALT(self):
        """Halt the program."""
        self.on = False

    def PRN(self):
        """Print the given data."""
        data = self.register[self.ram_read(self.pc+1)]
        print(data)
        self.pc += 2

    def PUSH(self):
        """Push the given data to the top of the stack."""
        self.register[self.SP] -= 1
        reg_num = self.ram_read(self.pc+1)
        stack_address = self.register[self.SP]
        self.ram_write(self.register[reg_num], stack_address)
        self.pc += 2

    def POP(self):
        """Pop the data from the top of the stack to the given register."""
        reg_num = self.ram_read(self.pc+1)
        stack_address = self.register[self.SP]
        self.register[reg_num] = self.ram_read(stack_address)
        self.register[self.SP] += 1
        self.pc += 2

    def LDI(self):
        """Set the given register to the given integer value."""
        self.register[self.ram_read(self.pc+1)] = self.ram_read(self.pc+2)
        self.pc += 3

    def NOP(self):
        """Do nothing."""
        self.pc += 1

    def JMP(self):
        """Jump to the address in the given register."""
        reg_address = self.ram_read(self.pc+1)
        self.pc = self.register[reg_address]

    def JEQ(self):
        """Jump to the address in the given register if the equal flag is true."""
        if self.FL == 0b00000001:
            reg_address = self.ram_read(self.pc+1)
            self.pc = self.register[reg_address]
        else:
            self.pc += 2

    def JNE(self):
        """Jump to the address in the given register if the equal flag is false."""
        if self.FL != 0b00000001:
            reg_address = self.ram_read(self.pc+1)
            self.pc = self.register[reg_address]
        else:
            self.pc += 2
