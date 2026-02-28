# Pintos 环境搭建指南

本指南介绍如何在本地搭建 Pintos 开发环境。

## 系统要求

- Linux (Ubuntu 20.04+ 推荐) 或 macOS
- GCC 编译器
- GDB 调试器
- QEMU 模拟器
- Make 工具

## 安装依赖

### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    gdb \
    qemu-system-x86 \
    git \
    vim
```

### macOS

```bash
# 使用 Homebrew
brew install qemu gdb make
```

## 获取代码

```bash
# 克隆 Pintos 仓库
git clone https://github.com/pku-os/Pintos.git
cd Pintos

# 查看目录结构
ls -la
```

## 目录结构

```
Pintos/
├── src/
│   ├── threads/     # Lab 1: 线程管理
│   ├── userprog/    # Lab 2: 用户程序
│   ├── vm/          # Lab 3: 虚拟内存
│   ├── filesys/     # 文件系统
│   └── devices/     # 设备驱动
├── docs/            # 文档
└── tests/           # 测试用例
```

## 构建项目

```bash
cd src/threads
make
```

如果构建成功，会生成 `build/` 目录。

## 运行测试

```bash
# 运行所有测试
make check

# 运行单个测试
make tests/threads/alarm-single.result

# 查看测试结果
cat build/tests/threads/alarm-single.result
cat build/tests/threads/alarm-single.output
```

## 调试

### GDB 调试

```bash
# 启动 Pintos 并等待 GDB 连接
pintos --gdb -- run alarm-single

# 在另一个终端
cd build
pintos-gdb kernel.o
(gdb) target remote localhost:1234
(gdb) continue
```

### 常用 GDB 命令

| 命令 | 说明 |
|------|------|
| `break function` | 设置断点 |
| `continue` | 继续运行 |
| `next` | 单步执行（不进入函数） |
| `step` | 单步执行（进入函数） |
| `print var` | 打印变量 |
| `backtrace` | 查看调用栈 |
| `info registers` | 查看寄存器 |

## 常见问题

### 问题 1: make 报错

**现象**: `make: *** No rule to make target ...`

**解决**: 确保在正确的目录下运行 make：
```bash
cd src/threads  # 或 userprog, vm
make
```

### 问题 2: QEMU 无法启动

**现象**: `qemu-system-x86_64: command not found`

**解决**: 安装 QEMU：
```bash
sudo apt-get install qemu-system-x86
```

### 问题 3: 权限问题

**现象**: 无法执行 pintos 脚本

**解决**: 添加执行权限：
```bash
chmod +x ../../utils/pintos
chmod +x ../../utils/pintos-gdb
```

## VSCode 配置

### 推荐插件

- C/C++ (Microsoft)
- GDB Debugger
- Makefile Tools

### launch.json 示例

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Pintos",
      "type": "cppdbg",
      "request": "launch",
      "program": "${workspaceFolder}/src/threads/build/kernel.o",
      "miDebuggerServerAddress": "localhost:1234",
      "miDebuggerPath": "gdb",
      "cwd": "${workspaceFolder}/src/threads/build"
    }
  ]
}
```

## 下一步

环境搭建完成后，可以开始 [Lab 1: Threads](../../courses/pku-os/labs/lab1-threads/)。
