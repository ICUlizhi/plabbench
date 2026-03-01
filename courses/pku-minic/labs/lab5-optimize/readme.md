# Lab 5: 代码优化 (Optimization)

## 实验概述

实现编译器优化，提高生成代码的性能。

## 文档链接

- [Lab 5 文档](https://pku-minic.github.io/online-doc/#/labs/lab5/)

## Skill 文件

查看 [`../../skills/lab5-optimize/CLAUDE.md`](../../skills/lab5-optimize/CLAUDE.md) 获取详细的实现指南。

## 实验目标

1. 实现常量折叠和常量传播
2. 实现死代码消除
3. 构建控制流图 (CFG)
4. 实现基本的数据流分析

## 优化类型

| 优化 | 描述 |
|------|------|
| 常量折叠 | 编译时计算常量表达式 |
| 常量传播 | 用常量值替换变量使用 |
| 死代码消除 | 删除无用的代码 |
| 公共子表达式消除 | 避免重复计算 |
| 窥孔优化 | 局部指令模式优化 |

## 优化示例

### 输入
```c
int main() {
    int x = 1 + 2;
    int y = x * 2;
    int z = y;      // z 未使用
    return y;
}
```

### 优化后
```c
int main() {
    return 6;
}
```

## 性能对比

```bash
# 未优化
./compiler -O0 test.c > test0.S
riscv64-linux-gnu-gcc -static test0.S -o test0
time qemu-riscv64 ./test0
riscv64-linux-gnu-size test0

# 优化后
./compiler -O1 test.c > test1.S
riscv64-linux-gnu-gcc -static test1.S -o test1
time qemu-riscv64 ./test1
riscv64-linux-gnu-size test1
```

## 运行测试

```bash
# 启用优化
cd lab5-optimize/source
./compiler -O1 test.c > test.S

# 验证正确性
riscv64-linux-gnu-gcc -static test.S -o test
qemu-riscv64 ./test
```

## 提交要求

- 优化实现代码
- 实验报告（优化策略和性能分析）
- 优化前后的性能对比数据

## 参考资源

- [Engineering a Compiler](https://www.cs.princeton.edu/~appel/modern/)
- [LLVM Optimization](https://llvm.org/docs/Passes.html)
