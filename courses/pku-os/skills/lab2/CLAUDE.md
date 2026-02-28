# Lab 2: User Programs

## 实验目标

实现用户程序的执行和系统调用：
- 进程加载和执行
- 参数传递（命令行参数）
- 系统调用框架
- 基本系统调用实现

## 核心概念

### 进程 vs 线程

在 Pintos 中：
- 一个进程包含一个线程
- 进程拥有独立的地址空间
- 进程通过 `exec()` 创建，通过 `exit()` 终止

### 地址空间布局

```
虚拟地址空间 (4GB)
+------------------+ 0xFFFFFFFF
|   Kernel Space   |  (内核代码和数据)
+------------------+ 0xC0000000 (PHYS_BASE)
|                  |
|   User Stack     |  ↓ 向下增长
|                  |
+------------------+
|                  |
|   Heap           |  ↑ 向上增长 (未实现)
|                  |
+------------------+
|   BSS Segment    |  未初始化数据
+------------------+
|   Data Segment   |  已初始化数据
+------------------+
|   Code Segment   |  代码 (ELF 文件)
+------------------+ 0x08048000 (典型起点)
|   Reserved       |
+------------------+ 0x00000000
```

### 系统调用流程

```
用户程序          内核
   |                |
   |  int 0x30      |
   |------------->  |  <-- 陷入内核
   |                |  syscall_handler()
   |                |  根据 syscall 号分发
   |                |  执行系统调用
   |  iret          |
   |<-------------  |  <-- 返回用户态
   |                |
```

## 任务详解

### 任务 1: 进程加载 (process_execute)

**目标**: 实现可执行文件的加载

**关键步骤**:

1. **解析命令行**
   ```c
   // "ls -l foo" -> args[0]="ls", args[1]="-l", args[2]="foo"
   char *file_name = args[0];  // 可执行文件名
   ```

2. **创建新线程执行 start_process**
   ```c
   tid_t process_execute(const char *file_name) {
     char *fn_copy = palloc_get_page(0);
     strlcpy(fn_copy, file_name, PGSIZE);
     tid_t tid = thread_create(file_name, PRI_DEFAULT,
                               start_process, fn_copy);
     // 等待子进程加载完成
     return tid;
   }
   ```

3. **加载 ELF 文件**
   ```c
   static void start_process(void *file_name_) {
     // 打开文件
     file = filesys_open(file_name);
     // 读取 ELF 头
     if (file_read(file, &ehdr, sizeof ehdr) != sizeof ehdr
         || memcmp(ehdr.e_ident, "\x7fELF", 4) != 0)
       goto fail;
     // 加载段到内存
     // ...
   }
   ```

### 任务 2: 参数传递

**目标**: 正确设置用户栈上的参数

**栈布局**:
```
地址        内容
----        ----
高地址      argv[argc] = NULL  (4 bytes)
            argv[argc-1]       (4 bytes)
            ...
            argv[0]            (4 bytes)
            argv               (4 bytes)  <- 指向 argv[0] 的指针
            argc               (4 bytes)
            返回地址 (假的)     (4 bytes)  <- 栈顶
低地址

参数字符串  按逆序存放
```

**实现要点**:

```c
void setup_stack(void **esp, char **argv, int argc) {
  // 1. 计算总大小
  int total_len = 0;
  for (int i = 0; i < argc; i++)
    total_len += strlen(argv[i]) + 1;

  // 2. 对齐到 4 字节边界
  int word_align = (4 - total_len % 4) % 4;

  // 3. 压入参数字符串（逆序）
  *esp -= total_len + word_align;
  char *args_start = *esp;
  for (int i = argc - 1; i >= 0; i--) {
    *esp -= strlen(argv[i]) + 1;
    memcpy(*esp, argv[i], strlen(argv[i]) + 1);
  }

  // 4. 压入 argv[] 数组
  *esp -= 4;  // argv[argc] = NULL
  **(uint32_t **)esp = 0;

  for (int i = argc - 1; i >= 0; i--) {
    *esp -= 4;
    **(uint32_t **)esp = args_start + /* offset to argv[i] */;
  }

  // 5. 压入 argv, argc, 返回地址
  *esp -= 4;
  **(uint32_t **)esp = *esp + 4;  // argv
  *esp -= 4;
  **(uint32_t **)esp = argc;
  *esp -= 4;
  **(uint32_t **)esp = 0;  // 假的返回地址
}
```

