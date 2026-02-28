# Lab 3a: Virtual Memory - Demand Paging

## 实验目标

实现按需分页（Demand Paging）虚拟内存系统：
- 页表管理（补充页表 Supplemental Page Table）
- 页面错误处理（Page Fault Handler）
- 帧管理（Frame Table）
- 页面置换算法（Page Replacement）
- 交换空间（Swap）

## 核心概念

### 虚拟内存 vs 物理内存

```
虚拟地址空间                    物理内存
+-------------+                +-------------+
|  Page 0     | --->| PTE | --->| Frame 3     |
|  (code)     |   |  |        |             |
+-------------+   |  |        +-------------+
|  Page 1     |   |  |        | Frame 1     |
|  (data)     | --->|        |             |
+-------------+                +-------------+
|  Page 2     | ---X (未分配)  | Frame 2     |
|             |                |             |
+-------------+                +-------------+

PTE: Page Table Entry
```

### 页面错误类型

| 类型 | 原因 | 处理 |
|------|------|------|
| 访问未映射页 | 首次访问 | 分配帧，加载数据 |
| 访问已换出页 | 页面被换出 | 从 swap 读回 |
| 写只读页 | 写时复制 | 复制页面 |
| 无效访问 | 空指针等 | 终止进程 |

### 补充页表 (SPT)

Pintos 原有页表只记录虚拟->物理映射，我们需要补充信息：

```c
struct supplemental_page_table_entry {
  void *upage;           // 虚拟页地址
  void *kpage;           // 物理帧地址（可能为 NULL）

  // 页面状态
  enum spte_type type;   // FILE, SWAP, ZERO, etc.
  bool writable;
  bool loaded;

  // FILE 类型
  struct file *file;
  off_t file_offset;
  size_t read_bytes;
  size_t zero_bytes;

  // SWAP 类型
  size_t swap_slot;

  // 用于 frame table
  struct list_elem frame_elem;
};
```

## 任务详解

### 任务 1: Frame Table (帧表)

**目标**: 管理物理帧，记录每个帧的使用情况

**数据结构**:
```c
struct frame {
  void *kpage;              // 物理帧地址
  struct spt_entry *spte;   // 对应的 SPT 项
  struct thread *thread;    // 使用此帧的线程
  struct list_elem elem;    // 用于 frame list
};

static struct list frame_table;  // 所有帧的列表
static struct lock frame_lock;   // 保护 frame_table
```

**函数实现**:

```c
// 分配一个物理帧
void *frame_alloc(enum palloc_flags flags, struct spt_entry *spte) {
  lock_acquire(&frame_lock);

  void *kpage = palloc_get_page(flags);
  if (kpage == NULL) {
    // 内存不足，需要置换页面
    kpage = frame_evict(flags);
  }

  if (kpage != NULL) {
    struct frame *frame = malloc(sizeof *frame);
    frame->kpage = kpage;
    frame->spte = spte;
    frame->thread = thread_current();
    list_push_back(&frame_table, &frame->elem);
  }

  lock_release(&frame_lock);
  return kpage;
}

// 释放帧
void frame_free(void *kpage) {
  lock_acquire(&frame_lock);

  struct frame *f = frame_lookup(kpage);
  if (f != NULL) {
    list_remove(&f->elem);
    free(f);
  }
  palloc_free_page(kpage);

  lock_release(&frame_lock);
}
```

### 任务 2: Page Fault Handler

**目标**: 处理页面错误，按需加载页面

```c
static void page_fault(struct intr_frame *f) {
  bool not_present;  // true = 页面不存在；false = 权限错误
  bool write;        // 访问类型
  bool user;         // 用户/内核态
  void *fault_addr;  // 故障地址

  // 获取故障信息
  asm ("movl %%cr2, %0" : "=r" (fault_addr));

  // 检查地址有效性
  if (!is_user_vaddr(fault_addr)) {
    exit(-1);  // 无效地址，终止进程
  }

  void *upage = pg_round_down(fault_addr);
  struct spt_entry *spte = spt_lookup(&thread_current()->spt, upage);

  if (spte == NULL) {
    // 栈增长检查
    if (is_stack_growth(fault_addr, f->esp)) {
      spte = stack_grow(upage);
    } else {
      exit(-1);  // 无效访问
    }
  }

  // 分配帧并加载页面
  void *kpage = frame_alloc(PAL_USER, spte);
  if (kpage == NULL) exit(-1);

  // 根据类型加载数据
  switch (spte->type) {
    case FILE:
      load_file_page(spte, kpage);
      break;
    case SWAP:
      load_swap_page(spte, kpage);
      break;
    case ZERO:
      memset(kpage, 0, PGSIZE);
      break;
  }

  // 设置页表映射
  if (!pagedir_set_page(thread_current()->pagedir, upage, kpage, spte->writable)) {
    frame_free(kpage);
    exit(-1);
  }

  spte->kpage = kpage;
  spte->loaded = true;
}
```

