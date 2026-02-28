# Lab 0: Booting / Appetizer

## 实验概述

理解操作系统的启动过程，包括 bootloader、实模式到保护模式的切换、以及内核的初始加载。

## 文档链接

- **Pintos**: [Lab 0 - Booting](https://pkuflyingpig.gitbook.io/pintos/project-description/lab0-booting)
- **Tacos**: [Lab 0 - Appetizer](https://pku-tacos.pages.dev/lab0-appetizer)

## Skill 文件

查看 [`../../skills/lab0/CLAUDE.md`](../../skills/lab0/CLAUDE.md) 获取详细的实现提示和调试技巧。

## 目录结构

```
lab0-booting/
├── pintos/          # Pintos (C) 版本
│   └── README.md    # 如何获取代码
└── tacos/           # Tacos (Rust) 版本
    └── README.md    # 如何获取代码
```

## 实验内容

### Pintos Track

1. **理解启动流程**:
   - BIOS 加载 bootloader (loader.S)
   - Bootloader 加载内核到内存
   - 切换到保护模式
   - 跳转到内核入口

2. **关键代码位置**:
   - `boot/loader.S`: Bootloader
   - `threads/start.S`: 内核入口
   - `threads/init.c`: 主初始化函数

### Tacos Track

1. **理解启动流程**:
   - Bootloader 加载内核
   - 设置 RISC-V 特权模式
   - 初始化页表
   - 跳转到 Rust 主函数

2. **关键代码位置**:
   - `bootloader/`: Bootloader 代码
   - `kernel/src/entry.asm`: 内核入口
   - `kernel/src/main.rs`: 主函数

## 代码获取

### Pintos

```bash
cd pintos
git clone https://github.com/pku-os/Pintos.git source
cd source
```

### Tacos

```bash
cd tacos
git clone https://github.com/pku-os/tacos.git source
cd source
```

## 提交要求

- 完成启动代码，确保内核正常启动
- 撰写实验报告，描述启动流程和你的理解

## 截止日期

- 代码: Feb 27
- 文档: Mar 2
