# Lecture 3 Lab Report

Name: Student Handout Solution  Student ID: RV32-LAB3-2026  Partner: Antigravity  Date: November 11, 2026
Simulator version / RV32 setting: Ripes 2.2.6 (RV32_SS Single-Cycle Processor, RV32I Base Integer ISA)

---

## A Register trace

### State Table
| After instruction | x5 (t0) | x6 (t1) | x7 (t2) | x0 (zero) |
|---|---|---|---|---|
| **Initial state** | 9 | 4 | 0 | 0 |
| `sub x7, x5, x6` | 9 | 4 | 5 | 0 |
| `addi x5, x7, -1` | 4 | 4 | 5 | 0 |
| `add x6, x5, x7` | 4 | 9 | 5 | 0 |
| `add x0, x5, x6` | 4 | 9 | 5 | 0 |

- **PC before sub:** `0x0000000C` (12)
- **PC after sub:** `0x00000010` (16)
- **PC change in bytes:** `+4 bytes`. All standard RV32I instructions are exactly 32 bits (4 bytes) wide, and memory is byte-addressed. Sequential execution advances the PC by 4 bytes.
- **Machine code for `sub x7, x5, x6`:** `0x006283b3` (`funct7=0000000`, `rs2=00110` [x6], `rs1=00101` [x5], `funct3=000`, `rd=00111` [x7], `opcode=0110011`).
- **Explanation:** Assembly mnemonics and machine words are two representations of the same operation: assembly is human-readable symbolic notation, while machine code is the binary pattern directly decoded by processor hardware control logic.

### Questions
- **A1 — Why does the third instruction use the new x5 value?**
  Instructions execute in sequential program order. The second instruction (`addi x5, x7, -1`) commits its computed result (`5 + (-1) = 4`) into destination register `x5` before the third instruction (`add x6, x5, x7`) reads `x5` as its source operand.
- **A2 — The last addition calculates a value. Why does x0 still contain zero?**
  In RISC-V RV32I, register `x0` is hardwired to constant zero. Even though the ALU calculates `4 + 9 = 13`, any write to `x0` is discarded by hardware logic, ensuring `x0` always reads `0x00000000`.

---

## B Memory and byte transfers

- **Actual sample address M:** `0x10000000` (Ripes default data segment base)

### Memory Byte Map (Little-Endian)
| Checkpoint | M (`0x10000000`) | M+1 (`0x10000001`) | M+2 (`0x10000002`) | M+3 (`0x10000003`) |
|---|---|---|---|---|
| **After sw** | `0x78` | `0x56` | `0x34` | `0x12` |
| **After sb** | `0x78` | `0xEF` | `0x34` | `0x12` |

- **Final register values in 8-digit hexadecimal:**
  - `t3` (`lw`): `0x1234EF78`
  - `t4` (`lb`): `0xFFFFFFEF`
  - `t5` (`lbu`): `0x000000EF`
- **Decimal interpretations:**
  - `t4` (signed decimal): `-17`
  - `t5` (unsigned decimal): `239`

### Questions
- **B1 — Why do lb and lbu read the same byte but produce different 32-bit values?**
  Both instructions fetch the exact same 8-bit byte `0xEF` (binary `1110 1111`) from address `M+1`. `lb` (load byte signed) performs sign extension by copying the sign bit (bit 7, which is 1) across the upper 24 bits (bits 31..8), yielding `0xFFFFFFEF` (-17). `lbu` (load byte unsigned) performs zero extension by padding bits 31..8 with zeros, yielding `0x000000EF` (239).
- **B2 — Does sw or sb change t0 or t1? How many bytes does each store write?**
  Neither `sw` nor `sb` modifies registers `t0` or `t1`. Store instructions transfer data from CPU registers into data memory without modifying general-purpose registers. `sw` writes a full 32-bit word (4 bytes: `M` through `M+3`), while `sb` writes exactly 1 byte (8 bits: `M+1` only).

---

## C Array sum

- **Actual base address B:** `0x10000000`
- **trace_start S:** `0x00000014` (following input wrapper instructions)

