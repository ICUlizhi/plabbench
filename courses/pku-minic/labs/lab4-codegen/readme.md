# Lab 4: 代码生成 (Code Generation)

## 实验概述

将 Koopa IR 转换为 RISC-V 汇编代码。

## 文档链接

- [Lab 4 文档](https://pku-minic.github.io/online-doc/#/labs/lab4/)

## Skill 文件

查看 [`../../skills/lab4-codegen/CLAUDE.md`](../../skills/lab4-codegen/CLAUDE.md) 获取详细的实现指南。

## 实验目标

1. 理解 RISC-V 指令集
2. 实现指令选择
3. 管理寄存器和栈帧
4. 生成可运行的 RISC-V 汇编

## 目标架构

- **RISC-V 64**: rv64gc
- **调用约定**: LP64
- **工具链**: riscv64-linux-gnu-gcc

## RISC-V 汇编示例

### 输入 (Koopa IR)
```
fun @main(): i32 {
%entry:
  ret 42
}
```

### 输出 (RISC-V 汇编)
```asm
  .globl main
main:
  addi sp, sp, -16
  sw ra, 12(sp)
  li a0, 42
  lw ra, 12(sp)
  addi sp, sp, 16
  ret
```

## 运行测试

```bash
# 生成汇编
cd lab4-codegen/source
./compiler test.c > test.S

# 编译汇编
riscv64-linux-gnu-gcc -static test.S -o test

# 运行
qemu-riscv64 ./test
echo $?
```

## 提交要求

- 完整的代码生成器
- 实验报告（寄存器分配策略和栈帧管理）

## 参考资源

- [RISC-V 指令集手册](https://riscv.org/technical/specifications/)
- [RISC-V Assembly Programmer's Manual](https://github.com/riscv/riscv-asm-manual)
