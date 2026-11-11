import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

doc = docx.Document('Lecture3_Lab_Student_Handout_BACKUP.docx')

# 1. Update Header
for p in doc.paragraphs:
    if 'Name ____________________' in p.text:
        p.text = 'Name: Student Handout Solution       Student ID: RV32-LAB3-2026       Date: November 11, 2026'
        for run in p.runs:
            run.font.bold = True
            run.font.color.rgb = RGBColor(0, 51, 102)

# Helper function to style table cell
def set_cell(cell, text, bold=False, color=RGBColor(0, 0, 0)):
    cell.text = text
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if len(p.runs) > 0:
        p.runs[0].font.name = 'Calibri'
        p.runs[0].font.size = Pt(9.5)
        p.runs[0].font.bold = bold
        p.runs[0].font.color.rgb = color

# 2. Table 2: Task A Register Trace
t2 = doc.tables[2]
t2_data = [
    ['Initial state', '9', '4', '0', '0'],
    ['sub x7, x5, x6', '9', '4', '5', '0'],
    ['addi x5, x7, -1', '4', '4', '5', '0'],
    ['add x6, x5, x7', '4', '9', '5', '0'],
    ['add x0, x5, x6', '4', '9', '5', '0']
]
for r_idx, row in enumerate(t2_data):
    for c_idx, val in enumerate(row[1:], start=1):
        set_cell(t2.rows[r_idx+1].cells[c_idx], val, bold=True, color=RGBColor(0, 70, 150))

# 3. Table 3: Task B Memory Byte Transfers
t3 = doc.tables[3]
t3_data = [
    ['After sw', '0x78', '0x56', '0x34', '0x12'],
    ['After sb', '0x78', '0xEF', '0x34', '0x12']
]
for r_idx, row in enumerate(t3_data):
    for c_idx, val in enumerate(row[1:], start=1):
        set_cell(t3.rows[r_idx+1].cells[c_idx], val, bold=True, color=RGBColor(0, 70, 150))

# 4. Table 5: Task C Snapshots before beq for n=3
t5 = doc.tables[5]
t5_data = [
    ['0', '0', '0', 'B (0x10000000)', '0 (sentinel)'],
    ['1', '3', '1', 'B+4 (0x10000004)', '3'],
    ['2', '2', '2', 'B+8 (0x10000008)', '-1'],
    ['3', '6', '3', 'B+12 (0x1000000C)', '4']
]
for r_idx, row in enumerate(t5_data):
    for c_idx, val in enumerate(row[1:], start=1):
        set_cell(t5.rows[r_idx+1].cells[c_idx], val, bold=True, color=RGBColor(0, 70, 150))

# 5. Table 6: Task C Boundary Tests
t6 = doc.tables[6]
t6_data = [
    ['0', '0', '0', 'B (0x10000000)', 'None (no load)', '4'],
    ['1', '3', '1', 'B+4 (0x10000004)', 'B (0x10000000)', '10'],
    ['2', '2', '2', 'B+8 (0x10000008)', 'B+4 (0x10000004)', '16'],
    ['3', '6', '3', 'B+12 (0x1000000C)', 'B+8 (0x10000008)', '22']
]
for r_idx, row in enumerate(t6_data):
    for c_idx, val in enumerate(row[1:], start=1):
        set_cell(t6.rows[r_idx+1].cells[c_idx], val, bold=True, color=RGBColor(0, 70, 150))

# 6. Table 7: Task C Formula Derivation
t7 = doc.tables[7]
t7_data = [
    '3 (initialization: addi x5, addi x6, addi x7)',
    'n + 1 (condition test: beq x6, x11, end; evaluated n times true + 1 exit)',
    '5n (loop body: lw, add, addi x7, addi x6, jal; 5 instructions * n iterations)',
    '6n + 4  (Verification: n=0: 4; n=1: 10; n=2: 16; n=3: 22)'
]
for r_idx, val in enumerate(t7_data):
    set_cell(t7.rows[r_idx+1].cells[1], val, bold=True, color=RGBColor(0, 70, 150))

