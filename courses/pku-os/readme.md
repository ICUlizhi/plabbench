# 北京大学 - 操作系统（实验班）

课程网站: https://pku-os.github.io/sp25/

## 课程简介

本课程讲授操作系统设计与实现的关键概念、原理、算法和机制。通过实现一个真实的教育操作系统，深入理解操作系统的核心机制。

## 双 Track 系统

本课程提供两个并行的实现 track：

### Pintos (C 语言)

传统的教学操作系统，代码清晰，文档丰富。

- **仓库**: https://github.com/pku-os/Pintos
- **文档**: https://pkuflyingpig.gitbook.io/pintos/
- **语言**: C
- **测试**: `make check`

### Tacos (Rust)

使用现代 Rust 语言实现的版本，内存安全，并发友好。

- **仓库**: https://github.com/pku-os/tacos
- **文档**: https://pku-tacos.pages.dev/
- **语言**: Rust
- **测试**: `cargo test`

## Lab 列表

| Lab | 名称 | 内容 | Pintos 链接 | Tacos 链接 | 截止日期 |
|-----|------|------|-------------|------------|----------|
| Lab 0 | Booting / Appetizer | 启动基础 | [P-Lab0](https://pkuflyingpig.gitbook.io/pintos/project-description/lab0-booting) | [T-Lab0](https://pku-tacos.pages.dev/lab0-appetizer) | Mar 2 |
| Lab 1 | Threads / Scheduling | 线程管理 | [P-Lab1](https://pkuflyingpig.gitbook.io/pintos/project-description/lab1-threads) | [T-Lab1](https://pku-tacos.pages.dev/lab1-scheduling) | Mar 23 |
| Lab 2 | User Programs | 用户程序执行 | [P-Lab2](https://pkuflyingpig.gitbook.io/pintos/project-description/lab2-user-programs) | [T-Lab2](https://pku-tacos.pages.dev/lab2-userprograms) | Apr 13 |
| Lab 3a | Virtual Memory | 分页实现 | [P-Lab3a](https://pkuflyingpig.gitbook.io/pintos/project-description/lab3a-demand-paging) | [T-Lab3](https://pku-tacos.pages.dev/lab3-virtual_memory) | May 18 |
| Lab 3b | Mmap Files | 内存映射文件 | [P-Lab3b](https://pkuflyingpig.gitbook.io/pintos/project-description/lab3b-mmap-files) | - | June 1 |

## 目录结构

```
pku-os/
├── skills/           # Claude Code Skills
│   ├── CLAUDE.md     # 课程级上下文
│   └── lab*/         # 各 Lab 的 Skill
├── labs/             # Lab 内容
│   └── lab*/         # 各 Lab 的说明和代码框架
└── benchmark/        # 评测相关
    ├── runner.py
    └── results/
```

## 快速开始

### 1. 选择 Track

根据你的偏好选择 Pintos (C) 或 Tacos (Rust)：

```bash
# Pintos
cd labs/lab0-booting/pintos

# Tacos
cd labs/lab0-booting/tacos
```

### 2. 启动 AI 助手

```bash
# 在课程根目录启动，加载课程上下文
cd ../..
claude
```

### 3. 开始 Lab

```
> 帮我完成 Lab 0 的启动代码
```

## 提交要求

每个 Lab 需要提交：
1. **代码**: 实现所有要求的功能
2. **实验报告**: 描述设计思路、实现细节和测试结果

## 评分标准

- 功能正确性 (60%): 通过所有测试用例
- 代码质量 (20%): 代码风格、注释、结构
- 实验报告 (20%): 清晰度、完整性、深度

## 调试工具

### Pintos

```bash
# GDB 调试
pintos-gdb kernel.o

# 运行特定测试
make tests/threads/alarm-single.result

# 查看完整输出
 pintos --gdb -- run alarm-single
```

### Tacos

```bash
# 调试测试
cargo test -- --nocapture

# 特定测试
cargo test alarm_single -- --nocapture
```

## 参考资源

- [课程主页](https://pku-os.github.io/sp25/)
- [往年课程](https://pku-os.github.io/sp24/)
- [Pintos 官方文档](https://pkuflyingpig.gitbook.io/pintos/)
- [Tacos 官方文档](https://pku-tacos.pages.dev/)
- [OSDev Wiki](https://wiki.osdev.org/)

## 获取帮助

1. 查阅课程文档和代码注释
2. 使用本项目的 [Skill 库](./skills/)
3. 使用 Claude Code / Kimi Code 询问
4. 课程 Piazza/论坛

## 评测记录

查看 [benchmark/results/](benchmark/results/) 目录获取 AI 评测结果。
