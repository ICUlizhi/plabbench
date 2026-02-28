# Lab 2: User Programs

## 实验概述

实现用户程序的执行和系统调用，包括进程加载、参数传递、系统调用框架和基本系统调用。

## 文档链接

- **Pintos**: [Lab 2 - User Programs](https://pkuflyingpig.gitbook.io/pintos/project-description/lab2-user-programs)
- **Tacos**: [Lab 2 - Userprograms](https://pku-tacos.pages.dev/lab2-userprograms)

## Skill 文件

查看 [`../../skills/lab2/CLAUDE.md`](../../skills/lab2/CLAUDE.md) 获取详细的系统调用实现指南。

## 目录结构

```
lab2-userprog/
├── pintos/          # Pintos (C) 版本
└── tacos/           # Tacos (Rust) 版本
```

## 实验任务

### 任务 1: 进程加载

- 实现 ELF 文件加载
- 设置用户栈
- 正确传递命令行参数

### 任务 2: 系统调用框架

- 实现系统调用处理函数
- 用户指针验证
- 参数传递

### 任务 3: 基础系统调用

| 系统调用 | 功能 |
|----------|------|
| `exit` | 进程退出 |
| `exec` | 执行新程序 |
| `wait` | 等待子进程 |
| `write` | 写入文件/stdout |
| `read` | 读取文件/stdin |

### 任务 4: 文件系统调用

| 系统调用 | 功能 |
|----------|------|
| `create` | 创建文件 |
| `remove` | 删除文件 |
| `open` | 打开文件 |
| `close` | 关闭文件 |
| `filesize` | 获取文件大小 |
| `seek` | 移动文件指针 |
| `tell` | 获取当前位置 |

## 关键文件

| 文件 | 说明 |
|------|------|
| `userprog/process.c` | 进程加载 |
| `userprog/syscall.c` | 系统调用处理 |
| `userprog/exception.c` | 异常处理 |
| `lib/user/syscall.c` | 用户态系统调用包装 |

## 测试列表

- args-single, args-multiple, args-many
- sc-bad-sp, sc-bad-arg, sc-boundary
- exit, halt
- create, open, close, read, write
- exec, wait
- bad-read, bad-write, bad-jump

## 安全要求

- 验证所有用户指针
- 防止访问内核内存
- 正确处理无效系统调用

## 截止日期

- 代码: Apr 10
- 文档: Apr 13
