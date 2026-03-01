# Lab 5: 代码优化 (Optimization)

## 实验目标

实现编译器优化，提高生成代码的性能。

## 核心概念

### 为什么要优化

```c
// 未优化代码
int foo() {
    int a = 1 + 2;      // 可以在编译时计算
    int b = a * 0;      // 结果总是 0
    if (0) {            // 永远不会执行
        return 1;
    }
    return b;           // 返回 0
}

// 优化后
int foo() {
    return 0;
}
```

### 优化分类

| 类别 | 描述 | 示例 |
|------|------|------|
| 机器无关优化 | 在中间表示上进行 | 常量折叠、死代码消除 |
| 机器相关优化 | 针对目标架构 | 寄存器分配、指令选择 |
| 局部优化 | 基本块内 | 窥孔优化 |
| 全局优化 | 跨基本块 | 数据流分析 |

## 基本块与控制流图

### 基本块 (Basic Block)

基本块是最大连续的指令序列，只有一个入口和一个出口。

```
entry:
  x = 1
  y = 2
  if x < y goto L1    <- 出口（分支）
  goto L2

L1:
  z = x + y           <- 入口
  goto exit

L2:
  z = x - y           <- 入口
  goto exit

exit:
  return z            <- 入口
```

### 控制流图 (CFG)

```
    [entry]
       |
       v
    [block1] ---> [block2]
       |              |
       v              v
    [block3] <------+
       |
       v
    [exit]
```

### 构建 CFG

```c
typedef struct BasicBlock {
    int id;
    Instruction *insts;
    int inst_count;

    // CFG 边
    struct BasicBlock *preds[10];
    int pred_count;
    struct BasicBlock *succs[10];
    int succ_count;
} BasicBlock;

typedef struct CFG {
    BasicBlock **blocks;
    int block_count;
    BasicBlock *entry;
    BasicBlock *exit;
} CFG;

CFG *build_cfg(Function *func) {
    // 1. 识别基本块边界（标签和跳转）
    // 2. 创建基本块
    // 3. 连接基本块形成 CFG
}
```

## 常见优化

### 1. 常量折叠 (Constant Folding)

```c
// 优化前
int x = 1 + 2;
int y = x * 3;

// 优化后
int x = 3;
int y = 9;
```

```c
void constant_folding(Function *func) {
    for (BasicBlock *bb = func->blocks; bb; bb = bb->next) {
        for (Instruction *inst = bb->insts; inst; inst = inst->next) {
            if (is_binary_op(inst)) {
                if (is_constant(inst->lhs) && is_constant(inst->rhs)) {
                    int result = compute(inst->op,
                                       get_const_value(inst->lhs),
                                       get_const_value(inst->rhs));
                    // 替换为常量
                    replace_with_constant(inst, result);
                }
            }
        }
    }
}
```

### 2. 常量传播 (Constant Propagation)

```c
// 优化前
int x = 5;
int y = x + 1;  // 可以知道 x = 5

// 优化后
int x = 5;
int y = 6;
```

### 3. 死代码消除 (Dead Code Elimination)

```c
// 优化前
int x = 1;      // x 从未使用
int y = 2;
return y;

// 优化后
int y = 2;
return y;
```

```c
void dead_code_elimination(Function *func) {
    // 标记所有被使用的值
    bool *used = calloc(value_count, sizeof(bool));

    // 从返回值开始反向遍历
    mark_used(func->return_value, used);

    // 删除未使用的指令
    for (BasicBlock *bb = func->blocks; bb; bb = bb->next) {
        for (Instruction *inst = bb->insts; inst; inst = inst->next) {
            if (!used[inst->id]) {
                remove_instruction(bb, inst);
            }
        }
    }
}
```

### 4. 公共子表达式消除 (CSE)

```c
// 优化前
int x = a + b;
int y = a + b;  // 重复计算

// 优化后
int x = a + b;
int y = x;
```

### 5. 窥孔优化 (Peephole Optimization)

对小的指令窗口进行局部优化：

```asm
# 优化前
addi t0, x0, 0      # t0 = 0

# 优化后
li t0, 0

# 优化前
mv t1, t0
mv t2, t1

# 优化后
mv t2, t0

# 优化前
sw t0, 0(sp)
lw t0, 0(sp)

# 优化后（如果没有其他指令修改内存）
# 删除 lw

# 优化前
beq t0, x0, label

# 优化后
beqz t0, label
```

