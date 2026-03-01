# PKU Minic 环境搭建指南

本指南介绍编译原理课程的开发环境搭建。

## 系统要求

- Linux (Ubuntu 20.04+ 推荐) 或 macOS
- C/C++ 编译器 (GCC/Clang)
- Flex 和 Bison
- RISC-V 工具链
- QEMU

## 安装依赖

### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    flex \
    bison \
    gcc-riscv64-linux-gnu \
    qemu-user \
    git
```

### macOS

```bash
# 使用 Homebrew
brew install flex bison qemu riscv-tools
```

## 验证安装

```bash
# 检查版本
flex --version
bison --version
riscv64-linux-gnu-gcc --version
qemu-riscv64 --version
```

## 获取课程框架

```bash
# 克隆 Minic 编译器框架
git clone https://github.com/pku-minic/minic-compiler.git
cd minic-compiler
```

## 目录结构

```
minic-compiler/
├── src/           # 源代码
├── include/       # 头文件
├── tests/         # 测试用例
├── Makefile
└── README.md
```

## 编译项目

```bash
make
```

## 运行测试

```bash
# 运行所有测试
make test

# 运行单个测试
./compiler tests/test1.c
```

## RISC-V 测试流程

```bash
# 1. 编译生成汇编
./compiler test.c > test.S

# 2. 汇编和链接
riscv64-linux-gnu-gcc -static test.S -o test

# 3. QEMU 运行
qemu-riscv64 ./test
echo $?  # 查看返回值
```

## VSCode 配置

### 推荐插件

- C/C++ (Microsoft)
- Makefile Tools
- RISC-V Assembly

### 调试配置

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Compiler",
      "type": "cppdbg",
      "request": "launch",
      "program": "${workspaceFolder}/compiler",
      "args": ["${workspaceFolder}/tests/test1.c"],
      "cwd": "${workspaceFolder}"
    }
  ]
}
```

## 常见问题

### Flex/Bison 版本不兼容

```bash
# 检查版本
flex --version  # 需要 2.6+
bison --version # 需要 3.0+
```

### RISC-V 工具链找不到

```bash
# 添加 PATH
export PATH=$PATH:/usr/riscv64-linux-gnu/bin
```

### QEMU 运行失败

```bash
# 检查 QEMU 安装
qemu-riscv64 --help

# 可能需要安装 qemu-user-static
sudo apt-get install qemu-user-static
```

## 下一步

环境搭建完成后，可以开始 [Lab 1: 词法分析器](../../../courses/pku-minic/labs/lab1-lexer/)。
