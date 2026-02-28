# Lab 3b: Mmap Files (内存映射文件)

## 实验目标

实现内存映射文件（Memory-Mapped Files）：
- `mmap` 系统调用：将文件映射到内存
- `munmap` 系统调用：解除内存映射
- 文件与内存的同步

## 核心概念

### 什么是 Mmap

Mmap 允许将文件内容直接映射到进程的地址空间，访问内存即访问文件：

```
进程地址空间
+------------------+
|  已映射文件 A     | <---> 文件 A 磁盘块
|  (只读或读写)     |
+------------------+
|  已映射文件 B     | <---> 文件 B 磁盘块
+------------------+
|      ...         |
+------------------+
```

### 与传统 I/O 对比

| 特性 | Read/Write | Mmap |
|------|------------|------|
| 数据拷贝 | 内核 -> 用户缓冲区 | 直接访问页面 |
| 随机访问 | 需要 seek | 直接指针访问 |
| 大文件处理 | 需要分块读取 | 按需加载页面 |
| 共享 | 困难 | 自然支持 |

## 任务详解

### 任务 1: Mmap 系统调用

**系统调用原型**:
```c
void *mmap(int fd, void *addr, size_t length);
```

**实现步骤**:

```c
void *sys_mmap(int fd, void *addr, size_t length) {
  // 1. 参数验证
  if (fd < 2 || fd >= MAX_FD) return MAP_FAILED;  // 排除 stdin/stdout
  if (length == 0) return MAP_FAILED;
  if (addr != 0) return MAP_FAILED;  // Pintos 要求 addr 必须为 0

  struct file *file = get_file(fd);
  if (file == NULL) return MAP_FAILED;

  // 2. 重新打开文件（每个映射有自己的文件偏移）
  struct file *reopened = file_reopen(file);
  if (reopened == NULL) return MAP_FAILED;

  // 3. 检查文件长度
  off_t file_len = file_length(reopened);
  if (file_len == 0) {
    file_close(reopened);
    return MAP_FAILED;
  }

  // 4. 分配映射 ID
  mapid_t mapid = allocate_mapid();

  // 5. 创建映射结构
  struct mmap_entry *me = malloc(sizeof *me);
  me->mapid = mapid;
  me->file = reopened;
  me->addr = NULL;  // 稍后分配
  me->length = length;
  list_push_back(&thread_current()->mmap_list, &me->elem);

  // 6. 为文件的每个页面创建 SPT 项
  size_t offset = 0;
  void *upage = NULL;

  while (offset < length) {
    // 查找未使用的虚拟地址
    upage = find_unmapped_page(thread_current()->pagedir, upage);
    if (upage == NULL) {
      // 地址空间不足，清理并返回失败
      unmap_all_pages(me);
      return MAP_FAILED;
    }

    size_t read_bytes = (offset + PGSIZE < length) ? PGSIZE : (length - offset);
    size_t zero_bytes = PGSIZE - read_bytes;

    // 创建 SPT 项（MMAP 类型）
    struct spt_entry *spte = malloc(sizeof *spte);
    spte->upage = upage;
    spte->kpage = NULL;
    spte->type = MMAP;  // 新类型
    spte->writable = true;
    spte->loaded = false;
    spte->file = reopened;
    spte->file_offset = offset;
    spte->read_bytes = read_bytes;
    spte->zero_bytes = zero_bytes;
    spte->mmap = me;  // 反向指针

    spt_insert(&thread_current()->spt, spte);

    if (me->addr == NULL) me->addr = upage;
    offset += PGSIZE;
    upage += PGSIZE;
  }

  return me->addr;
}
```

### 任务 2: Munmap 系统调用

**系统调用原型**:
```c
void munmap(mapid_t mapid);
```

**实现**:

```c
void sys_munmap(mapid_t mapid) {
  struct mmap_entry *me = find_mmap_entry(mapid);
  if (me == NULL) return;

  unmap_all_pages(me);
  list_remove(&me->elem);
  free(me);
}

static void unmap_all_pages(struct mmap_entry *me) {
  void *upage = me->addr;
  size_t remaining = me->length;

  while (remaining > 0) {
    struct spt_entry *spte = spt_lookup(&thread_current()->spt, upage);

    if (spte != NULL && spte->type == MMAP) {
      // 如果页面已加载且被修改，写回文件
      if (spte->loaded && spte->kpage != NULL) {
        if (pagedir_is_dirty(thread_current()->pagedir, upage)) {
          write_page_to_file(spte);
        }

        // 释放帧
        frame_free(spte->kpage);
        pagedir_clear_page(thread_current()->pagedir, upage);
      }

      // 从 SPT 中移除
      spt_remove(&thread_current()->spt, spte);
      free(spte);
    }

    upage += PGSIZE;
    remaining -= (remaining > PGSIZE) ? PGSIZE : remaining;
  }

  file_close(me->file);
}
```