# 7. Table 8: Task D Debugging
t8 = doc.tables[8]
t8_data = [
    [
        'In iteration 2 (x6=1), pointer x7 is B+1 instead of B+4. Instruction lw x8, 0(x7) performs an unaligned word load across byte boundaries [B+1..B+4], loading corrupted data (0x0400ffff instead of -1) and yielding an incorrect sum of 3.',
        'Repair: Change addi x7, x7, 1 back to addi x7, x7, 4 (stride must be 4 bytes per 32-bit word). Retest: x7 advances cleanly by 4 bytes; final sum correctly equals 6.'
    ],
    [
        'For n=0 with sentinel x8=0, lw x8, 0(x7) executes unconditionally BEFORE beq tests the length. Even though n=0 requires zero memory loads, x8 is erroneously overwritten with array[0]=3 (an illegal speculative read).',
        'Repair: Move beq x6, x11, end back BEFORE lw x8, 0(x7) (check-before-access paradigm). Retest: with n=0, loop branches immediately to end; x8 remains sentinel 0.'
    ],
    [
        'In iteration 2, x6 remains 0 instead of 1, while x7 advances to B+4. Because x6 never increments, the termination condition x6 == x11 (3) is never satisfied, causing an infinite loop that reads past array bounds.',
        'Repair: Restore addi x6, x6, 1 inside the loop body. Retest: index increments properly each iteration; loop terminates cleanly after 3 iterations with sum=6.'
    ]
]
for r_idx, row in enumerate(t8_data):
    set_cell(t8.rows[r_idx+1].cells[1], row[0], bold=False, color=RGBColor(0, 0, 0))
    set_cell(t8.rows[r_idx+1].cells[2], row[1], bold=False, color=RGBColor(0, 70, 150))

# Now let's update specific paragraphs
p_map = {}
for i, p in enumerate(doc.paragraphs):
    text = p.text.strip()
    p_map[i] = text

# Helper to format answer paragraph
def fill_answer(p, answer_text):
    p.text = answer_text
    p.runs[0].font.name = 'Calibri'
    p.runs[0].font.size = Pt(10)
    p.runs[0].font.color.rgb = RGBColor(0, 40, 120)

# P041: PC before sub
doc.paragraphs[41].text = 'PC before sub: 0x0000000C (12)          PC after sub: 0x00000010 (16)'
for r in doc.paragraphs[41].runs:
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 70, 150)

# P042: Explanation of PC and machine code
fill_answer(doc.paragraphs[42],
    'Explanation: In RV32I, all base instructions are strictly 4 bytes (32 bits) wide, and memory is byte-addressed. Sequential execution advances the Program Counter by exactly +4 bytes (from 0x0C to 0x10). The machine-code word for "sub x7, x5, x6" is 0x006283b3 (funct7=0x00, rs2=x6/00110, rs1=x5/00101, funct3=0x0, rd=x7/00111, opcode=0x33/0110011). Assembly mnemonics and 32-bit machine words are two equivalent representations of the same operation: assembly is human-readable symbolic text, while the machine word is the exact binary encoding executed by processor hardware.')

# P044 & P045: Question A1
doc.paragraphs[44].text = 'Answer: Instructions execute in strict sequential program order. The second instruction (addi x5, x7, -1) computes 5 - 1 = 4 and commits this value into destination register x5 before the third instruction (add x6, x5, x7) reads x5 as its source operand. In hardware datapaths, the updated value is available immediately.'
for r in doc.paragraphs[44].runs:
    r.font.color.rgb = RGBColor(0, 40, 120)
doc.paragraphs[45].text = ''

# P047 & P048: Question A2
doc.paragraphs[47].text = 'Answer: In the RISC-V RV32I architecture, register x0 is hardwired to constant zero. Although the ALU calculates 4 + 9 = 13, any write to register x0 is permanently discarded by hardware logic, ensuring x0 always reads 0x00000000.'
for r in doc.paragraphs[47].runs:
    r.font.color.rgb = RGBColor(0, 40, 120)
doc.paragraphs[48].text = ''

# P069: Actual M and t3, t4, t5
doc.paragraphs[69].text = 'Actual M: 0x10000000    t3: 0x1234EF78    t4: 0xFFFFFFEF (-17 signed)    t5: 0x000000EF (239 unsigned)'
for r in doc.paragraphs[69].runs:
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 70, 150)

# P071 & P072: Question B1
doc.paragraphs[71].text = 'Answer: Both instructions read the exact same 8-bit byte from address M+1, which is 0xEF (binary 1110 1111). "lb" (load byte, signed) performs sign extension: it copies bit 7 (which is 1) across bits 31..8, resulting in 0xFFFFFFEF (signed decimal -17). In contrast, "lbu" (load byte unsigned) performs zero extension: it fills bits 31..8 with zeros regardless of bit 7, yielding 0x000000EF (unsigned decimal 239).'
for r in doc.paragraphs[71].runs:
    r.font.color.rgb = RGBColor(0, 40, 120)
