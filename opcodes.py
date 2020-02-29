opc = {
    "LDI" : 0b10000010,
    "PRN" : 0b01000111,
    "MUL" : 0b10100010,
    "ADD" : 0b10100000,
    "HLT" : 0b00000001,
    "PUSH": 0b01000101,
    "POP" : 0b01000110,
    "JMP" : 0b01010100,
    "CALL": 0b01010000,
    "RET" : 0b00010001,
    "IRET": 0b00010011,
    "ST"  : 0b10000100,
    "PRA" : 0b01001000,
    "CMP" : 0b10100111,
    "JEQ" : 0b01010101,
    "JNE" : 0b01010110,
    "ADDI" : 0b10100001, #2 operands, 1 ALU operation, 0 - no modifying the pc
    "AND" : 0b10101000,
    "OR"  : 0b10101010,
    "XOR" : 0b10101011,
    "NOT" : 0b01101001,
    "SHL" : 0b10101100,
    "SHR" : 0b10101101,
    "MOD" : 0b10100100,
}

branch_table = {
    'pass' : 'pass'
}