### 任务 3: 修改 Page Fault Handler

在 Lab 3a 的基础上添加 MMAP 类型处理：

```c
static bool load_mmap_page(struct spt_entry *spte, void *kpage) {
  // 从文件读取
  off_t bytes_read = file_read_at(spte->file, kpage,
                                   spte->read_bytes, spte->file_offset);
  if (bytes_read != (off_t)spte->read_bytes)
    return false;

  // 零填充剩余部分
  memset(kpage + spte->read_bytes, 0, spte->zero_bytes);
  return true;
}

// 在 page_fault 中添加 case
switch (spte->type) {
  // ... 其他 case ...
  case MMAP:
    success = load_mmap_page(spte, kpage);
    break;
}
```

### 任务 4: 进程退出处理

确保进程退出时自动解除所有映射：

```c
void process_exit(void) {
  struct thread *cur = thread_current();

  // 解除所有 mmap
  struct list_elem *e;
  while (!list_empty(&cur->mmap_list)) {
    e = list_begin(&cur->mmap_list);
    struct mmap_entry *me = list_entry(e, struct mmap_entry, elem);
    sys_munmap(me->mapid);
  }

  // ... 原有清理代码 ...
}
```

## 关键数据结构

### Mmap Entry

```c
struct mmap_entry {
  mapid_t mapid;           // 映射 ID
  struct file *file;       // 映射的文件
  void *addr;              // 起始虚拟地址
  size_t length;           // 映射长度
  struct list_elem elem;   // 用于 mmap_list
};
```

### 扩展 SPT Entry

```c
struct spt_entry {
  // ... Lab 3a 字段 ...
  enum spte_type type;     // 新增 MMAP 类型
  struct mmap_entry *mmap; // 如果是 MMAP 类型，指向 mmap_entry
};
```

## 同步考虑

### 文件修改同步

1. **Munmap 时**: 检查 dirty bit，如果被修改则写回
2. **页置换时**: 如果被修改且是 MMAP 类型，写回文件
3. **进程退出时**: 自动解除所有映射，确保数据写回

### 并发访问

```c
// 写回页面到文件
static void write_page_to_file(struct spt_entry *spte) {
  if (spte->type != MMAP) return;

  off_t bytes_written = file_write_at(spte->file, spte->kpage,
                                       spte->read_bytes, spte->file_offset);
  if (bytes_written != (off_t)spte->read_bytes) {
    PANIC("Failed to write back mmap page");
  }
}
```

## 测试列表

- mmap-read: 读取映射文件
- mmap-write: 写入映射文件
- mmap-shuffle: 随机访问映射
- mmap-twice: 同一文件多次映射
- mmap-exit: 退出时自动解除映射
- mmap-offest: 非零偏移映射
- mmap-bad-fd: 无效文件描述符
- mmap-zero-length: 零长度映射
- mmap-overlap: 重叠映射（应失败）
- mmap-clean: 未修改页面不写入

## 常见陷阱

1. **文件关闭**: munmap 时才关闭文件，不是 mmap 时
2. **重叠映射**: 检查新映射是否与现有映射/栈/堆重叠
3. **写回时机**: 只在必要时写回（dirty page）
4. **长度处理**: 文件长度可能与页面对齐
5. **地址分配**: 确保分配的虚拟地址不冲突

## 调试技巧

```c
// 打印 mmap 信息
void mmap_dump(struct thread *t) {
  struct list_elem *e;
  for (e = list_begin(&t->mmap_list);
       e != list_end(&t->mmap_list);
       e = list_next(e)) {
    struct mmap_entry *me = list_entry(e, struct mmap_entry, elem);
    printf("Mmap: id=%d, addr=%p, length=%zu, file=%p\n",
           me->mapid, me->addr, me->length, me->file);
  }
}
```

## 参考资源

- [Pintos Lab 3b](https://pkuflyingpig.gitbook.io/pintos/project-description/lab3b-mmap-files)
- [Linux mmap man page](https://man7.org/linux/man-pages/man2/mmap.2.html)
- [OSDev Mmap](https://wiki.osdev.org/Mmap)