```c
void peephole_optimize(Function *func) {
    for (BasicBlock *bb = func->blocks; bb; bb = bb->next) {
        for (Instruction *inst = bb->insts; inst; inst = inst->next) {
            // 匹配模式并替换
            if (match_pattern(inst, "addi %r, x0, 0")) {
                replace_with(inst, "mv %r, x0");
            }
            // ... 更多模式
        }
    }
}
```

## 数据流分析

### 到达定义分析 (Reaching Definitions)

```
对于每个程序点，确定哪些定义可能到达此处

IN[B] = 所有前驱的 OUT 的并集
OUT[B] = gen[B] ∪ (IN[B] - kill[B])
```

### 活跃变量分析 (Live Variable Analysis)

```
确定哪些变量的值在程序点之后还可能被使用

OUT[B] = 所有后继的 IN 的并集
IN[B] = use[B] ∪ (OUT[B] - def[B])
```

```c
void live_variable_analysis(CFG *cfg) {
    // 初始化
    for (BasicBlock *bb = cfg->blocks; bb; bb = bb->next) {
        bb->in = empty_set;
        bb->out = empty_set;
    }

    // 迭代直到不动点
    bool changed = true;
    while (changed) {
        changed = false;
        for (BasicBlock *bb = cfg->blocks; bb; bb = bb->next) {
            BitSet old_in = bb->in;

            // OUT[B] = ∪ IN[succ]
            bb->out = empty_set;
            for (int i = 0; i < bb->succ_count; i++) {
                bb->out = union_set(bb->out, bb->succs[i]->in);
            }

            // IN[B] = use[B] ∪ (OUT[B] - def[B])
            bb->in = union_set(bb->use, difference_set(bb->out, bb->def));

            if (!equal_set(bb->in, old_in)) {
                changed = true;
            }
        }
    }
}
```

### 应用：寄存器分配

知道变量的活跃区间，可以更好地分配寄存器。

## SSA 形式 (静态单赋值)

SSA 形式确保每个变量只被赋值一次。

```c
// 原始代码
int x = 1;
if (cond) {
    x = 2;
} else {
    x = 3;
}
return x;

// SSA 形式
int x1 = 1;
if (cond) {
    x2 = 2;
} else {
    x3 = 3;
}
x4 = φ(x2, x3);  // phi 函数
return x4;
```

## 优化框架

```c
void optimize(Function *func) {
    // 构建 CFG
    CFG *cfg = build_cfg(func);

    // 机器无关优化
    constant_folding(func);
    constant_propagation(func);
    dead_code_elimination(func);

    // 构建 SSA（可选）
    // convert_to_ssa(func);

    // 数据流分析
    live_variable_analysis(cfg);

    // 寄存器分配优化
    allocate_registers(func);

    // 机器相关优化
    peephole_optimize(func);
}
```

## 常见陷阱

### 1. 优化改变语义

```c
// 未定义行为可以优化，但要小心
int x = 1 / 0;  // 可以删除（未定义）
```

### 2. 别名分析

```c
int *p = &x;
int *q = &x;
*p = 1;
*q = 2;  // 是否会影响 *p？
```

### 3. 优化顺序

某些优化可能开启其他优化的机会，需要多次遍历。

### 4. 编译时间

复杂的优化可能显著增加编译时间。

## 调试技巧

### 打印优化前后的 IR

```c
void dump_ir(Function *func, const char *phase) {
    printf("=== %s ===\n", phase);
    print_ir(func);
}

// 使用
dump_ir(func, "before optimization");
optimize(func);
dump_ir(func, "after optimization");
```

### 验证优化正确性

```bash
# 比较优化前后的输出
./compiler -O0 test.c > test0.S
./compiler -O1 test.c > test1.S

# 编译并运行
riscv64-linux-gnu-gcc -static test0.S -o test0
riscv64-linux-gnu-gcc -static test1.S -o test1
qemu-riscv64 ./test0
echo $?
qemu-riscv64 ./test1
echo $?
```

### 性能测试

```bash
# 测量执行时间
time qemu-riscv64 ./test0
time qemu-riscv64 ./test1

# 测量代码大小
riscv64-linux-gnu-size test0iscv64-linux-gnu-size test1
```

## 参考资源

- [Lab 5 文档](https://pku-minic.github.io/online-doc/#/labs/lab5/)
- [Engineering a Compiler](https://www.cs.princeton.edu/~appel/modern/)
- [LLVM Optimization](https://llvm.org/docs/Passes.html)
- [SSA Book](https://pfalcon.github.io/ssabook/)
