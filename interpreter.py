#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File name: interpreter.py
Author: Daniel Detore
Created: 2024-12-1
Version: 1.0
Description: Interprets a HANDv8 program and creates instruction and data memory image files.
"""

import sys

def toNbitbin(x, n):
    y = bin(int(x))[2:]
    output = (n - len(y))*"0" + y
    return output

def inputHandle(Rw, Ra, b):
    if(Rw == ""): return "Syntax error; Rw required but missing or misspelled."
    if(Ra == ""): return "Syntax error; Ra required but missing or misspelled."
    if (Rw[0].upper() != "R"):
        return "Rw must be a register. Given "+Rw+".";
    elif (Ra[0].upper() != "R"):
        return "Ra must be a register. Given "+Ra+".";
    w = int(Rw[1:])
    a = int(Ra[1:])
    if (w < 0 or w > 3):
        return "Rw must be one of R0, R1, R2, R3. Given "+Rw+".";
    elif (a < 0 or a > 3):
        return "Ra must be one of R0, R1, R2, R3. Given "+Ra+".";
    if (b == ""): return "ok"
    useimm = b[0].upper() != "R"
    if (useimm and (int(b) > 255 or int(b) < 0)): 
        return "imm8 must be between 0 and 255 inclusive. Given "+b+".";
    elif (not useimm):
        bb = b[1:]
        if (int(bb) < 0 or int(bb) > 3):
            return "Rb must be one of R0, R1, R2, R3. Given "+b+".";
    return "ok"


def ADD(Rw, Ra, b):
    handle = inputHandle(Rw, Ra, b)
    if (handle != "ok"): return handle
    useimm = b[0].upper() != "R"
    # opcode
    output = "000"
    if (not useimm): output += "0"
    else: output += "1"
    # operands
    output += toNbitbin(Rw[1], 2)
    output += toNbitbin(Ra[1], 2)
    if (not useimm):
        output += toNbitbin(b[1], 2) + "000000"
    else:
        output += toNbitbin(b, 8)
    return output


def DIV(Rw, Ra, b):
    base = ADD(Rw, Ra, b)
    return base[:2]+"1"+base[3:]

#assert(ADD("R1", "r0", "r3") == "0000010011000000")
#assert(ADD("R2", "r1", "15") == "0001100100001111")

#assert(DIV("r3", "R2", "r1") == "0010111001000000")
#assert(DIV("r0", "R3", "5") == "0011001100000101")
#assert(DIV("r1", "R1", "10") == "0011010100001010")

def LDR(Rw, Ra, b):
    if (b == ""): b = "0"
    handle = inputHandle(Rw, Ra, b)
    if (handle != "ok"): return handle
    useimm = (b[0].upper() != "R")
    # opcode
    output = "100"
    if (not useimm): output += "0"
    else: output += "1"
    # operands
    output += toNbitbin(Rw[1], 2)
    output += toNbitbin(Ra[1], 2)
    if (not useimm):
        output += toNbitbin(b[1], 2) + "000000"
    else:
        output += toNbitbin(b, 8)
    return output

def STR(Rt, Ra, b):
    if (b[0].upper() == "R"): 
        return "STR cannot take Rb. Format: STR Rt Ra [imm8]. Given "+b+"."
    if (int(b) > 63 or int(b) < 0): 
        return "imm8 must be between 0 and 63 inclusive. Given "+b+".";
    output = "010100"
    output += toNbitbin(Ra[1], 2)
    output += toNbitbin(Rt[1], 2)
    output += toNbitbin(b, 6)
    return output

#assert(LDR("R0", "R1", "") == "1001000100000000")
#assert(LDR("R1", "R2", "4") == "1001011000000100")
#assert(LDR("R2", "R3", "R0") == "1000101100000000")

#assert(STR("R0", "R1", "") == "0101000100000000")
#assert(STR("R1", "R2", "4") == "0101011000000100")
#assert(STR("R2", "R3", "R0") == "0100101100000000")


# ACTUAL PROGRAM START

if (len(sys.argv) == 1 or len(sys.argv) > 2):
    raise Exception("Usage: py "+sys.argv[0]+" <yourfile.s>")

filename = sys.argv[1]
if (".s" not in filename):
    filename += ".s"

source = open(filename, "r")

lines = source.readlines()
source.close()


# we need to know the range of each section
textstart = -1
datastart = -1

# finding each section starts
for i in range(0, len(lines)):
    line = lines[i]
    lineend = line.find("//")
    if (lineend != -1): line = line[:lineend]
    if (".text" in line): 
        textstart = i
    elif (".data" in line):
        datastart = i
    if (textstart != -1 and datastart != -1): break

# complaining
if (datastart == -1 and textstart == -1):
    print("Warning: No labels found. Assuming everything is .text.")
elif (datastart != -1 and textstart == -1):
    print("Warning: Did you mean to include no .text?")

# generously estimating endings
textend = 0
dataend = 0
if (datastart > textstart): 
    dataend = len(lines)
    textend = datastart-1
else:
    textend = len(lines)
    dataend = textstart-1

# Processing instructions
instructions = ["0"]*256        # stores machine code binaries
instructionCount = 0
for i in range(textstart+1, textend):
    line = lines[i]
    # ignore comments
    lineend = line.find("//")
    if (lineend != -1): line = line[:lineend]
    line = " ".join(line.upper().split())

    # ignore blank/commented lines
    if (line == ""): continue
    # stop at END, complain if there's more
    if (line == "END"): 
        if (i < textend-1): print("Warning: Possibly premature END at line", str(i+1)+".")
        break
    if (instructionCount >= 256):
        raise Exception("Fatal error at line "+str(i+1)+": Instruction limit reached.")

    name = line[:3]
    Rw = line[4:6]
    Ra = line[7:9]
    if (len(line)>9): b = line[10:]
    else: b = "0"


    match name:
        case "ADD":
            temp = ADD(Rw, Ra, b)
        case "DIV":
            temp = DIV(Rw, Ra, b)
        case "LDR":
            temp = LDR(Rw, Ra, b)
        case "STR":
            temp = STR(Rw, Ra, b)
        case _:
            raise Exception("Fatal error at line "+str(i+1)+": Nonexistent or misspelled instruction name "+line[:line.find(" ")]+".\n"+line)
    if (temp[-1] == "."):
        raise Exception("Fatal error at line "+str(i+1)+":\n"+line+"\n"+temp)
    if (instructionCount >= 256):
        raise Exception("Fatal error at line "+str(i+1)+": instruction memory overfull. Your program has many instructions.")
    
    instructions[instructionCount] = temp
    instructionCount+=1

instructionMemory = open(filename+"-instructions.txt", "w")
instructionMemory.write("v3.0 hex words addressed")
# outputting instructions
for i in range(0, 256):
    if (i == 0): instructionMemory.write("\n00:")
    elif (i % 16 == 0): instructionMemory.write("\n"+hex(i)[2:]+":")
    code = hex(int(instructions[i], 2))[2:]
    code = (4 - len(code))*"0" + code
    instructionMemory.write(" " + code)
    
instructionMemory.close()
print("Successfully processed .text section and output "+filename[:-2]+"-instructions.txt to active directory.")

# processing .data
data = ["0"]*256        # stores data 
for i in range(datastart+1, dataend):
    line = lines[i]
    # ignore comments
    lineend = line.find("//")
    if (lineend != -1): line = line[:lineend]
    line = " ".join(line.upper().split())

    # ignore blank/commented lines
    if (line == ""): continue

    if ("=" in line):
        hexvalue = line[5:]
        value = int(hexvalue, 16)
        if (value < 0 or value > 255):
            raise Exception("Fatal error at line "+str(i+1)+": received value 0x"+hexvalue+" = "+value+"which is out of range (0 to 255 inclusive).")
        data[int(line[:line.find("=")], 16)] = hexvalue
    elif (":" in line):
        base = int(line[:line.find(":")], 16)
        arguments = line[line.find(":")+1:].split()
        for offset in range(len(arguments)):
            hexvalue = arguments[offset]
            value = int(hexvalue, 16)
            if (value < 0 or value > 255):
                raise Exception("Fatal error at line "+str(i+1)+": received value 0x"+hexvalue+" = "+value+"which is out of range (0 to 255 inclusive).")
            data[base + offset] = hexvalue


# outputting .data
dataMemory = open(filename+"-data.txt", "w")
dataMemory.write("v3.0 hex words addressed")

for i in range(0, 256):
    if (i == 0): dataMemory.write("\n00:")
    elif (i % 16 == 0): dataMemory.write("\n"+hex(i)[2:]+":")
    code = data[i]
    code = (2 - len(code))*"0" + code
    dataMemory.write(" " + code)
    
dataMemory.close()
print("Successfully processed .data section and output "+filename[:-2]+"-data.txt to active directory.")

print("Successfully assembled "+filename+". Terminating interpreter.")
exit(0)