# Lab 1: Threads / Scheduling

## 实验概述

实现线程管理和调度，包括避免忙等待的 timer_sleep、优先级调度、优先级捐赠和 MLFQS。

## 文档链接

- **Pintos**: [Lab 1 - Threads](https://pkuflyingpig.gitbook.io/pintos/project-description/lab1-threads)
- **Tacos**: [Lab 1 - Scheduling](https://pku-tacos.pages.dev/lab1-scheduling)

## Skill 文件

查看 [`../../skills/lab1/CLAUDE.md`](../../skills/lab1/CLAUDE.md) 获取详细的实现指南、代码模板和调试技巧。

## 目录结构

```
lab1-threads/
├── pintos/          # Pintos (C) 版本
└── tacos/           # Tacos (Rust) 版本
```

## 实验任务

### 任务 1: Alarm Clock (所有学生)

- 修改 `timer_sleep()` 避免忙等待
- 使用阻塞等待机制
- 在定时器中断中唤醒线程

### 任务 2: Priority Scheduler (所有学生)

- 实现按优先级排序的就绪队列
- 优先级变化时重新调度
- 新线程创建时抢占

### 任务 3: Priority Donation (所有学生)

- 解决优先级反转问题
- 实现优先级捐赠机制
- 处理嵌套捐赠

### 任务 4: MLFQS (进阶，可选)

- 实现多级反馈队列调度器
- 使用 `recent_cpu` 和 `nice` 值
- 定期重新计算优先级

## 关键文件

| 文件 | 说明 |
|------|------|
| `threads/thread.c` | 线程管理 |
| `threads/thread.h` | 线程数据结构 |
| `threads/synch.c` | 同步原语 |
| `devices/timer.c` | 定时器中断 |

## 测试列表

### Alarm Clock
- alarm-single, alarm-multiple, alarm-simultaneous

### Priority
- priority-change, priority-preempt, priority-fifo
- priority-donate-one, priority-donate-multiple
- priority-donate-nest, priority-donate-sema

### MLFQS
- mlfqs-load-1, mlfqs-load-60, mlfqs-fair-2
- mlfqs-nice-2, mlfqs-nice-10

## 运行测试

```bash
# Pintos
cd pintos/src/threads
make check

# Tacos
cd tacos/kernel
cargo test
```

## 截止日期

- 代码: Mar 20
- 文档: Mar 23
