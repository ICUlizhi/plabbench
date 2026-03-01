# 北京大学 - 编译原理（编译实践）

课程网站: https://pku-minic.github.io/online-doc/#/

GitHub: https://github.com/pku-minic/online-doc

## 课程简介

本课程通过实现一个完整的编译器（Minic）来讲解编译原理的核心概念，包括词法分析、语法分析、语义分析、代码生成和优化。

**目标语言**: MiniC（C 语言子集）

**目标架构**: RISC-V 32/64

**实现语言**: C/C++ 或 Rust

## 实验列表

| Lab | 名称 | 内容 | 文档链接 | 状态 |
|-----|------|------|----------|------|
| Lab 1 | 词法分析器 | Flex/Lex 词法分析 | [Lab 1](https://pku-minic.github.io/online-doc/#/labs/lab1/) | 可用 |
| Lab 2 | 语法分析器 | Bison/Yacc 语法分析，AST 构建 | [Lab 2](https://pku-minic.github.io/online-doc/#/labs/lab2/) | 可用 |
| Lab 3 | 语义分析 | 类型检查、符号表 | [Lab 3](https://pku-minic.github.io/online-doc/#/labs/lab3/) | 可用 |
| Lab 4 | 代码生成 | RISC-V 汇编生成 | [Lab 4](https://pku-minic.github.io/online-doc/#/labs/lab4/) | 可用 |
| Lab 5 | 代码优化 | 基本块、数据流分析、优化 | [Lab 5](https://pku-minic.github.io/online-doc/#/labs/lab5/) | 可用 |

## 目录结构

```
pku-minic/
├── README.md           # 本文件
├── skills/             # Claude Code Skills
│   ├── CLAUDE.md       # 课程级上下文
│   └── lab*/           # 各 Lab 的 Skill
├── labs/               # Lab 内容
│   └── lab*/           # 各 Lab 的说明
└── benchmark/          # 评测相关
    ├── runner.py
    └── results/
```

## 快速开始

### 1. 环境准备

```bash
# 安装必要工具
sudo apt-get install flex bison gcc-riscv64-linux-gnu qemu-user

# 或使用 Docker
# docker pull pku-minic/env
```

### 2. 获取框架代码

```bash
# Lab 1 框架
git clone https://github.com/pku-minic/minic-compiler.git
cd minic-compiler
```

### 3. 启动 AI 助手

```bash
cd courses/pku-minic
claude
```

### 4. 开始实验

```
> 帮我完成 Lab 1 的词法分析器
```

## 编译器整体架构

```
源代码 (.c) → 词法分析 → 语法分析 → 语义分析 → 中间代码 → 代码生成 → 汇编代码
                ↓           ↓           ↓           ↓           ↓
              Tokens      AST        符号表       Koopa IR    RISC-V
```

## 各阶段任务

### Lab 1: 词法分析 (Lexer)

将源代码转换为 Token 序列：
- 识别关键字 (int, if, while, return)
- 识别标识符
- 识别常量 (整数、浮点数)
- 识别运算符和分隔符

**工具**: Flex/Lex

### Lab 2: 语法分析 (Parser)

将 Token 序列解析为抽象语法树 (AST)：
- 上下文无关文法
- 递归下降分析 或 LR 分析
- 构建 AST

**工具**: Bison/Yacc 或手写递归下降

### Lab 3: 语义分析 (Semantic Analysis)

检查程序语义正确性：
- 类型检查
- 变量声明检查
- 符号表管理
- 作用域分析

### Lab 4: 代码生成 (Code Generation)

将 AST 转换为目标代码：
- 中间表示 (Koopa IR)
- 寄存器分配
- RISC-V 汇编生成

### Lab 5: 代码优化 (Optimization)

改进生成代码的性能：
- 常量折叠
- 死代码消除
- 基本块划分
- 数据流分析

## 测试方法

```bash
# 编译你的编译器
cd labs/lab1-lexer/source
make

# 运行测试
./compiler test.c > test.S

# 使用 RISC-V 工具链编译
riscv64-linux-gnu-gcc test.S -o test

# QEMU 运行
qemu-riscv64 ./test
echo $?  # 查看返回值
```

## 自动化测试

```bash
# 运行所有测试
python ../benchmark/runner.py --lab lab1-lexer

# 查看结果
cat ../benchmark/results/latest.json
```

## 提交要求

- 每个 Lab 的完整源代码
- 实验报告（设计思路、实现细节、测试结果）
- 通过的测试用例列表

## 参考资源

- [课程文档](https://pku-minic.github.io/online-doc/#/)
- [Flex 手册](https://westes.github.io/flex/manual/)
- [Bison 手册](https://www.gnu.org/software/bison/manual/)
- [RISC-V 指令集手册](https://riscv.org/technical/specifications/)
- [Koopa IR 文档](https://github.com/pku-minic/koopa)

## 获取帮助

1. 查阅课程文档
2. 使用本项目的 [Skill 库](./skills/)
3. 使用 Claude Code / Kimi Code 询问
4. 课程 GitHub Issues

## 评测记录

查看 [benchmark/results/](benchmark/results/) 目录获取 AI 评测结果。
