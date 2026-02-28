# Lab 0: Booting / Appetizer

## 实验目标

理解操作系统的启动过程，包括：
- Bootloader 的工作原理
- 从实模式切换到保护模式
- 加载内核到内存
- 建立基本的运行环境

## 核心概念

### 启动流程

1. **BIOS/UEFI**: 硬件初始化，加载 Bootloader
2. **Bootloader**: 从磁盘加载内核，设置保护模式
3. **Kernel Entry**: 初始化内核，跳转到主函数

### 实模式 vs 保护模式

| 特性 | 实模式 | 保护模式 |
|------|--------|----------|
| 地址空间 | 1MB (20位) | 4GB (32位) |
| 内存保护 | 无 | 有 |
| 特权级 | 无 | Ring 0-3 |

### 关键汇编指令

```asm
; 关中断
cli

; 加载 GDT
lgdt gdtdesc

; 开启保护模式 (设置 CR0.PE)
movl %cr0, %eax
orl $0x1, %eax
movl %eax, %cr0

; 长跳转进入保护模式
ljmp $0x8, $start32
```

## Pintos 关键点

### 文件位置

- `boot/loader.S`: Bootloader 汇编代码
- `boot/start.S`: 内核入口（保护模式）
- `threads/start.S`: 内核初始化
- `threads/init.c`: 主初始化函数

### 需要理解的内容

1. **Loader 如何读取磁盘**
   - 使用 BIOS 中断 `int $0x13`
   - 加载内核到内存 0x20000

2. **GDT 设置**
   - 代码段描述符
   - 数据段描述符

3. **页表初始化**
   - `paging_init()` 函数
   - 将虚拟地址映射到物理地址

## Tacos 关键点

### 文件位置

- `bootloader/src/main.rs`: Bootloader
- `kernel/src/entry.asm`: 内核入口
- `kernel/src/main.rs`: 主函数

### 需要理解的内容

1. **Rust 内联汇编**
   ```rust
   asm!(
       "li sp, {boot_stack_top}",
       boot_stack_top = const BOOT_STACK_TOP,
   )
   ```

2. **页表设置**
   - `PageTable` 结构
   - 递归页表映射

## 常见错误

### Pintos

1. **A20 线未启用**: 无法访问高于 1MB 的内存
2. **GDT 设置错误**: 段选择子不正确
3. **页表映射错误**: 虚拟地址和物理地址对应关系错误

### Tacos

1. **栈未对齐**: RISC-V 要求 16 字节对齐
2. **页表权限错误**: 缺少必要的标志位

## 调试方法

### QEMU 调试

```bash
# 带调试信息启动
pintos --gdb -- run

# 在另一个终端
gdb
(gdb) target remote localhost:1234
(gdb) break *0x7c00   # Bootloader 入口
```

### 打印输出

使用 `vga_putc()` 或串口输出查看启动日志。

## 参考资源

- [OSDev Boot Sequence](https://wiki.osdev.org/Boot_Sequence)
- [OSDev Protected Mode](https://wiki.osdev.org/Protected_Mode)
- [Pintos Booting Guide](https://pkuflyingpig.gitbook.io/pintos/project-description/lab0-booting)
- [Tacos Lab 0](https://pku-tacos.pages.dev/lab0-appetizer)
