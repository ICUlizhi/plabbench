# Lab 4: 代码生成 (Code Generation)

## 实验目标

将 Koopa IR 转换为 RISC-V 汇编代码。

## 核心概念

### 编译器后端流程

```
Koopa IR → 指令选择 → 寄存器分配 → 栈帧管理 → RISC-V 汇编
```

### RISC-V 基础

RISC-V 是精简指令集架构，有 32 个通用寄存器（x0-x31）：

| 寄存器 | 名称 | 用途 |
|--------|------|------|
| x0 | zero | 恒为 0 |
| x1 | ra | 返回地址 |
| x2 | sp | 栈指针 |
| x3 | gp | 全局指针 |
| x4 | tp | 线程指针 |
| x5-x7 | t0-t2 | 临时寄存器 |
| x8 | s0/fp | 保存寄存器/帧指针 |
| x9 | s1 | 保存寄存器 |
| x10-x17 | a0-a7 | 函数参数/返回值 |
| x18-x27 | s2-s11 | 保存寄存器 |
| x28-x31 | t3-t6 | 临时寄存器 |

### 指令格式

```asm
# 算术运算
add  rd, rs1, rs2    # rd = rs1 + rs2
sub  rd, rs1, rs2    # rd = rs1 - rs2
mul  rd, rs1, rs2    # rd = rs1 * rs2
div  rd, rs1, rs2    # rd = rs1 / rs2
rem  rd, rs1, rs2    # rd = rs1 % rs2
neg  rd, rs          # rd = -rs

# 立即数
addi rd, rs, imm     # rd = rs + imm
li   rd, imm         # rd = imm (伪指令)

# 内存访问
lw   rd, offset(rs)  # rd = *(rs + offset)
sw   rs2, offset(rs1) # *(rs1 + offset) = rs2

# 分支
beq  rs1, rs2, label # if (rs1 == rs2) goto label
bne  rs1, rs2, label # if (rs1 != rs2) goto label
blt  rs1, rs2, label # if (rs1 < rs2) goto label
bge  rs1, rs2, label # if (rs1 >= rs2) goto label

# 跳转
jal  rd, label       # rd = PC + 4; goto label
jalr rd, offset(rs)  # rd = PC + 4; goto rs + offset
j    label           # goto label (伪指令)
ret                  # return (伪指令: jalr x0, 0(x1))

# 比较
seqz rd, rs          # rd = (rs == 0)
snez rd, rs          # rd = (rs != 0)
slt  rd, rs1, rs2    # rd = (rs1 < rs2)
sgt  rd, rs1, rs2    # rd = (rs1 > rs2)

# 逻辑
xori rd, rs, -1      # rd = ~rs (not)
```

## 代码生成实现

### 整体结构

```c
typedef struct {
    FILE *out;
    int stack_size;      // 栈帧大小
    int stack_offset;    // 当前栈偏移
} CodeGenContext;

void generate_asm(KoopaProgram *prog, FILE *out) {
    CodeGenContext ctx = {.out = out};

    // 生成数据段（全局变量）
    fprintf(out, "  .data\n");
    for (GlobalValue *g = prog->globals; g; g = g->next) {
        gen_global(&ctx, g);
    }

    // 生成代码段
    fprintf(out, "  .text\n");
    for (Function *f = prog->functions; f; f = f->next) {
        gen_function(&ctx, f);
    }
}
```

### 函数生成

```c
void gen_function(CodeGenContext *ctx, Function *func) {
    // 函数标签
    fprintf(ctx->out, "  .globl %s\n", func->name);
    fprintf(ctx->out, "%s:\n", func->name);

    // 函数序言 (prologue)
    fprintf(ctx->out, "  addi sp, sp, -%d\n", func->stack_size);
    fprintf(ctx->out, "  sw ra, %d(sp)\n", func->stack_size - 4);

    // 计算栈帧大小
    int stack_size = calculate_stack_size(func);
    // 对齐到 16 字节
    stack_size = (stack_size + 15) / 16 * 16;
    ctx->stack_size = stack_size;

    // 生成基本块
    for (BasicBlock *bb = func->blocks; bb; bb = bb->next) {
        fprintf(ctx->out, "%s_%s:\n", func->name, bb->name);
        gen_basic_block(ctx, bb);
    }
}

void gen_basic_block(CodeGenContext *ctx, BasicBlock *bb) {
    for (Instruction *inst = bb->insts; inst; inst = inst->next) {
        gen_instruction(ctx, inst);
    }
}
```

