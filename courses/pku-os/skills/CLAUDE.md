# PKU OS 课程上下文

## 课程信息

- **名称**: 操作系统（实验班）
- **学期**: 2025 Spring
- **网址**: https://pku-os.github.io/sp25/
- **机构**: 北京大学

## 双 Track 系统

本课程有两个并行的实现版本，选择其一完成：

### Pintos (C 语言 Track)

传统的教学用操作系统，基于 C 语言实现。

**代码结构:**
```
pintos/src/
├── threads/         # 线程管理 (Lab 1)
│   ├── thread.c, thread.h
│   ├── synch.c, synch.h    # 同步原语
│   └── interrupt.h         # 中断处理
├── userprog/        # 用户程序 (Lab 2)
│   ├── process.c, process.h
│   ├── syscall.c, syscall.h
│   └── pagedir.c, pagedir.h
├── vm/              # 虚拟内存 (Lab 3a/3b)
│   ├── frame.c, frame.h
│   ├── page.c, page.h
│   └── swap.c, swap.h
├── filesys/         # 文件系统
│   ├── filesys.c, filesys.h
│   ├── inode.c, inode.h
│   └── directory.c
└── devices/         # 设备驱动
    ├── timer.c      # 定时器 (Lab 1)
    └── input.c, input.h
```

**常用命令:**
```bash
# 编译
cd pintos/src/threads
make

# 运行测试
make check                    # 运行所有测试
make tests/threads/alarm-single.result   # 单个测试

# GDB 调试
pintos-gdb kernel.o
(gdb) target remote localhost:1234
(gdb) continue
```

**测试输出位置:**
- 结果: `src/threads/build/tests/threads/*.result`
- 输出: `src/threads/build/tests/threads/*.output`
- 错误: `src/threads/build/tests/threads/*.errors`

### Tacos (Rust Track)

使用 Rust 语言实现的现代版本，内存安全且并发友好。

**代码结构:**
```
tacos/kernel/src/
├── main.rs          # 入口
├── trap/            # 中断/异常处理
├── task/            # 任务/线程管理 (Lab 1)
│   ├── mod.rs
│   ├── context.rs
│   └── scheduler.rs
├── syscall/         # 系统调用 (Lab 2)
│   └── mod.rs
├── mm/              # 内存管理 (Lab 3)
│   ├── mod.rs
│   ├── page_table.rs
│   └── frame_allocator.rs
└── fs/              # 文件系统
    └── mod.rs
```

**常用命令:**
```bash
# 构建
cargo build

# 运行测试
cargo test                    # 所有测试
cargo test alarm_single       # 单个测试

# 带输出运行
cargo test -- --nocapture

# QEMU 运行
cargo run
```

## Lab 概述

| Lab | 主题 | 核心概念 | Pintos 关键文件 | Tacos 关键文件 |
|-----|------|----------|-----------------|----------------|
| 0 | Booting | 启动流程、实模式/保护模式 | boot/loader.S, start.S | entry.asm, main.rs |
| 1 | Threads | 线程调度、同步、定时器 | thread.c, timer.c, synch.c | task/mod.rs, trap/timer.rs |
| 2 | User Programs | 系统调用、进程管理 | process.c, syscall.c | syscall/mod.rs, task/mod.rs |
| 3a | Virtual Memory | 分页、页表、页面置换 | vm/*.c, pagedir.c | mm/*.rs |
| 3b | Mmap Files | 内存映射、文件系统接口 | vm/mmap.c | (Tacos 无此 Lab) |

## 通用开发流程

1. **阅读文档**: 仔细阅读 Lab 文档和要求
2. **理解代码**: 阅读提供的起始代码和注释
3. **设计实现**: 规划数据结构和算法
4. **编写代码**: 实现功能
5. **本地测试**: 运行测试套件
6. **调试修复**: 分析问题并修复
7. **撰写报告**: 记录设计思路和测试结果

## 重要概念

### 线程状态 (Pintos)

```c
enum thread_status {
  THREAD_RUNNING,     // 正在运行
  THREAD_READY,       // 就绪，等待调度
  THREAD_BLOCKED,     // 阻塞，等待事件
  THREAD_DYING        // 即将被销毁
};
```

### 同步原语

- **Semaphore**: 计数信号量，`sema_down()`/`sema_up()`
- **Lock**: 互斥锁，`lock_acquire()`/`lock_release()`
- **Condition Variable**: 条件变量，`cond_wait()`/`cond_signal()`

### 中断控制

```c
// 禁用中断（进入临界区）
enum intr_level old_level = intr_disable();
// ... 临界区代码 ...
intr_set_level(old_level);  // 恢复中断状态
```

**重要**: 修改全局数据结构时必须禁用中断！

### 内存管理 (Lab 3)

- **Page Table**: 虚拟地址到物理地址的映射
- **Frame**: 物理内存页框
- **Swap**: 磁盘交换空间
- **Page Fault**: 缺页异常处理

## 常见陷阱

### 竞态条件

**问题**: 多个线程同时访问共享数据，未正确同步。

**解决**: 使用锁或禁用中断保护临界区。

### 中断禁用范围

**问题**: 禁用中断时间过长导致系统无响应。

**解决**: 临界区代码尽量简短，只保护必要操作。

### 优先级反转

**问题**: 高优先级线程等待低优先级线程持有的锁。

**解决**: 实现优先级捐赠（priority donation）。

### 内存泄漏

**问题**: 分配的内存/资源未释放。

**解决**: 确保每个 `malloc`/`palloc_get_page` 都有对应的 `free`/`palloc_free_page`。

## 调试技巧

### 使用 ASSERT

```c
ASSERT(condition);  // 条件不满足时 panic
```

### 打印调试

```c
printf("Debug: thread %s, value=%d\n", thread_name(), value);
hex_dump(ptr, size, true);  // 十六进制打印
```

### GDB 常用命令

```
(gdb) break function_name    # 设置断点
(gdb) continue               # 继续运行
(gdb) next                   # 单步执行（不进入函数）
(gdb) step                   # 单步执行（进入函数）
(gdb) print variable         # 打印变量
(gdb) backtrace              # 查看调用栈
(gdb) info registers         # 查看寄存器
```

### 分析测试失败

1. 查看 `.result` 文件确认失败
2. 查看 `.output` 文件了解输出
3. 查看 `.errors` 文件查看错误信息
4. 使用 GDB 复现问题

## 参考资源

- [Pintos 官方文档](https://pkuflyingpig.gitbook.io/pintos/)
- [Tacos 官方文档](https://pku-tacos.pages.dev/)
- [80x86 汇编参考](https://wiki.osdev.org/X86-64_Instruction_Listing)
- [OSDev Wiki](https://wiki.osdev.org/Main_Page)

## 提交检查清单

- [ ] 代码能通过所有测试
- [ ] 没有编译警告
- [ ] 代码风格一致
- [ ] 关键函数有注释
- [ ] 实验报告已完成
- [ ] 报告包含设计思路和测试结果
