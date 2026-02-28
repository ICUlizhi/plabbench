# Claude Code 使用指南

本指南介绍如何使用 Claude Code 高效完成北大计算机课程 Lab。

## 安装与配置

### 安装

```bash
# 通过 npm 安装（需要 Node.js 18+）
npm install -g @anthropic-ai/claude-code

# 验证安装
claude --version
```

### 首次配置

1. 运行 `claude` 启动
2. 按提示登录 Claude 账号
3. 授权访问

## 基本命令

| 命令 | 说明 |
|------|------|
| `/help` | 显示帮助信息 |
| `/clear` | 清空对话历史 |
| `/compact` | 压缩对话上下文 |
| `/exit` 或 `Ctrl+D` | 退出 Claude Code |

## 与 Plabbench 配合使用

### 1. 进入课程目录

```bash
cd courses/pku-os
claude
```

进入目录后，Claude Code 会自动读取 `skills/CLAUDE.md` 获取课程上下文。

### 2. 请求帮助

```
> 帮我分析 Lab 1 的 requirements

> timer_sleep 函数有什么问题？如何修复？

> 运行测试时出现 "Assertion failed"，怎么调试？
```

### 3. 使用 Skills

课程特定的 Skills 会自动加载。你也可以手动引用：

```
> @lab1 告诉我线程调度的关键函数
```

### 4. 常用工作流

**编写代码：**
```
> 帮我实现 timer_sleep 函数，要求使用 semaphore 避免忙等待
```

**调试错误：**
```
> 测试 alarm-single 失败了，查看测试结果并分析原因
```

**代码审查：**
```
> 检查我的 thread_yield 实现是否有竞态条件
```

## 最佳实践

### 1. 清晰的指令

✅ **好的示例：**
```
在 timer_sleep 函数中，将忙等待改为使用 semaphore 的阻塞等待。
需要修改 devices/timer.c，并确保在 timer_interrupt 中释放 semaphore。
```

❌ **不好的示例：**
```
修复 timer_sleep
```

### 2. 提供上下文

如果遇到问题，提供：
- 错误信息（复制粘贴或截图）
- 相关代码片段
- 你尝试过的解决方案

### 3. 分步骤进行

复杂的 lab 可以分步骤完成：
```
步骤 1: 理解代码结构和需求
> 解释 thread.c 中的主要数据结构和函数

步骤 2: 实现核心功能
> 帮我实现 thread_sleep 函数

步骤 3: 测试和调试
> 运行 tests/threads/alarm 测试并修复错误
```

## 调试技巧

### 使用 GDB

```
> 在 thread_yield 函数处设置断点，启动 GDB 调试
```

### 查看日志

```
> 查看 pintos 的完整输出日志，找出失败的测试用例
```

### 分析死锁

```
> 分析这个死锁情况，所有线程都在等待什么？
```

## 常见问题

### Q: Claude Code 无法访问某些文件？
A: 确保在正确的目录下启动，或手动提供文件路径。

### Q: 上下文太长导致响应变慢？
A: 使用 `/compact` 压缩上下文，或开启新对话。

### Q: 如何导入图片或截图？
A: 直接将图片文件拖入终端，Claude Code 会读取。

### Q: 可以批量处理多个文件吗？
A: 可以，直接请求："检查 threads/ 目录下所有文件的竞态条件问题"

## 相关资源

- [Claude Code 官方文档](https://docs.anthropic.com/en/docs/claude-code/overview)
- [PKU OS 教程](./pku-os/)

## 提示词技巧

### 角色设定

```
你是一位操作系统专家，擅长 Pintos 教学操作系统。
请帮我分析代码问题并提供修复建议。
```

### 结构化输出

```
请按以下格式分析：
1. 问题原因
2. 修复方案
3. 需要修改的文件和代码行
4. 测试验证方法
```

### 代码风格

```
请保持代码风格与周围代码一致，使用 2 空格缩进，
变量名使用小写下划线格式。
```