### 指令生成

```c
void gen_instruction(CodeGenContext *ctx, Instruction *inst) {
    switch (inst->kind) {
        case INST_ALLOC:
            // alloc 已在栈帧分配时处理
            break;

        case INST_STORE: {
            const char *src = get_value_reg(ctx, inst->src);
            int offset = get_alloc_offset(ctx, inst->dest);
            fprintf(ctx->out, "  sw %s, %d(sp)\n", src, offset);
            break;
        }

        case INST_LOAD: {
            const char *dest = get_temp_reg(ctx, inst);
            int offset = get_alloc_offset(ctx, inst->src);
            fprintf(ctx->out, "  lw %s, %d(sp)\n", dest, offset);
            break;
        }

        case INST_BINARY: {
            const char *lhs = get_value_reg(ctx, inst->lhs);
            const char *rhs = get_value_reg(ctx, inst->rhs);
            const char *dest = get_temp_reg(ctx, inst);

            switch (inst->op) {
                case OP_ADD:
                    fprintf(ctx->out, "  add %s, %s, %s\n", dest, lhs, rhs);
                    break;
                case OP_SUB:
                    fprintf(ctx->out, "  sub %s, %s, %s\n", dest, lhs, rhs);
                    break;
                case OP_MUL:
                    fprintf(ctx->out, "  mul %s, %s, %s\n", dest, lhs, rhs);
                    break;
                case OP_DIV:
                    fprintf(ctx->out, "  div %s, %s, %s\n", dest, lhs, rhs);
                    break;
                case OP_MOD:
                    fprintf(ctx->out, "  rem %s, %s, %s\n", dest, lhs, rhs);
                    break;
                case OP_EQ:
                    fprintf(ctx->out, "  xor %s, %s, %s\n", dest, lhs, rhs);
                    fprintf(ctx->out, "  seqz %s, %s\n", dest, dest);
                    break;
                case OP_NE:
                    fprintf(ctx->out, "  xor %s, %s, %s\n", dest, lhs, rhs);
                    fprintf(ctx->out, "  snez %s, %s\n", dest, dest);
                    break;
                case OP_LT:
                    fprintf(ctx->out, "  slt %s, %s, %s\n", dest, lhs, rhs);
                    break;
                case OP_GT:
                    fprintf(ctx->out, "  sgt %s, %s, %s\n", dest, lhs, rhs);
                    break;
                case OP_LE:
                    // a <= b 等价于 !(a > b)
                    fprintf(ctx->out, "  sgt %s, %s, %s\n", dest, lhs, rhs);
                    fprintf(ctx->out, "  seqz %s, %s\n", dest, dest);
                    break;
                case OP_GE:
                    // a >= b 等价于 !(a < b)
                    fprintf(ctx->out, "  slt %s, %s, %s\n", dest, lhs, rhs);
                    fprintf(ctx->out, "  seqz %s, %s\n", dest, dest);
                    break;
            }
            break;
        }

        case INST_RET: {
            if (inst->has_value) {
                const char *val = get_value_reg(ctx, inst->value);
                fprintf(ctx->out, "  mv a0, %s\n", val);  // 返回值放入 a0
            }
            // 函数尾声 (epilogue)
            fprintf(ctx->out, "  lw ra, %d(sp)\n", ctx->stack_size - 4);
            fprintf(ctx->out, "  addi sp, sp, %d\n", ctx->stack_size);
            fprintf(ctx->out, "  ret\n");
            break;
        }

        case INST_BRANCH: {
            const char *cond = get_value_reg(ctx, inst->cond);
            fprintf(ctx->out, "  bnez %s, %s\n", cond, inst->true_label);
            fprintf(ctx->out, "  j %s\n", inst->false_label);
            break;
        }

        case INST_JUMP:
            fprintf(ctx->out, "  j %s\n", inst->label);
            break;
    }
}
```

