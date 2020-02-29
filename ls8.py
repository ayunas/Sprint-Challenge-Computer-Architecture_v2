import sys
from itertools import dropwhile
sys.path.append('./examples')
from datetime import datetime
import time, json
from opcodes import opc  #operation code

class LS8:
    def __init__(self):
        self.ram = [0]*256 #8 bit processor can handle 256 bytes in memory
        self.registers = [0]*8 #general purpose registers
        self.pc = 0 #program counter register (reserved)
        # self.sp = 0xf4 #initialized to index 244, used for moving through the RAM.
        self.registers[7] = 0xf4  
        self.sp = self.registers[7] #r7 is the stack pointer, initialized to 244
        self.IS = self.registers[6] #interrupt status
        self.im = self.registers[5] #interrupt mask
        # self.i0,self.i1,self.i2,self.i3,self.i4,self.i5,self.i6,self.i7 = self.ram[-7:] #interrupt vector table
        self.fl = '0b00000LGE'  #flag register (reserved)
        self.time = datetime.now().second
        self.interrupts_enabled = True

    def load(self):
        print(sys.argv)
        if len(sys.argv) > 1:
            data = open(sys.argv[1],'r')
        else:
            filename = input("enter the LS8 program you wish to run: ")
            try:
                data = open(f"./examples/{filename}",'r')
                # print([*data])
            except:
                print(f"Could not open/read file {filename}. exiting...")
                sys.exit(1)
        
        clear_header = [*dropwhile(lambda l : l.startswith('#') or l == '\n',data)]
        clear_comments = [byte.split('#')[0].strip() for byte in clear_header]
        program = [b for b in clear_comments if b != '']

        address = self.ram.index(0) #sets address to first empty space in memory
        
        for byte_str in program:
            self.ram_write(address,int(byte_str,2))
            # self.ram[address] = int(byte_str,2)
            address += 1
        print('LS8 assembly program:\n',program,'\nloaded into RAM successfully.')
        data.close()
    
    def ram_read(self,n):
        # self.pc += 1
        mdr = self.ram[self.pc + n]  #memory data register
        return mdr
    
    def ram_write(self,mar,mdr):
        self.ram[mar] = mdr  #write the memory data register value at the memory address register.
    
    def reg_write(self,reg,data):
        self.registers[reg] = data
        return self.registers[reg]
        # self.pc += 1

    def reg_read(self,reg, asci=None):
        if asci:
             print(f'r[{reg}]: {chr(self.registers[reg])}')
        else:
            print(f'r[{reg}]: {self.registers[reg]}')
        return self.registers[reg]
        # self.pc += 1
    
    def alu(self, op, reg_a, reg_b=None):
        """ALU operations."""
        # AND OR XOR NOT SHL SHR MOD
        if op == "ADD":
            self.registers[reg_a] += self.registers[reg_b]
        #elif op == "SUB": etc
        # elif op == "ADDI":
        #     self.registers[reg_a] += self.registers[reg_b]
        elif op == "MUL":
            self.registers[reg_a] *= self.registers[reg_b]
        elif op == "CMP":
            val_a = self.registers[reg_a]
            val_b = self.registers[reg_b]
            if val_a < val_b:
                self.fl = 0b00000100
                print(val_a,'<',val_b)
            elif val_a > val_b:
                self.fl = 0b00000010
                print(val_a,'>',val_b)
            else: #val_a == val_b
                self.fl = 0b00000001
                print(val_a,'=',val_b)
        elif op == "AND":
            self.registers[reg_a] = self.registers[reg_a] & self.registers[reg_b]
        elif op == "OR":
            # print(self.registers[reg_a],self.registers[reg_b])
            self.registers[reg_a] = self.registers[reg_a] | self.registers[reg_b]
        elif op == "XOR":
            val_a = self.registers[reg_a]
            val_b = self.registers[reg_b]
            print(val_a,val_b)
            self.registers[reg_a] = self.registers[reg_a] ^ self.registers[reg_b]
        elif op == "NOT":
            # self.registers[reg_a] = ~self.registers[reg_a]
            byte_arr = list(f"{self.registers[reg_a]:08b}")
            notted_arr = ['1' if b == '0' else '0' for b in byte_arr]
            notted = ''.join(notted_arr)
            self.registers[reg_a] = int(notted,2)
        elif op == "SHL":
            bits = self.registers[reg_b]
            # print('bits shift left', bits, bits > 8)
            if bits > 8:
                self.registers[reg_a] = 0
            else:
                self.registers[reg_a] = self.registers[reg_a] << bits
        elif op == "SHR":
            bits = self.registers[reg_b]
            # print('bits shift right', bits, bits > 8)
            if bits > 8:
                self.registers[reg_a] = 0
            else:
                self.registers[reg_a] = self.registers[reg_a] >> bits
        elif op == "MOD":
            self.registers[reg_a] %= self.registers[reg_b]
        else:
            raise Exception("Unsupported ALU operation")
        # self.pc += 1
    
    def push(self,byte):
        self.sp -= 1
        if self.ram[self.sp] != 0:
            raise IndexError('stack overflow...')
            sys.exit(1)
        else:
            # self.ram[self.sp] = self.registers[reg]
            self.ram[self.sp] = byte
            # self.pc += 1

    def pop(self,reg=None): #pops the value off the stack and stores in the passed in register
        if reg == None:
            val = self.ram[self.sp]
        else:
            self.registers[reg] = self.ram[self.sp]
            val = self.registers[reg]
            
        self.ram[self.sp] = 0 #clear out the value in the stack regardless of pushing to register or not
        
        if self.sp >= len(self.ram):
            raise IndexError('stack underflow...')
            sys.exit(1)

        self.sp += 1
        return val
        # self.pc += 1
    
    def increment_pc(self,ir):
        ir_operands = ir >> 6
        instruction_length = ir_operands + 1
            # print('instruction length', instruction_length)
        self.pc += instruction_length
    
    def time_check(self):
        current = datetime.now().second
        elapsed = (current - self.time)
        if elapsed >= 1:
            self.time = current
            return True
        else:
            return False
    
    def timer_interrupt(self):
        print('timer interrupt')
        # time.sleep(3)
        self.interrupts_enabled = False
        # masked_interrupts = self.is & self.im
        # for i in range(8):
        #     if b == 1:
        #         self.is = 0
        #         self.push(self.pc)
        #         self.push(self.fl)
        #         for r in self.registers[:-1]:  #don't push stack pointer onto the stack r7
        #             self.push(r)
        
        # self.pc = self.i0
        self.interrupts_enabled = True

    def jump(self,reg):
        self.pc = self.registers[reg]
        print('JUMPED to ', self.pc)
    
    def equal(self):
        equal_mask = 0b00000001
        equal = self.fl & equal_mask
        return equal

    def run(self):
        self.load()
        halted = False
        while halted == False:
            ir = self.ram[self.pc]  #instruction register.  the current instruction to process from the ls8 assembly program loaded
            print([o for o in opc if opc[o] == ir])

            if self.time_check() == True:
                self.timer_interrupt()
    
            if ir == opc['LDI']:  #opc = operation code or the instruction
                reg = self.ram_read(1)
                data = self.ram_read(2)
                self.reg_write(reg,data)

            elif ir == opc['PRN']:
                reg = self.ram_read(1)
                self.reg_read(reg)
            
            elif ir == opc['MUL']:
                reg_1 = self.ram_read(1)
                reg_2 = self.ram_read(2)
                self.alu('MUL', reg_1,reg_2)
            
            elif ir == opc['ADD']:
                reg_1 = self.ram_read(1)
                reg_2 = self.ram_read(2)
                self.alu('ADD', reg_1,reg_2)
            
            elif ir == opc['PUSH']:
                # reg = self.ram_read()
                # val = self.reg_read(reg)
                # self.push()
                reg = self.ram_read(1)
                self.push(self.registers[reg])
            
            elif ir == opc['POP']:
                reg = self.ram_read(1)
                self.pop(reg)
            
            elif ir == opc["JMP"]:
                #jump to address stored in the register operand
                # reg = self.ram[self.pc + 1]
                reg = self.ram_read(1)
                self.jump(reg)
                # self.pc = self.registers[reg]
                # print('JMP to ', self.pc)
                continue

            elif ir == opc["PRA"]:
                reg = self.ram_read(1)
                self.reg_read(reg,True)  #True to print out the ASCII equivalent of the code in the register

            elif ir == opc["CALL"]:
                # next_opc = self.ram_read(2)
                instruction_length = (ir >> 6) + 1 #inst_len = 2 for the CALL.  1 instruction + 1 operand only
                next_pc = self.pc + instruction_length
                self.push(next_pc) #push the ADDRESS of the next OPC not the opcode itself
                reg = self.ram_read(1)
                self.pc = self.registers[reg]
                continue
            
            elif ir == opc["RET"]:
                address = self.pop()
                self.pc = address
                continue  #any instruction manually setting the pc, like returning from subroutine or jmp, don't process the typical increment of the while loop
            
            elif ir == opc["ADDI"]:
                reg_a = self.ram_read(1)
                val = self.ram_read(2)
                reg_b = self.registers.index(0) #find first empty register to store new value
                self.reg_write(reg_b,val)
                self.alu('ADD',reg_a,reg_b)

            elif ir == opc["IRET"]:
                pass

            elif ir == opc["CMP"]:
                reg_a = self.ram_read(1)
                reg_b = self.ram_read(2)
                self.alu('CMP',reg_a,reg_b)
            
            elif ir == opc["JEQ"]:
                # equal_mask = 0b00000001
                # equal = self.fl & equal_mask
                equal = self.equal()
                if equal:
                    reg = self.ram_read(1)
                    self.jump(reg)
                    continue
            
            elif ir == opc["JNE"]:
                # equal_mask = 0b00000001
                # equal = self.fl & equal_mask
                equal = self.equal()
                if not equal:
                    reg = self.ram_read(1)
                    self.jump(reg)
                    continue

            elif ir == opc['ST']:
                reg_a = self.ram_read(1)
                reg_b = self.ram_read(2)
                mar = self.registers[reg_a]
                mdr = self.registers[reg_b]
                self.ram_write(mar,mdr)
                print(self.ram)
            
            elif ir == opc["AND"]: 
                reg_a = self.ram_read(1)
                reg_b = self.ram_read(2)
                self.alu('AND', reg_a,reg_b)
            
            elif ir == opc["OR"]:
                reg_a = self.ram_read(1)
                reg_b = self.ram_read(2)
                self.alu('OR', reg_a,reg_b)
            
            elif ir == opc["XOR"]:
                reg_a = self.ram_read(1)
                reg_b = self.ram_read(2)
                self.alu('XOR', reg_a,reg_b)

            elif ir == opc["SHL"]:
                reg_a = self.ram_read(1)
                reg_b = self.ram_read(2)
                self.alu('SHL', reg_a,reg_b)

            elif ir == opc["SHR"]:
                reg_a = self.ram_read(1)
                reg_b = self.ram_read(2)
                self.alu('SHR', reg_a,reg_b) 

            elif ir == opc["MOD"]:
                reg_a = self.ram_read(1)
                reg_b = self.ram_read(2)
                self.alu('MOD', reg_a,reg_b)                   

            elif ir == opc["NOT"]:
                reg_a = self.ram_read(1)
                self.alu("NOT", reg_a)

            elif ir == opc['HLT']:
                halted == True
                # self.pc += 1
                sys.exit(1)
            else:
                opcode = [o for o in opc if opc[o] == ir]
                if not len(opcode):
                    print(f'opcode {ir} not found, exiting...')
                else:
                    print('invalid opcode', opcode[0], 'exiting...')
                sys.exit(1)

            self.increment_pc(ir)
    
    def __repr__(self):
        return json.dumps({'RAM' : self.ram, 'Registers' : self.registers})

if __name__ == '__main__':
    ls8 = LS8()
    ls8.run()
    # print(ls8.ram)
    # print(ls8.registers)