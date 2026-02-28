# Tacos 环境搭建指南

本指南介绍如何在本地搭建 Tacos (Rust OS) 开发环境。

## 系统要求

- Linux, macOS, 或 Windows (WSL2)
- Rust 工具链 (1.70+)
- QEMU (RISC-V 版本)
- Git

## 安装 Rust

```bash
# 安装 rustup
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# 安装 RISC-V 目标
rustup target add riscv64gc-unknown-none-elf

# 安装必要工具
cargo install cargo-binutils
rustup component add llvm-tools-preview
```

## 安装 QEMU (RISC-V)

### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install qemu-system-misc
```

### macOS

```bash
brew install qemu
```

### 验证安装

```bash
qemu-system-riscv64 --version
```

## 获取代码

```bash
# 克隆 Tacos 仓库
git clone https://github.com/pku-os/tacos.git
cd tacos

# 查看目录结构
ls -la
```

## 目录结构

```
tacos/
├── bootloader/      # Bootloader
├── kernel/          # 内核代码
│   ├── src/
│   │   ├── main.rs
│   │   ├── mm/      # 内存管理
│   │   ├── task/    # 任务调度
│   │   └── syscall/ # 系统调用
│   └── Cargo.toml
├── user/            # 用户程序
└── Cargo.toml       # Workspace
```

## 构建项目

```bash
# 构建内核
cd kernel
cargo build

# 发布构建
cargo build --release
```

## 运行

```bash
# 在 QEMU 中运行
cargo run

# 带调试信息
qemu-system-riscv64 \
  -machine virt \
  -nographic \
  -bios ../bootloader/rustsbi-qemu.bin \
  -device loader,file=target/riscv64gc-unknown-none-elf/release/kernel,addr=0x80200000
```

## 运行测试

```bash
# 运行所有测试
cargo test

# 运行特定测试
cargo test alarm_single

# 带输出
cargo test -- --nocapture
```

## 调试

### GDB 调试

```bash
# 终端 1: 启动 QEMU 并等待 GDB
cd kernel
qemu-system-riscv64 \
  -machine virt \
  -nographic \
  -bios ../bootloader/rustsbi-qemu.bin \
  -device loader,file=target/riscv64gc-unknown-none-elf/release/kernel,addr=0x80200000 \
  -s -S

# 终端 2: 连接 GDB
riscv64-unknown-elf-gdb \
  -ex 'file target/riscv64gc-unknown-none-elf/release/kernel' \
  -ex 'target remote localhost:1234' \
  -ex 'break main' \
  -ex 'continue'
```

### VSCode 调试配置

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Tacos",
      "type": "cppdbg",
      "request": "launch",
      "program": "${workspaceFolder}/kernel/target/riscv64gc-unknown-none-elf/release/kernel",
      "miDebuggerServerAddress": "localhost:1234",
      "miDebuggerPath": "riscv64-unknown-elf-gdb",
      "cwd": "${workspaceFolder}/kernel"
    }
  ]
}
```

## 常见问题

### 问题 1: Rust 版本过旧

**现象**: 编译错误，提示需要新特性

**解决**: 更新 Rust
```bash
rustup update
```

### 问题 2: RISC-V 工具链未安装

**现象**: `target 'riscv64gc-unknown-none-elf' not found`

**解决**:
```bash
rustup target add riscv64gc-unknown-none-elf
```

### 问题 3: QEMU RISC-V 未安装

**现象**: `qemu-system-riscv64: command not found`

**解决**: 确保安装的是 `qemu-system-misc` 包（Ubuntu）或完整 QEMU（macOS）

## 下一步

环境搭建完成后，可以开始 [Lab 0: Appetizer](../../courses/pku-os/labs/lab0-booting/)。
