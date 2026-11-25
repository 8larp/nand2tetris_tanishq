// Capstone Project - Part C: Make the Computer Draw a Box
// Course: Nand to Tetris - I (ETCCNT301)
// Student Name: Tanishq
// Roll No.: 2501410009
// Personal Number K = 09 (K = 9)
//
// Box Specifications for K = 9:
// - Starts at row K = 9
//   Starting screen address = SCREEN + 32 * 9 = 16384 + 288 = 16672
// - Height = 20 rows tall (rows 9 through 28 inclusive)
// - Width  = 16 * ((K mod 4) + 1) = 16 * ((9 mod 4) + 1) = 16 * (1 + 1) = 32 pixels wide (2 words per row)
// - Behavior:
//   While any key is pressed (RAM[KBD] != 0), a black box (all 1s = -1) appears.
//   When the key is released (RAM[KBD] == 0), the box disappears (all 0s = 0).

(LOOP)
    // Read keyboard state at KBD (24576)
    @KBD
    D=M
    @SET_BLACK
    D;JNE       // If key != 0, set color to -1 (black)

    // Key is 0 (released) -> set color to 0 (white)
    @color
    M=0
    @INIT_DRAW
    0;JMP

(SET_BLACK)
    @color
    M=-1

(INIT_DRAW)
    // Starting screen address for row K = 9: 16384 + 32 * 9 = 16672
    @16672
    D=A
    @addr
    M=D

    // Number of rows to draw = 20
    @20
    D=A
    @rows
    M=D

(ROW_LOOP)
    // Check if rows == 0; if so, return to main keyboard polling LOOP
    @rows
    D=M
    @LOOP
    D;JEQ

    // Draw first 16-pixel word (pixels 0..15 from left edge) at addr
    @color
    D=M
    @addr
    A=M
    M=D

    // Draw second 16-pixel word (pixels 16..31 from left edge) at addr + 1
    @color
    D=M
    @addr
    A=M+1
    M=D

    // Advance addr to next row (1 row = 32 words)
    @32
    D=A
    @addr
    M=D+M

    // Decrement remaining row counter
    @rows
    M=M-1

    @ROW_LOOP
    0;JMP
