# Lab 3b: Mmap Files

## 实验概述

实现内存映射文件（mmap）系统调用，允许将文件内容映射到进程地址空间。

## 文档链接

- **Pintos**: [Lab 3b - Mmap Files](https://pkuflyingpig.gitbook.io/pintos/project-description/lab3b-mmap-files)
- **Tacos**: 无此 Lab

## Skill 文件

查看 [`../../skills/lab3b/CLAUDE.md`](../../skills/lab3b/CLAUDE.md) 获取详细的 mmap 实现指南。

## 目录结构

```
lab3b-mmap/
└── pintos/          # 仅 Pintos 版本
```

## 实验任务

### 任务 1: Mmap 系统调用

```c
void *mmap(int fd, void *addr, size_t length);
```

- 验证参数
- 分配虚拟地址空间
- 创建 SPT 项
- 延迟加载页面

### 任务 2: Munmap 系统调用

```c
void munmap(mapid_t mapping);
```

- 解除映射
- 写回修改的页面
- 释放资源

### 任务 3: 文件同步

- 检测页面修改（dirty bit）
- 写回文件
- 处理重叠映射

## 关键文件

| 文件 | 说明 |
|------|------|
| `vm/mmap.c` | mmap 实现 |
| `userprog/syscall.c` | 系统调用入口 |
| `vm/page.c` | 页面管理（添加 MMAP 类型） |

## 测试列表

- mmap-read: 读取映射文件
- mmap-write: 写入映射文件
- mmap-shuffle: 随机访问
- mmap-twice: 多次映射同一文件
- mmap-exit: 退出时自动解除
- mmap-offest: 非零偏移

## 使用示例

```c
// 用户程序示例
int fd = open("test.txt", O_RDWR);
char *data = mmap(fd, 0, filesize(fd));

// 直接访问文件内容
printf("%c", data[0]);
data[0] = 'X';  // 修改文件

munmap(fd);  // 解除映射，修改写回
close(fd);
```

## 截止日期

- 代码: May 29
- 文档: June 1
