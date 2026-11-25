#!/usr/bin/env python3
"""
Hack Assembler (Part B - Capstone Project)
Course: Nand to Tetris - I (ETCCNT301)
Student Name: Tanishq
Roll No.: 2501410009
Personal Number K = 9 (K mod 3 = 0)

Extra Feature for K mod 3 == 0:
Save all labels and variables with their addresses in symbols.txt.
"""

import os
import sys

# Predefined symbols in the Hack assembly language
PREDEFINED_SYMBOLS = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    **{f"R{i}": i for i in range(16)},
    "SCREEN": 16384,
    "KBD": 24576,
}

# C-instruction computation (comp) lookup table: comp_mnemonic -> 7-bit string (a c1 c2 c3 c4 c5 c6)
COMP_TABLE = {
    # a = 0
    "0":   "0101010",
    "1":   "0111111",
    "-1":  "0111010",
    "D":   "0001100",
    "A":   "0110000",
    "!D":  "0001101",
    "!A":  "0110001",
    "-D":  "0001111",
    "-A":  "0110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "D+A": "0000010",
    "D-A": "0010011",
    "A-D": "0000111",
    "D&A": "0000000",
    "D|A": "0010101",
    # a = 1
    "M":   "1110000",
    "!M":  "1110001",
    "-M":  "1110011",
    "M+1": "1110111",
    "M-1": "1110010",
    "D+M": "1000010",
    "D-M": "1010011",
    "M-D": "1000111",
    "D&M": "1000000",
    "D|M": "1010101",
}

# C-instruction destination (dest) lookup table: dest_mnemonic -> 3-bit string (d1 d2 d3)
DEST_TABLE = {
    "":    "000",
    "M":   "001",
    "D":   "010",
    "MD":  "011",
    "DM":  "011",
    "A":   "100",
    "AM":  "101",
    "MA":  "101",
    "AD":  "110",
    "DA":  "110",
    "AMD": "111",
    "ADM": "111",
}

# C-instruction jump (jump) lookup table: jump_mnemonic -> 3-bit string (j1 j2 j3)
JUMP_TABLE = {
    "":    "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
}


def clean_line(raw_line: str) -> str:
    """Remove inline comments and surrounding whitespace."""
    if "//" in raw_line:
        raw_line = raw_line[:raw_line.index("//")]
    return raw_line.strip()


def first_pass(lines: list[str], symbol_table: dict[str, int]) -> tuple[list[tuple[int, str]], dict[str, int]]:
    """
    First reading:
    Remove comments and blank lines, and record every label (LABEL) with its ROM instruction address.
    Returns cleaned instruction list and a dictionary of discovered labels.
    """
    instructions: list[tuple[int, str]] = []
    labels_found: dict[str, int] = {}
    rom_address = 0

    for line_num, raw_line in enumerate(lines, start=1):
        line = clean_line(raw_line)
        if not line:
            continue
        if line.startswith("(") and line.endswith(")"):
            label_name = line[1:-1].strip()
            symbol_table[label_name] = rom_address
            labels_found[label_name] = rom_address
        else:
            instructions.append((line_num, line))
            rom_address += 1

    return instructions, labels_found


def second_pass(
    instructions: list[tuple[int, str]],
    symbol_table: dict[str, int]
) -> tuple[list[str], dict[str, int]]:
    """
    Second reading:
    Turn every instruction into a 16-bit binary string.
    New variables are allocated RAM addresses starting at 16, 17, 18, ...
    Returns the list of 16-bit binary strings and a dictionary of allocated variables.
    """
    binary_lines: list[str] = []
    variables_found: dict[str, int] = {}
    next_var_address = 16

    for line_num, inst in instructions:
        # A-instruction: @value or @symbol
        if inst.startswith("@"):
            symbol = inst[1:].strip()
            if symbol.isdigit():
                address = int(symbol)
            else:
                if symbol not in symbol_table:
                    symbol_table[symbol] = next_var_address
                    variables_found[symbol] = next_var_address
                    next_var_address += 1
                address = symbol_table[symbol]
            binary_lines.append(f"{address:016b}")

        # C-instruction: dest=comp;jump
        else:
            dest_part = ""
            jump_part = ""
            comp_part = inst

            if "=" in comp_part:
                dest_part, comp_part = comp_part.split("=", 1)
            if ";" in comp_part:
                comp_part, jump_part = comp_part.split(";", 1)

            dest_part = dest_part.strip()
            comp_part = comp_part.strip()
            jump_part = jump_part.strip()

            if comp_part not in COMP_TABLE or dest_part not in DEST_TABLE or jump_part not in JUMP_TABLE:
                raise ValueError(f"Line {line_num}: invalid instruction '{inst}'")

            binary_inst = "111" + COMP_TABLE[comp_part] + DEST_TABLE[dest_part] + JUMP_TABLE[jump_part]
            binary_lines.append(binary_inst)

    return binary_lines, variables_found


def save_symbols_file(
    symbols_path: str,
    source_name: str,
    labels: dict[str, int],
    variables: dict[str, int]
) -> None:
    """
    Extra Feature (K = 9, K mod 3 = 0):
    Save all labels and variables with their addresses in symbols.txt.
    """
    with open(symbols_path, "w", encoding="utf-8") as f:
        f.write("=========================================================\n")
        f.write(f"Symbol Table Dump (Extra Feature: K = 9, K mod 3 = 0)\n")
        f.write(f"Source File: {source_name}\n")
        f.write("=========================================================\n\n")

        f.write("--- Labels (ROM Addresses) ---\n")
        if labels:
            for name, addr in labels.items():
                f.write(f"{name:<24} : {addr} (0x{addr:04X} | {addr:016b})\n")
        else:
            f.write("(None)\n")

        f.write("\n--- Variables (RAM Addresses) ---\n")
        if variables:
            for name, addr in variables.items():
                f.write(f"{name:<24} : {addr} (0x{addr:04X} | {addr:016b})\n")
        else:
            f.write("(None)\n")


def assemble_file(asm_path: str, write_symbols_txt: bool = True) -> str:
    """Assemble a single .asm file into a .hack file and save symbols.txt."""
    with open(asm_path, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()

    symbol_table = dict(PREDEFINED_SYMBOLS)
    instructions, labels = first_pass(raw_lines, symbol_table)
    binary_lines, variables = second_pass(instructions, symbol_table)

    base, _ = os.path.splitext(asm_path)
    hack_path = base + ".hack"

    with open(hack_path, "w", encoding="utf-8") as f:
        for b_line in binary_lines:
            f.write(b_line + "\n")

    if write_symbols_txt:
        out_dir = os.path.dirname(os.path.abspath(asm_path))
        symbols_path = os.path.join(out_dir, "symbols.txt")
        save_symbols_file(symbols_path, os.path.basename(asm_path), labels, variables)

    return hack_path


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python assembler.py <file.asm>")
        sys.exit(1)

    for arg in sys.argv[1:]:
        hack_out = assemble_file(arg, write_symbols_txt=True)
        print(f"Assembled '{arg}' -> '{hack_out}' (symbols saved to symbols.txt)")


if __name__ == "__main__":
    main()
