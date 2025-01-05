// Author: Daniel Detore
// Meaningless driver to show off the Sqrtr.

.data
    // just throwing in some data
    8: 1 2 3 4 5 6
    0f: 07 08
    0 = ff
    ff = 19
    3f = 21

.text
// logisim starts with all registers = 0,
// but it won't clear them for you when the program finishes.
// don't assume they're 0 unless the user will surely restart the simulation first.
    DIV R0 R0 0         // R0 = 0
    
    LDR R1 R0 12        // R1 = 5
    LDR R2 R1 R1        // R2 = *(10) = 3
    ADD R1 R1 R2        // R1 = 8
    LDR R3 R1           // R3 = 1
    DIV R1 R1 R3        // R1 = 8
    DIV R1 R1 R2        // R1 = 2
    ADD R1 R1 10        // R1 = 12
    STR R1 R1           // 0c = 12
    STR R3 R1 16        // 1c = 1

    // extra tests for corner cases:
    DIV R0 R0 0         // R0 = 0
    LDR R0 R0 63        // R0 = 33
    ADD R1 R0 0         // R1 = 33
    DIV R1 R1 10        // R1 = 3
    ADD R1 R0 221       // R1 = 254
    STR R1 R1 1         // ff = 254
    ADD R1 R1 255       // R1 = 253

    END

    // showing that END works. 
    // this instruction won't be read, and the interpreter will warn you.
    ADD R3 R3 255