### Four Snapshots immediately before loop's beq (for n=3)
| Elements processed | x5 (sum) | x6 (index) | x7 (pointer) | x8 (last load) |
|---|---|---|---|---|
| **0** | `0` | `0` | `B (0x10000000)` | `0 (sentinel)` |
| **1** | `3` | `1` | `B+4 (0x10000004)` | `3` |
| **2** | `2` | `2` | `B+8 (0x10000008)` | `-1` |
| **3** | `6` | `3` | `B+12 (0x1000000C)` | `4` |

### Boundary Cases
| n | Predicted sum | Observed sum | x6 (index) | x7 (pointer) | x8 (last load) | Last load address | Count |
|---|---|---|---|---|---|---|---|
| **0** | 0 | 0 | 0 | `B (0x10000000)` | 0 (sentinel) | None (no load) | 4 |
| **1** | 3 | 3 | 1 | `B+4 (0x10000004)` | 3 | `B (0x10000000)` | 10 |
| **2** | 2 | 2 | 2 | `B+8 (0x10000008)` | -1 | `B+4 (0x10000004)` | 16 |
| **3** | 6 | 6 | 3 | `B+12 (0x1000000C)` | 4 | `B+8 (0x10000008)` | 22 |

### Dynamic Instruction Count Derivation
- Initialization instructions: `3` (`addi x5`, `addi x6`, `addi x7` at `trace_start`)
- Condition tests: `n + 1` (`beq x6, x11, end`; evaluated $n$ times false + 1 time taken exit)
- Loop body & jump back: `5n` (`lw`, `add`, `addi x7`, `addi x6`, `jal`; 5 instructions $\times$ $n$ iterations)
- **Total formula:** $\text{Count} = 3 + (n + 1) + 5n = 6n + 4$
  - $n=0 \implies 6(0) + 4 = 4$
  - $n=1 \implies 6(1) + 4 = 10$
  - $n=2 \implies 6(2) + 4 = 16$
  - $n=3 \implies 6(3) + 4 = 22$

### Questions & Transfer Test
- **Why does a final pointer of B+12 not prove a fourth load happened?**
  In the 3rd iteration, after `lw` loads `array[2]`, `addi x7, x7, 4` increments `x7` from `B+8` to `B+12` in anticipation of a possible next iteration. Then `addi x6, x6, 1` increments `x6` to 3 and jumps to `loop`. The branch `beq x6, x11, end` tests $3 == 3$, evaluates true, and exits immediately. Pointer increment is speculative for the next iteration; no load occurs at `B+12`.
- **Transfer test (array=[5, -2, 9], n=2):**
  - Predicted sum: `5 + (-2) = 3`
  - Observed sum: `3`
  - Final pointer: `B+8 (0x10000008)`
  - Last load address: `B+4 (0x10000004)` (loaded value `-2`)
  - Instruction count: `16` ($6(2) + 4 = 16$)
  - **Is the value 9 read?** No, because $n=2$ causes the loop to exit when index `x6` reaches 2 before the loop body ever executes for index 2 (element 9 at `B+8`).

---

## D Debugging

| Bug | Mutation | Exposing Test | First incorrect state or access | Repair and retest result |
|---|---|---|---|---|
| **D1** | `addi x7, x7, 1` (advance by 1 byte instead of 4) | $n=3$, array `[3, -1, 4]` | In iteration 2 ($x6=1$), $x7$ becomes $B+1$ instead of $B+4$. `lw x8, 0(x7)` executes an unaligned word read spanning bytes $[B+1..B+4]$, loading corrupted data (`0x0400ffff` instead of `-1`) and yielding incorrect sum 3. | **Repair:** Change `addi x7, x7, 1` back to `addi x7, x7, 4` (stride must equal 4 bytes per 32-bit word). **Retest:** $x7$ increments by 4; sum correctly equals 6. |
| **D2** | Move `lw` before `beq` | $n=0$, sentinel $x8=0$ | For $n=0$, `lw x8, 0(x7)` executes unconditionally before the length check. $x8$ is erroneously overwritten with `array[0]=3` (illegal speculative read on empty array). | **Repair:** Place `beq x6, x11, end` before `lw x8, 0(x7)` (check-before-access). **Retest:** for $n=0$, loop exits immediately; $x8$ remains sentinel 0. |
| **D3** | Delete `addi x6, x6, 1` | $n=3$, step 2 iterations | In iteration 2, $x6$ remains 0 instead of 1, while $x7$ advances to $B+4$. Because $x6$ never increments, termination condition $x6 == x11$ is never met, resulting in an infinite loop that reads past array bounds. | **Repair:** Restore `addi x6, x6, 1` in the loop body. **Retest:** index increments properly each iteration; loop terminates after 3 iterations with sum 6. |