### 任务 3: 系统调用框架

**syscall_handler 结构**:

```c
static void syscall_handler(struct intr_frame *f) {
  // 从用户栈获取系统调用号
  uint32_t *sp = f->esp;
  uint32_t syscall_num = *sp;

  switch (syscall_num) {
    case SYS_HALT:     /* ... */ break;
    case SYS_EXIT:     /* ... */ break;
    case SYS_EXEC:     /* ... */ break;
    case SYS_WAIT:     /* ... */ break;
    case SYS_CREATE:   /* ... */ break;
    case SYS_REMOVE:   /* ... */ break;
    case SYS_OPEN:     /* ... */ break;
    case SYS_FILESIZE: /* ... */ break;
    case SYS_READ:     /* ... */ break;
    case SYS_WRITE:    /* ... */ break;
    case SYS_SEEK:     /* ... */ break;
    case SYS_TELL:     /* ... */ break;
    case SYS_CLOSE:    /* ... */ break;
    default: thread_exit();
  }
}
```

### 任务 4: 具体系统调用

**SYS_EXIT**:
```c
case SYS_EXIT:
  thread_current()->exit_status = *(sp + 1);
  printf("%s: exit(%d)\n", thread_name(), *(sp + 1));
  thread_exit();
```

**SYS_WRITE**:
```c
case SYS_WRITE:
  int fd = *(sp + 1);
  const void *buffer = *(sp + 2);
  unsigned size = *(sp + 3);

  // 验证 buffer 是有效的用户地址
  if (!is_user_vaddr(buffer) || !is_user_vaddr(buffer + size))
    syscall_exit(-1);

  if (fd == STDOUT_FILENO) {
    putbuf(buffer, size);
    f->eax = size;
  } else {
    // 写入文件
    struct file *file = get_file(fd);
    if (file == NULL) f->eax = -1;
    else f->eax = file_write(file, buffer, size);
  }
  break;
```

### 任务 5: 进程等待 (wait)

**目标**: 父进程等待子进程结束并获取退出状态

**实现**:
```c
int process_wait(tid_t child_tid) {
  struct thread *child = get_child_by_tid(child_tid);
  if (child == NULL) return -1;

  // 等待子进程结束
  sema_down(&child->exit_sema);

  int status = child->exit_status;
  list_remove(&child->child_elem);
  sema_up(&child->reap_sema);  // 允许子进程被销毁
  return status;
}
```

## 关键数据结构

### 文件描述符表

```c
struct thread {
  // ...
  struct list file_descriptors;
  int next_fd;  // 下一个可用的 fd 号
};

struct file_descriptor {
  int fd;
  struct file *file;
  struct list_elem elem;
};
```

## 安全考虑

### 用户指针验证

所有来自用户程序的指针都必须验证：

```c
bool is_valid_user_pointer(const void *ptr) {
  // 1. 非 NULL
  if (ptr == NULL) return false;

  // 2. 用户地址空间内
  if (!is_user_vaddr(ptr)) return false;

  // 3. 已映射的页面
  if (pagedir_get_page(thread_current()->pagedir, ptr) == NULL)
    return false;

  return true;
}
```

### 字符串验证

```c
bool is_valid_string(const char *str) {
  if (!is_valid_user_pointer(str)) return false;

  // 检查每个字符直到 '\0'
  while (*str != '\0') {
    str++;
    if (!is_valid_user_pointer(str)) return false;
  }
  return true;
}
```

## 测试列表

- args-single, args-multiple, args-many
- sc-bad-sp, sc-bad-arg
- sc-boundary, sc-boundary-2, sc-boundary-3
- exit, halt
- create, open, close, read, write
- exec, wait, multi-recurse, multi-child-fd
- rox-simple, rox-child, rox-multichild

## 常见陷阱

1. **用户指针未验证**: 导致内核 panic
2. **文件系统并发**: 多个线程同时访问文件
3. **内存泄漏**: 文件描述符未关闭
4. **父子同步**: wait/exit 信号量使用错误

## 参考资源

- [Pintos Lab 2](https://pkuflyingpig.gitbook.io/pintos/project-description/lab2-user-programs)
- [Tacos Lab 2](https://pku-tacos.pages.dev/lab2-userprograms)
- [ELF 格式](https://wiki.osdev.org/ELF)
- [System V ABI](https://wiki.osdev.org/System_V_ABI)
