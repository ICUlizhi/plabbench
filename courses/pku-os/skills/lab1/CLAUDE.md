# Lab 1: Threads / Scheduling

## 实验目标

实现线程管理和调度：
- 修改 `timer_sleep()` 避免忙等待
- 实现优先级调度
- 实现优先级捐赠（解决优先级反转）
- 实现多级反馈队列调度器 (MLFQS)

## 核心概念

### 线程状态

```c
enum thread_status {
  THREAD_RUNNING,     // 当前运行线程（只有一个）
  THREAD_READY,       // 就绪队列中的线程
  THREAD_BLOCKED,     // 等待事件的线程
  THREAD_DYING        // 等待被清理的线程
};
```

### 调度器

默认使用 Round-Robin 算法：
- 每个线程运行 4ms (TIME_SLICE)
- 时间到则加入就绪队列尾部
- 从就绪队列头部取出下一个线程

### 定时器中断

```c
// devices/timer.c
static void timer_interrupt(struct intr_frame *args UNUSED) {
  ticks++;  // 全局时间戳
  thread_tick();  // 检查是否需要抢占
}
```

## 任务详解

### 任务 1: Alarm Clock (timer_sleep)

**问题**: 当前 `timer_sleep()` 使用忙等待：

```c
void timer_sleep(int64_t ticks) {
  int64_t start = timer_ticks();
  while (timer_elapsed(start) < ticks)  // 忙等待！
    thread_yield();
}
```

**解决方案**: 使用阻塞等待

1. 在线程结构中添加 `wakeup_tick` 字段
2. 修改 `timer_sleep()`: 计算唤醒时间，阻塞线程
3. 在 `timer_interrupt()`: 检查并唤醒到期的线程

**关键代码**:

```c
// thread.h 中添加字段
struct thread {
  // ... 原有字段 ...
  int64_t wakeup_tick;  // 线程应该被唤醒的时间
};

// timer.c
void timer_sleep(int64_t ticks) {
  if (ticks <= 0) return;
  ASSERT(intr_get_level() == INTR_ON);

  enum intr_level old_level = intr_disable();
  struct thread *cur = thread_current();
  cur->wakeup_tick = timer_ticks() + ticks;
  thread_block();  // 阻塞，不是 yield
  intr_set_level(old_level);
}

// timer_interrupt 中唤醒线程
static void timer_interrupt(struct intr_frame *args UNUSED) {
  ticks++;
  thread_tick();
  // 遍历所有阻塞的线程，唤醒到期的
  // 提示: 可以维护一个按 wakeup_tick 排序的列表
}
```

### 任务 2: Priority Scheduler

**目标**: 高优先级线程先运行

**修改点**:

1. **就绪队列排序**: 按优先级排序
   ```c
   // 在 thread_yield() 和 thread_unblock() 中
   // 使用 list_insert_ordered() 而不是 list_push_back()
   ```

2. **优先级变化时重新调度**:
   ```c
   void thread_set_priority(int new_priority) {
     // 设置新优先级
     // 检查是否需要让出 CPU
   }
   ```

3. **新线程创建时**: 如果新线程优先级更高，立即调度

**重要**: 需要维护 `original_priority` 用于优先级捐赠后的恢复。

### 任务 3: Priority Donation

**问题**: 优先级反转

```
高优先级线程 H 等待低优先级线程 L 持有的锁
中等优先级线程 M 抢占了 L
导致 H 被 M 间接阻塞
```

**解决方案**: 优先级捐赠

- 当 H 等待 L 的锁时，L 暂时获得 H 的优先级
- 捐赠可以是嵌套的（H -> L -> LL）

**实现要点**:

1. **锁结构中添加捐赠信息**:
   ```c
   struct lock {
     struct thread *holder;
     struct semaphore semaphore;
     struct list_elem elem;  // 用于线程的 locks_held 列表
     int max_priority;       // 等待此锁的最高优先级
   };
   ```

2. **线程结构中添加**:
   ```c
   struct thread {
     int priority;           // 当前有效优先级（可能含捐赠）
     int original_priority;  // 原始优先级
     struct list locks_held; // 持有的锁列表
     struct lock *waiting_lock; // 正在等待的锁
   };
   ```

3. **修改 lock_acquire()**:
   ```c
   void lock_acquire(struct lock *lock) {
     ASSERT(!lock_held_by_current_thread(lock));

     if (lock->holder != NULL) {
       // 当前线程正在等待此锁
       thread_current()->waiting_lock = lock;
       // 捐赠优先级
       donate_priority(thread_current(), lock->holder);
     }

     sema_down(&lock->semaphore);
     lock->holder = thread_current();
     thread_current()->waiting_lock = NULL;
     list_push_back(&thread_current()->locks_held, &lock->elem);
   }
   ```

4. **修改 lock_release()**:
   ```c
   void lock_release(struct lock *lock) {
     ASSERT(lock_held_by_current_thread(lock));

     list_remove(&lock->elem);
     // 恢复优先级：取原始优先级和剩余捐赠的最大值
     update_priority_after_release(thread_current());

     lock->holder = NULL;
     sema_up(&lock->semaphore);
   }
   ```

### 任务 4: MLFQS (Advanced)

**多级反馈队列调度器**

- 64 个优先级队列 (0-63)
- 使用 `recent_cpu` 和 `nice` 值计算优先级
- 每 4 ticks 重新计算当前线程优先级
- 每秒重新计算所有线程的 `recent_cpu` 和优先级

**公式**:
```
priority = PRI_MAX - (recent_cpu / 4) - (nice * 2)
recent_cpu = (2*load_avg)/(2*load_avg + 1) * recent_cpu + nice
load_avg = (59/60)*load_avg + (1/60)*ready_threads
```

## 关键文件

| 文件 | 说明 |
|------|------|
| `threads/thread.c` | 线程创建、调度、管理 |
| `threads/thread.h` | 线程结构定义 |
| `threads/synch.c` | 同步原语（锁、信号量） |
| `devices/timer.c` | 定时器中断 |

## 测试列表

### Alarm Clock
- alarm-single
- alarm-multiple
- alarm-simultaneous
- alarm-zero, alarm-negative

### Priority Scheduler
- priority-change
- priority-preempt
- priority-fifo

### Priority Donation
- priority-donate-one
- priority-donate-multiple
- priority-donate-nest
- priority-donate-sema
- priority-donate-lower

### MLFQS
- mlfqs-load-1, mlfqs-load-60, mlfqs-load-avg
- mlfqs-recent-1
- mlfqs-fair-2, mlfqs-fair-20
- mlfqs-nice-2, mlfqs-nice-10
- mlfqs-block

## 常见陷阱

1. **竞态条件**: 修改线程结构时未禁用中断
2. **优先级捐赠链**: 忘记处理嵌套捐赠
3. **内存泄漏**: 线程退出时未清理资源
4. **中断禁用范围**: 中断禁用太久导致定时器不准确

## 调试技巧

```c
// 打印线程信息
printf("Thread %s: priority=%d, status=%d\n",
       t->name, t->priority, t->status);

// 检查就绪队列
struct list_elem *e;
for (e = list_begin(&ready_list);
     e != list_end(&ready_list);
     e = list_next(e)) {
  struct thread *t = list_entry(e, struct thread, elem);
  printf("Ready: %s (pri=%d)\n", t->name, t->priority);
}
```

## 参考资源

- [Pintos Lab 1](https://pkuflyingpig.gitbook.io/pintos/project-description/lab1-threads)
- [Tacos Lab 1](https://pku-tacos.pages.dev/lab1-scheduling)