doc.paragraphs[72].text = ''

# P074 & P075: Question B2
doc.paragraphs[74].text = 'Answer: Neither sw nor sb changes registers t0 or t1. Store instructions transfer data from CPU registers into memory; they do not write to general-purpose registers. "sw" writes a full 32-bit word (4 contiguous bytes: M through M+3), while "sb" writes exactly 1 byte (8 bits: M+1 only).'
for r in doc.paragraphs[74].runs:
    r.font.color.rgb = RGBColor(0, 40, 120)
doc.paragraphs[75].text = ''

# P111: Question C1
doc.paragraphs[111].text = 'Answer: The "beq x6, x11, end" instruction prevents the load. Since x6 = 0 and x11 = 0 initially, the equality condition is true on the very first evaluation, jumping directly to "end" and skipping "lw x8, 0(x7)". Evidence: (1) register x8 retains its initial pre-loop sentinel value 0x00000000; (2) pointer register x7 remains at base address B without advancing; and (3) exactly 4 dynamic instructions retire from trace_start to end.'
for r in doc.paragraphs[111].runs:
    r.font.color.rgb = RGBColor(0, 40, 120)

# P113: Question C2
doc.paragraphs[113].text = 'Answer: In iteration 3, after "lw" loads the final element (array[2]=4 at address B+8), the instruction "addi x7, x7, 4" advances the pointer to B+12 in preparation for a hypothetical next iteration. Then index x6 increments to 3 and branches back to "loop". At the condition test "beq x6, x11, end", 3 == 3 evaluates to true and branches to "end" before any load occurs. Advancing x7 is speculative for the next iteration, but no memory access occurs at B+12.'
for r in doc.paragraphs[113].runs:
    r.font.color.rgb = RGBColor(0, 40, 120)

# P115: Transfer test
doc.paragraphs[115].text = 'Transfer test results (array=[5, -2, 9], n=2): Predicted sum = 3, Observed sum = 3; Final index x6 = 2; Final pointer x7 = B+8 (0x10000008); Last load address = B+4 (0x10000004); Dynamic instruction count = 6(2)+4 = 16. The value 9 is NOT read from memory because n=2 restricts execution to indices 0 and 1; the loop cleanly terminates when index x6 reaches 2 before attempting to load index 2 (value 9 at B+8).'
for r in doc.paragraphs[115].runs:
    r.font.color.rgb = RGBColor(0, 40, 120)

# P136: Question D4
doc.paragraphs[136].text = 'Answer: Test with n = 0 (the empty array boundary test) with an explicit pre-cleared sentinel in destination register x8 (e.g., x8 = 0). For an empty collection (n=0), zero elements exist, so a correct loop must never touch memory. If "lw" is placed before the condition check, running with n=0 immediately executes the load instruction and alters the sentinel register value, instantly exposing the premature read without requiring memory page faults.'
for r in doc.paragraphs[136].runs:
    r.font.color.rgb = RGBColor(0, 40, 120)

# P148 & P149: Question E1
doc.paragraphs[148].text = 'Answer: A leaf function is a function that makes no nested function calls. Consequently, its return address in register "ra" is never overwritten and can be retained in "ra" throughout execution. Furthermore, our function uses exclusively temporary caller-saved registers (t0, t1, t2, t3) without modifying any callee-saved registers (s0..s11) or spilling variables. Because ra remains intact and no callee-saved registers are touched, allocating a stack frame (adjusting sp) is entirely unnecessary.'
for r in doc.paragraphs[148].runs:
    r.font.color.rgb = RGBColor(0, 40, 120)
doc.paragraphs[149].text = ''

# P151 & P152: Question E2
doc.paragraphs[151].text = 'Answer: In the standard RISC-V calling convention (ABI), register x8 is designated as "s0" (a callee-saved register / frame pointer). The ABI contract mandates that any function modifying a callee-saved register must preserve its value across the call by saving it onto the stack at function entry and restoring it before returning. In our caller, s0 holds 123. If sum_array overwrites x8 without saving and restoring it, the caller\'s s0 is corrupted upon return, violating the ABI contract.'
for r in doc.paragraphs[151].runs:
    r.font.color.rgb = RGBColor(0, 40, 120)
doc.paragraphs[152].text = ''