### 任务 3: Lazy Loading (懒加载)

**目标**: 进程启动时不加载所有页面，按需加载

**修改 process.c**:
```c
bool load_segment(struct file *file, off_t ofs, uint8_t *upage,
                  uint32_t read_bytes, uint32_t zero_bytes,
                  bool writable) {
  // 不立即分配帧，只记录到 SPT
  while (read_bytes > 0 || zero_bytes > 0) {
    size_t page_read_bytes = read_bytes < PGSIZE ? read_bytes : PGSIZE;
    size_t page_zero_bytes = PGSIZE - page_read_bytes;

    // 创建 SPT 项，标记为 FILE 类型
    struct spt_entry *spte = malloc(sizeof *spte);
    spte->upage = upage;
    spte->kpage = NULL;
    spte->type = FILE;
    spte->writable = writable;
    spte->loaded = false;
    spte->file = file;
    spte->file_offset = ofs;
    spte->read_bytes = page_read_bytes;
    spte->zero_bytes = page_zero_bytes;

    spt_insert(&thread_current()->spt, spte);

    read_bytes -= page_read_bytes;
    zero_bytes -= page_zero_bytes;
    upage += PGSIZE;
    ofs += page_read_bytes;
  }
  return true;
}

// 在 page fault 时真正加载
static bool load_file_page(struct spt_entry *spte, void *kpage) {
  file_read_at(spte->file, kpage, spte->read_bytes, spte->file_offset);
  memset(kpage + spte->read_bytes, 0, spte->zero_bytes);
  return true;
}
```

### 任务 4: Stack Growth (栈增长)

**目标**: 自动扩展用户栈

```c
#define STACK_MAX (8 * 1024 * 1024)  // 最大栈大小 8MB

bool is_stack_growth(void *fault_addr, void *esp) {
  // 栈向下增长，检查故障地址是否在栈区域附近
  return fault_addr >= PHYS_BASE - STACK_MAX
      && fault_addr < PHYS_BASE
      && fault_addr >= esp - 32;  // 允许一定余量
}

struct spt_entry *stack_grow(void *upage) {
  void *kpage = frame_alloc(PAL_ZERO | PAL_USER, NULL);
  if (kpage == NULL) return NULL;

  struct spt_entry *spte = malloc(sizeof *spte);
  spte->upage = upage;
  spte->kpage = kpage;
  spte->type = ZERO;
  spte->writable = true;
  spte->loaded = true;

  pagedir_set_page(thread_current()->pagedir, upage, kpage, true);
  spt_insert(&thread_current()->spt, spte);

  return spte;
}
```

### 任务 5: Page Replacement (页面置换)

**目标**: 当内存不足时，选择页面换出到 swap

**Second Chance (Clock) 算法**:
```c
void *frame_evict(enum palloc_flags flags) {
  static struct list_elem *clock_hand = NULL;

  lock_acquire(&frame_lock);

  while (true) {
    if (clock_hand == NULL || clock_hand == list_end(&frame_table))
      clock_hand = list_begin(&frame_table);

    struct frame *frame = list_entry(clock_hand, struct frame, elem);
    struct thread *t = frame->thread;

    // 检查访问位
    if (pagedir_is_accessed(t->pagedir, frame->spte->upage)) {
      // 给第二次机会
      pagedir_set_accessed(t->pagedir, frame->spte->upage, false);
      clock_hand = list_next(clock_hand);
    } else {
      // 选择此帧置换
      if (pagedir_is_dirty(t->pagedir, frame->spte->upage)
          || frame->spte->type == SWAP) {
        // 写入 swap
        frame->spte->swap_slot = swap_out(frame->kpage);
        frame->spte->type = SWAP;
      }

      // 清除页表映射
      pagedir_clear_page(t->pagedir, frame->spte->upage);
      frame->spte->kpage = NULL;
      frame->spte->loaded = false;

      void *kpage = frame->kpage;
      list_remove(&frame->elem);
      free(frame);

      lock_release(&frame_lock);
      return kpage;
    }
  }
}
```

