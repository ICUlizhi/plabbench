# Lab 3a: Virtual Memory - Demand Paging

## 实验概述

实现按需分页虚拟内存系统，包括页表管理、页面错误处理、帧管理和页面置换。

## 文档链接

- **Pintos**: [Lab 3a - Demand Paging](https://pkuflyingpig.gitbook.io/pintos/project-description/lab3a-demand-paging)
- **Tacos**: [Lab 3 - Virtual Memory](https://pku-tacos.pages.dev/lab3-virtual_memory)

## Skill 文件

查看 [`../../skills/lab3a/CLAUDE.md`](../../skills/lab3a/CLAUDE.md) 获取详细的 VM 实现指南。

## 目录结构

```
lab3a-vm/
├── pintos/          # Pintos (C) 版本
└── tacos/           # Tacos (Rust) 版本
```

## 实验任务

### 任务 1: Frame Table

- 管理物理帧
- 记录每个帧的使用情况（线程、页面）
- 实现帧分配和释放

### 任务 2: Supplemental Page Table

- 扩展页表信息
- 记录页面类型（FILE, SWAP, ZERO）
- 保存文件偏移和长度

### 任务 3: Page Fault Handler

- 处理页面错误异常
- 按需加载页面
- 栈自动增长

### 任务 4: Lazy Loading

- 进程启动时不加载所有页面
- 首次访问时加载
- 延迟文件读取

### 任务 5: Swap

- 管理磁盘交换空间
- 页面换出（eviction）
- 页面换入

### 任务 6: Page Replacement

- 实现 Clock 算法
- 选择 victim 页面
- 处理 dirty page

## 关键文件

| 文件 | 说明 |
|------|------|
| `vm/page.c` | 补充页表 |
| `vm/frame.c` | 帧管理 |
| `vm/swap.c` | 交换空间 |
| `userprog/exception.c` | 页面错误处理 |

## 测试列表

- page-linear, page-parallel
- page-merge-seq, page-merge-par
- page-merge-stk, page-merge-mm
- page-shuffle
- mmap-read, mmap-write (与 Lab 3b 共享)

## 核心概念

```
虚拟地址          页表              物理内存
--------+      +--------+        +--------+
Page 0  |---->| PTE    |------->| Frame  |
        |      +--------+        +--------+
Page 1  |---->| PTE    |--X     | Frame  |
(未加载)       +--------+   |    +--------+
Page 2  |---->| PTE    |----    | Frame  |
        |      +--------+        +--------+

PTE: Page Table Entry
X: Page Fault (触发加载)
```

## 截止日期

- 代码: May 15
- 文档: May 18