# Exit ticket questions:
# P167:
p167 = doc.paragraphs[167]
p167_ans = doc.add_paragraph('Answer: It places the 32-bit data word stored in memory at the effective address (x7 + 0), NOT the address itself. In our trace, when x7 = 0x10000000, lw places the value 3 into x8, while x7 continues holding the address.')
p167_ans.runs[0].font.color.rgb = RGBColor(0, 40, 120)
p167._p.addnext(p167_ans._p)

# P168:
p168 = doc.paragraphs[168]
p168_ans = doc.add_paragraph('Answer: No. "addi" is an arithmetic ALU instruction that performs integer register addition purely within the CPU datapath; it does not generate a memory address or activate data memory read lines. Observed register x8 remains completely unchanged when addi x7, x7, 4 executes.')
p168_ans.runs[0].font.color.rgb = RGBColor(0, 40, 120)
p168._p.addnext(p168_ans._p)

# P169:
p169 = doc.paragraphs[169]
p169_ans = doc.add_paragraph('Answer: Exactly 16 real instructions. Derived from the formula: 3 (initialization) + (n + 1) (condition tests) + 5n (loop body & jump) = 6n + 4. For n = 2, count = 6(2) + 4 = 16 instructions.')
p169_ans.runs[0].font.color.rgb = RGBColor(0, 40, 120)
p169._p.addnext(p169_ans._p)

# P170:
p170 = doc.paragraphs[170]
p170_ans = doc.add_paragraph('Answer: (1) Register x8 retains its initial pre-loop sentinel value of 0x00000000 throughout execution; (2) Pointer register x7 never advances beyond base address B; and (3) The total instruction count between trace_start and end is exactly 4 (3 initialization instructions + 1 taken beq), proving that "lw x8, 0(x7)" was never fetched or retired.')
p170_ans.runs[0].font.color.rgb = RGBColor(0, 40, 120)
p170._p.addnext(p170_ans._p)

# 8. Insert Proof Screenshots
def insert_screenshot(target_p, img_path, caption_text):
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_img = p_img.add_run()
    run_img.add_picture(img_path, width=Inches(6.0))
    
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_cap = p_cap.add_run(caption_text)
    run_cap.font.name = 'Calibri'
    run_cap.font.size = Pt(9.5)
    run_cap.font.italic = True
    run_cap.font.color.rgb = RGBColor(80, 80, 80)
    
    target_p._p.addnext(p_cap._p)
    target_p._p.addnext(p_img._p)

# Insert after Task A (P049)
insert_screenshot(doc.paragraphs[49], 'screenshot_task_a.png', 'Figure A: Ripes execution proof for Task A (01_register_trace.s) showing register updates and 10 instructions retired.')

# Insert after Task B (P075)
insert_screenshot(doc.paragraphs[75], 'screenshot_task_b.png', 'Figure B: Ripes execution proof for Task B (02_memory_bytes.s) showing t3=0x1234ef78, t4=0xffffffef (-17), and t5=0x000000ef (239).')

# Insert after Task C (P115)
insert_screenshot(doc.paragraphs[115], 'screenshot_task_c_n0.png', 'Figure C2: Ripes execution proof for Task C with n=0 (empty array boundary test; x8 remains sentinel 0).')
insert_screenshot(doc.paragraphs[115], 'screenshot_task_c_n3.png', 'Figure C1: Ripes execution proof for Task C with n=3 (array sum = 6, pointer = B+12, 29 total retired cycles).')

# Insert after Task D (P137)
insert_screenshot(doc.paragraphs[137], 'screenshot_task_d2_read_before_check.png', 'Figure D2: Ripes execution proof for Mutation D2 (premature read: x8 overwritten with 3 when n=0).')
insert_screenshot(doc.paragraphs[137], 'screenshot_task_d1_stride_error.png', 'Figure D1: Ripes execution proof for Mutation D1 (wrong stride +1 instead of +4 causing unaligned read and wrong sum).')

# Insert after Task E (P153)
insert_screenshot(doc.paragraphs[153], 'screenshot_task_e_function_n0.png', 'Figure E2: Ripes execution proof for Task E function with n=0 (a0=0, caller s0=123 and s1=456 preserved).')
insert_screenshot(doc.paragraphs[153], 'screenshot_task_e_function_n3.png', 'Figure E1: Ripes execution proof for Task E function with n=3 (a0=6, caller s0=123, s1=456, and sp preserved).')

# Save updated docx
doc.save('Lecture3_Lab_Student_Handout.docx')
print('Successfully updated Lecture3_Lab_Student_Handout.docx with all solutions and screenshots!')