### 任务 6: Swap Space (交换空间)

**目标**: 管理磁盘上的交换空间

```c
#define SWAP_FREE 0
#define SWAP_USED 1

static struct block *swap_block;
static struct bitmap *swap_bitmap;
static struct lock swap_lock;

void swap_init(void) {
  swap_block = block_get_role(BLOCK_SWAP);
  if (swap_block == NULL) PANIC("No swap device");

  // 每个 swap slot 是一个页面大小
  size_t swap_size = block_size(swap_block) / (PGSIZE / BLOCK_SECTOR_SIZE);
  swap_bitmap = bitmap_create(swap_size);
  bitmap_set_all(swap_bitmap, SWAP_FREE);
  lock_init(&swap_lock);
}

// 将页面写入 swap，返回 slot 号
size_t swap_out(void *kpage) {
  lock_acquire(&swap_lock);

  size_t slot = bitmap_scan_and_flip(swap_bitmap, 0, 1, SWAP_FREE);
  if (slot == BITMAP_ERROR) PANIC("Swap full");

  // 写入磁盘
  for (size_t i = 0; i < PGSIZE / BLOCK_SECTOR_SIZE; i++) {
    block_write(swap_block, slot * (PGSIZE / BLOCK_SECTOR_SIZE) + i,
                kpage + i * BLOCK_SECTOR_SIZE);
  }

  lock_release(&swap_lock);
  return slot;
}

// 从 swap 读回页面
void swap_in(size_t slot, void *kpage) {
  lock_acquire(&swap_lock);

  ASSERT(bitmap_test(swap_bitmap, slot) == SWAP_USED);

  for (size_t i = 0; i < PGSIZE / BLOCK_SECTOR_SIZE; i++) {
    block_read(swap_block, slot * (PGSIZE / BLOCK_SECTOR_SIZE) + i,
               kpage + i * BLOCK_SECTOR_SIZE);
  }

  bitmap_set(swap_bitmap, slot, SWAP_FREE);
  lock_release(&swap_lock);
}
```

## 关键文件

| 文件 | 说明 |
|------|------|
| `vm/page.c` | 补充页表实现 |
| `vm/frame.c` | 帧管理 |
| `vm/swap.c` | 交换空间 |
| `userprog/process.c` | 懒加载修改 |
| `userprog/exception.c` | 页面错误处理 |

## 测试列表

- page-linear, page-parallel
- page-merge-seq, page-merge-par
- page-merge-stk
- page-merge-mm
- page-shuffle
- mmap-read, mmap-write
- mmap-shuffle, mmap-twice
- bad-read, bad-write, bad-jump
- bad-read2, bad-write2, bad-jump2
- sc-bad-sp, sc-bad-arg
- sc-boundary, sc-boundary-2
- sc-boundary-3

## 常见陷阱

1. **同步问题**: frame_table 和 swap_bitmap 需要锁保护
2. **内存泄漏**: SPT 项和帧未正确释放
3. **栈边界**: 未正确处理最大栈限制
4. **文件同步**: 懒加载时需要保持文件打开状态
5. **页表同步**: 修改 SPT 后需要同步页目录

## 调试技巧

```c
// 打印 SPT 信息
void spt_dump(struct hash *spt) {
  struct hash_iterator i;
  hash_first(&i, spt);
  while (hash_next(&i)) {
    struct spt_entry *e = hash_entry(hash_cur(&i), struct spt_entry, elem);
    printf("SPT: upage=%p, kpage=%p, type=%d, loaded=%d\n",
           e->upage, e->kpage, e->type, e->loaded);
  }
}

// 检查帧表
void frame_dump(void) {
  struct list_elem *e;
  for (e = list_begin(&frame_table); e != list_end(&frame_table);
       e = list_next(e)) {
    struct frame *f = list_entry(e, struct frame, elem);
    printf("Frame: kpage=%p, thread=%s, upage=%p\n",
           f->kpage, f->thread->name, f->spte->upage);
  }
}
```

## 参考资源

- [Pintos Lab 3a](https://pkuflyingpig.gitbook.io/pintos/project-description/lab3a-demand-paging)
- [Tacos Lab 3](https://pku-tacos.pages.dev/lab3-virtual_memory)
- [OSDev Paging](https://wiki.osdev.org/Paging)
- [OSDev Page Frame Allocation](https://wiki.osdev.org/Page_Frame_Allocation)
