# PKU OS 调试技巧

本指南汇总了 PKU OS (Pintos/Tacos) 实验中常用的调试技巧。

## 通用调试原则

1. **复现问题**: 确保能稳定复现 bug
2. **缩小范围**: 定位到具体的代码区域
3. **检查假设**: 验证你对代码的假设是否正确
4. **使用工具**: 善用调试器和日志

## Pintos 调试技巧

### 1. 使用 ASSERT

```c
// 检查条件，不满足则 panic
ASSERT(condition);

// 示例
ASSERT(t != NULL);
ASSERT(intr_get_level() == INTR_OFF);
```

### 2. 打印调试

```c
// 简单打印
printf("Debug: thread %s, value=%d\n", thread_name(), value);

// 十六进制打印
hex_dump((uintptr_t)ptr, ptr, length, true);

// 带位置的打印
#define DEBUG(fmt, ...) \
  printf("[%s:%d] " fmt "\n", __FILE__, __LINE__, ##__VA_ARGS__)
```

### 3. 查看线程状态

```c
void print_thread_info(struct thread *t) {
  printf("Thread: %s\n", t->name);
  printf("  Status: %d\n", t->status);
  printf("  Priority: %d\n", t->priority);
  printf("  Stack: %p\n", t->stack);
}
```

### 4. 检查就绪队列

```c
void print_ready_list(void) {
  struct list_elem *e;
  printf("Ready list:\n");
  for (e = list_begin(&ready_list);
       e != list_end(&ready_list);
       e = list_next(e)) {
    struct thread *t = list_entry(e, struct thread, elem);
    printf("  %s (priority=%d)\n", t->name, t->priority);
  }
}
```

### 5. GDB 调试

```bash
# 启动调试模式
pintos --gdb -- run test-name

# 另一个终端
cd build
pintos-gdb kernel.o
(gdb) target remote localhost:1234

# 常用命令
(gdb) break function_name     # 设置断点
(gdb) break thread.c:123      # 在文件行号设断点
(gdb) continue                # 继续运行
(gdb) next                    # 下一行
(gdb) step                    # 进入函数
(gdb) finish                  # 完成当前函数
(gdb) print variable          # 打印变量
(gdb) print/x variable        # 十六进制打印
(gdb) backtrace               # 调用栈
(gdb) info registers          # 寄存器
(gdb) x/10x $esp              # 检查栈内存
```

### 6. 检查测试失败

```bash
# 测试结果
cat build/tests/threads/alarm-single.result

# 详细输出
cat build/tests/threads/alarm-single.output

# 错误信息
cat build/tests/threads/alarm-single.errors
```

## Tacos 调试技巧

### 1. 使用 print 宏

```rust
// 内核态打印
println!("Debug: task {:?}, value={}", task, value);

// 格式化打印
log::info!("Task {} created", task_id);
log::debug!("Registers: {:x?", registers);
```

### 2. 使用 assert

```rust
assert!(condition);
assert_eq!(expected, actual);
assert_ne!(value1, value2);
```

### 3. 调试 panic

```rust
// 添加位置信息
panic!("Unexpected state at {:?}", location);

// 或者使用 unwrap/expect
let value = option.expect("Value should exist");
```

### 4. GDB 调试

```bash
# 启动 QEMU 等待 GDB
qemu-system-riscv64 ... -s -S

# GDB 连接
riscv64-unknown-elf-gdb target/riscv64gc-unknown-none-elf/release/kernel
(gdb) target remote :1234
(gdb) break main
(gdb) continue
```

## Lab 特定调试技巧

### Lab 1: Threads

#### 检测竞态条件

```c
// 在访问共享数据前后添加检查
void check_consistency(void) {
  // 检查数据结构不变量
  ASSERT(list_size(&ready_list) >= 0);
}
```

#### 检查中断状态

```c
enum intr_level old_level = intr_get_level();
// ... 操作 ...
ASSERT(intr_get_level() == old_level);  // 确保中断状态恢复
```