### 寄存器分配（简单方案）

```c
// 简单的寄存器分配：所有值都分配到临时寄存器 t0-t6
// 更复杂的实现可以使用图着色算法

const char *get_temp_reg(CodeGenContext *ctx, Value *val) {
    static int reg_counter = 0;
    const char *regs[] = {"t0", "t1", "t2", "t3", "t4", "t5", "t6"};

    // 为值分配寄存器
    if (val->reg == NULL) {
        val->reg = regs[reg_counter % 7];
        reg_counter++;
    }
    return val->reg;
}

const char *get_value_reg(CodeGenContext *ctx, Value *val) {
    if (val->kind == VALUE_INT) {
        // 整数立即数
        fprintf(ctx->out, "  li t6, %d\n", val->int_val);
        return "t6";
    }
    return get_temp_reg(ctx, val);
}

int get_alloc_offset(CodeGenContext *ctx, Value *alloc) {
    return alloc->stack_offset;
}
```

### 栈帧管理

```c
int calculate_stack_size(Function *func) {
    int size = 0;

    // 为 alloc 指令分配空间
    for (BasicBlock *bb = func->blocks; bb; bb = bb->next) {
        for (Instruction *inst = bb->insts; inst; inst = inst->next) {
            if (inst->kind == INST_ALLOC) {
                inst->dest->stack_offset = size;
                size += 4;  // i32 占 4 字节
            }
        }
    }

    // 保存 ra 和寄存器
    size += 4;  // ra

    // 对齐到 16 字节
    return (size + 15) / 16 * 16;
}
```

## 完整示例

### 输入 (Koopa IR)

```
fun @main(): i32 {
%entry:
  @x = alloc i32
  store 42, @x
  %0 = load @x
  ret %0
}
```

### 输出 (RISC-V 汇编)

```asm
  .globl main
main:
  addi sp, sp, -16
  sw ra, 12(sp)

  li t0, 42
  sw t0, 8(sp)       # store 42 to @x
  lw a0, 8(sp)       # load @x to a0

  lw ra, 12(sp)
  addi sp, sp, 16
  ret
```

## 常见陷阱

### 1. 寄存器保存

```asm
# 错误：修改 t0 但调用者期望 t0 不变
foo:
  addi t0, t0, 1
  ret

# 正确：使用 s0-s11 或保存/恢复
foo:
  addi sp, sp, -8
  sw s0, 0(sp)
  addi s0, s0, 1
  lw s0, 0(sp)
  addi sp, sp, 8
  ret
```

### 2. 栈对齐

```asm
# 错误：栈未 16 字节对齐
addi sp, sp, -12

# 正确
addi sp, sp, -16
```

### 3. 立即数范围

```asm
# 错误：addi 立即数范围是 -2048~2047
addi t0, x0, 100000

# 正确
li t0, 100000   # 拆分为 lui + addi
```

### 4. 返回值

```asm
# 返回值必须放在 a0
ret_value:
  mv a0, t0    # 将结果放入 a0
  ret
```

## 测试方法

```bash
# 1. 生成汇编
./compiler test.c > test.S

# 2. 编译汇编
riscv64-linux-gnu-gcc -static test.S -o test

# 3. 运行
qemu-riscv64 ./test
echo $?  # 查看返回值
```

## 调试技巧

### 查看汇编

```bash
riscv64-linux-gnu-objdump -d test
```

### GDB 调试

```bash
qemu-riscv64 -g 1234 ./test &
riscv64-linux-gnu-gdb ./test
(gdb) target remote localhost:1234
(gdb) break main
(gdb) continue
```

## 参考资源

- [Lab 4 文档](https://pku-minic.github.io/online-doc/#/labs/lab4/)
- [RISC-V 指令集手册](https://riscv.org/technical/specifications/)
- [RISC-V Assembly Programmer's Manual](https://github.com/riscv/riscv-asm-manual)