- **D4 — Which test would you choose first when checking whether a loop reads too early?**
  Test with $n = 0$ (the empty array boundary case) with an initialized sentinel in the destination register ($x8 = 0$). An empty array should never touch memory. If `lw` precedes the branch condition, testing $n=0$ immediately triggers the load and changes the sentinel, exposing the fault without requiring memory page violations.

---

## E Function

Completed source code saved in `04_sum_function.s`:
```assembly
sum_array:
    addi t0, x0, 0        # sum = 0
    addi t1, x0, 0        # i = 0
    addi t2, a0, 0        # ptr = base
sum_loop:
    beq  t1, a1, sum_done # Check condition BEFORE loading
    lw   t3, 0(t2)        # Load word from memory
    add  t0, t0, t3       # sum += element
    addi t2, t2, 4        # advance pointer by 4 bytes (1 word)
    addi t1, t1, 1        # advance index i by 1
    jal  x0, sum_loop     # repeat
sum_done:
    addi a0, t0, 0        # return sum in a0
    jalr ra               # return to caller (after_call)
```

### Verification Results
- **Return value a0:**
  - $n=0 \implies a0 = 0$
  - $n=1 \implies a0 = 3$
  - $n=2 \implies a0 = 2$
  - $n=3 \implies a0 = 6$
- **Preserved registers:**
  - `s0` = `123` (`0x0000007b`) — preserved
  - `s1` = `456` (`0x000001c8`) — preserved
  - `sp` = `0x7ffffff0` — 16-byte aligned and preserved
- **Address in ra at function entry:** Address of `after_call` instruction (`0x00000054` in Ripes).
- **Instruction that returns to it:** `jalr ra` (or `jalr x0, ra, 0`), which branches to the address held in `ra`.

### Questions
- **E1 — Why can this leaf function avoid a stack frame?**
  A leaf function makes no nested function calls. Therefore, its return address in register `ra` is never overwritten and remains valid throughout. Furthermore, the function uses only caller-saved temporary registers (`t0..t3`), without modifying any callee-saved registers (`s0..s11`) or needing local stack variables. With `ra` intact and no callee-saved state to restore, allocating a stack frame (modifying `sp`) is completely unnecessary.
- **E2 — Why is replacing t3 with x8 unsafe if the function does not save and restore x8?**
  In the RISC-V calling convention (ABI), register `x8` is designated as `s0` (callee-saved register). Callers assume `s0` remains preserved across function calls (e.g., caller initializes `s0 = 123`). If `sum_array` overwrites `x8` without pushing it to the stack at entry and popping it before exit, the caller's `s0` is corrupted upon return, violating the ABI contract.

---

## Exit ticket

1. **What does `lw x8, 0(x7)` place in `x8`?**
   It places the 32-bit data word stored in memory at the effective address (`x7 + 0`), NOT the address itself. In our trace, when $x7 = 0x10000000$, `lw` places the value 3 into $x8$, while $x7$ continues holding the address.
2. **Does `addi x7, x7, 4` read memory? Explain using your observed `x8`.**
   No. `addi` is an ALU arithmetic instruction operating purely within the CPU register file; it does not access the memory bus. Observed register $x8$ remains completely unchanged when `addi x7, x7, 4` executes.
3. **How many real instructions execute in Task C when n=2, under our boundary?**
   Exactly 16 real instructions. Derived from the formula: $\text{Count} = 3 + (n + 1) + 5n = 6n + 4$. For $n = 2$, $\text{Count} = 6(2) + 4 = 16$.
4. **What observation proves that n=0 performs no array load?**
   (1) Register $x8$ retains its pre-loop sentinel value `0x00000000` throughout execution; (2) Pointer register $x7$ remains unchanged at base address $B$; and (3) Exactly 4 dynamic instructions retire from `trace_start` to `end` (3 initializations + 1 taken `beq`), confirming that `lw` was never executed.