#### 优先级捐赠调试

```c
void print_donation_chain(struct thread *t) {
  printf("Donation chain: ");
  while (t != NULL) {
    printf("%s(pri=%d) -> ", t->name, t->priority);
    if (t->waiting_lock == NULL) break;
    t = t->waiting_lock->holder;
  }
  printf("NULL\n");
}
```

### Lab 2: User Programs

#### 检查用户指针

```c
// 验证用户指针有效性
bool is_valid_user_pointer(const void *ptr) {
  return ptr != NULL
      && is_user_vaddr(ptr)
      && pagedir_get_page(thread_current()->pagedir, ptr) != NULL;
}
```

#### 打印系统调用

```c
// 在 syscall_handler 开头添加
printf("SYSCALL: %d from %s\n", syscall_num, thread_name());
```

#### 检查参数传递

```c
// 打印栈上的参数
void print_args(void **esp) {
  printf("argc: %d\n", *(int *)esp);
  printf("argv: %p\n", *(void **)(esp + 1));
  // 打印每个参数
  char **argv = *(char ***)(esp + 1);
  for (int i = 0; argv[i] != NULL; i++) {
    printf("  argv[%d]: %s\n", i, argv[i]);
  }
}
```

### Lab 3: Virtual Memory

#### 打印 SPT

```c
void spt_dump(struct hash *spt) {
  struct hash_iterator i;
  hash_first(&i, spt);
  printf("Supplemental Page Table:\n");
  while (hash_next(&i)) {
    struct spt_entry *e = hash_entry(hash_cur(&i), struct spt_entry, elem);
    printf("  upage=%p, kpage=%p, type=%d, loaded=%d\n",
           e->upage, e->kpage, e->type, e->loaded);
  }
}
```

#### 检查帧表

```c
void frame_dump(void) {
  struct list_elem *e;
  printf("Frame Table:\n");
  for (e = list_begin(&frame_table); e != list_end(&frame_table);
       e = list_next(e)) {
    struct frame *f = list_entry(e, struct frame, elem);
    printf("  kpage=%p, thread=%s, upage=%p\n",
           f->kpage, f->thread->name, f->spte->upage);
  }
}
```

#### 页面错误调试

```c
static void page_fault(struct intr_frame *f) {
  void *fault_addr;
  asm ("movl %%cr2, %0" : "=r" (fault_addr));

  printf("PAGE FAULT at %p\n", fault_addr);
  printf("  eip: %p\n", f->eip);
  printf("  esp: %p\n", f->esp);
  printf("  error: %d\n", f->error_code);

  // ... 原有处理代码 ...
}
```

## 常见错误及解决

### 1. 竞态条件 (Race Condition)

**症状**: 随机崩溃，难以复现

**解决**:
- 确保访问共享数据时禁用中断或持有锁
- 使用 ASSERT 检查不变量

### 2. 空指针解引用

**症状**: Kernel panic at 0x00000000

**解决**:
- 检查所有指针是否为 NULL
- 使用 ASSERT(ptr != NULL)

### 3. 栈溢出

**症状**: 奇怪的崩溃，损坏的数据

**解决**:
- 检查递归深度
- 避免在栈上分配大数组

### 4. 内存泄漏

**症状**: 运行一段时间后崩溃

**解决**:
- 确保每个 malloc 都有对应的 free
- 使用 valgrind（用户态程序）

## 调试检查清单

- [ ] 编译无警告
- [ ] 已启用调试信息 (-g)
- [ ] 单步调试定位问题
- [ ] 检查边界条件
- [ ] 验证同步机制
- [ ] 检查内存分配/释放
- [ ] 测试小规模用例

## 参考资源

- [GDB 手册](https://sourceware.org/gdb/current/onlinedocs/gdb/)
- [OSDev Debugging](https://wiki.osdev.org/Debugging)
