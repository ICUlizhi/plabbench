# PKU Minic 编译原理课程上下文

## 课程信息

- **名称**: 编译原理（编译实践）
- **学期**: 2025 Spring
- **网址**: https://pku-minic.github.io/online-doc/#/
- **GitHub**: https://github.com/pku-minic/online-doc
- **机构**: 北京大学

## 课程目标

实现一个完整的 MiniC 编译器，将 C 语言子集编译为 RISC-V 汇编代码。

## 编译器架构

```
+-------------+     +-------------+     +-------------+
|  Source     | --> |   Lexer     | --> |   Parser    |
|  (.c file)  |     |  (Flex)     |     |  (Bison)    |
+-------------+     +-------------+     +------+------+
                                               |
                                               v
+-------------+     +-------------+     +-------------+
|  RISC-V     | <-- |   CodeGen   | <-- |  Semantic   |
|  Assembly   |     |             |     |  Analysis   |
+-------------+     +-------------+     +-------------+
        ^                                        |
        +-------------+-------------+------------+
                      |             |
               +-------------+ +-------------+
               |  Optimize   | | Symbol Table|
               +-------------+ +-------------+
```

## MiniC 语言特性

### 数据类型

- `int`: 32 位整数
- `void`: 空类型（仅用于函数返回）
- 指针（可选扩展）

### 语法特性

```c
// 变量声明
int a;
int b = 10;

// 常量
int c = 0x1F;  // 十六进制
int d = 042;   // 八进制

// 表达式
a + b;
a - b;
a * b;
a / b;
a % b;
-a;            // 一元负号
!a;            // 逻辑非

// 比较
a < b;
a > b;
a <= b;
a >= b;
a == b;
a != b;

// 赋值
a = b;
a += b;
a -= b;
a *= b;
a /= b;
a %= b;

// 控制流
if (cond) { ... }
if (cond) { ... } else { ... }
while (cond) { ... }
break;
continue;
return expr;

// 函数
def foo(a: int, b: int): int {
  return a + b;
}

// main 函数
def main(): int {
  return foo(1, 2);
}
```

## 常用工具

### Flex (词法分析)

```bash
# 安装
sudo apt-get install flex

# 使用
flex lexer.l       # 生成 lex.yy.c
gcc lex.yy.c -lfl  # 编译
./a.out < test.c   # 运行
```

### Bison (语法分析)

```bash
# 安装
sudo apt-get install bison

# 使用
bison -d parser.y  # 生成 parser.tab.c 和 parser.tab.h
gcc parser.tab.c   # 编译
```

### RISC-V 工具链

```bash
# 安装
sudo apt-get install gcc-riscv64-linux-gnu

# 编译汇编
riscv64-linux-gnu-gcc -march=rv64gc -o output test.S

# 静态链接
riscv64-linux-gnu-gcc -static -o output test.S
```

### QEMU

```bash
# 安装
sudo apt-get install qemu-user

# 运行 RISC-V 程序
qemu-riscv64 ./output
echo $?  # 查看返回值
```

## 开发流程

1. **阅读文档**: 理解本阶段要求
2. **编写代码**: 实现对应功能
3. **本地测试**: 使用提供的测试用例
4. **验证输出**: 确保汇编正确
5. **提交代码**: 通过评测系统

## 测试方法

### 基本测试

```bash
# 编译你的编译器
make

# 编译测试文件
./compiler test.c > test.S

# 汇编和链接
riscv64-linux-gnu-gcc -static test.S -o test

# 运行
qemu-riscv64 ./test
echo $?
```

### 自动化测试

```bash
# 运行评测脚本
python benchmark/runner.py --lab lab1-lexer
```

## 调试技巧

### 词法分析调试

```c
// 在 lexer.l 中添加调试输出
%%
"int"       { printf("TOKEN: INT\n"); return INT; }
[a-zA-Z]+   { printf("TOKEN: IDENT(%s)\n", yytext); return IDENT; }
%%
```

### 语法分析调试

```bash
# Bison 调试输出
bison --verbose --debug parser.y

# 设置环境变量
export YYDEBUG=1
./parser
```

### 中间表示调试

```c
// 打印 AST
void print_ast(Node *node, int indent) {
  for (int i = 0; i < indent; i++) printf("  ");
  printf("%s\n", node_type_to_string(node->type));
  for (int i = 0; i < node->child_count; i++) {
    print_ast(node->children[i], indent + 1);
  }
}
```

### 汇编调试

```bash
# 查看生成的汇编
cat test.S

# 反编译
riscv64-linux-gnu-objdump -d test

# GDB 调试
qemu-riscv64 -g 1234 ./test &
riscv64-linux-gnu-gdb ./test
(gdb) target remote localhost:1234
```

## 常见错误

### 词法分析

- **词法错误**: 无法识别的字符
- **字符串未闭合**: `"abc` 缺少 `"`
- **注释未闭合**: `/* ...` 缺少 `*/`

### 语法分析

- **语法错误**: 不符合文法的代码
- **移进-归约冲突**: 文法歧义
- **归约-归约冲突**: 多个归约选择

### 语义分析

- **未定义变量**: 使用未声明的变量
- **类型不匹配**: 操作数类型不兼容
- **重复定义**: 变量重复声明

### 代码生成

- **寄存器冲突**: 寄存器使用冲突
- **栈不平衡**: 函数调用前后栈不平衡
- **立即数溢出**: 立即数超出范围

## 优化技巧

### 常量折叠

```c
// 优化前
int a = 1 + 2;

// 优化后
int a = 3;
```

### 死代码消除

```c
// 优化前
if (0) { ... }
return 1;
return 2;  // 死代码

// 优化后
return 1;
```

### 窥孔优化

```asm
# 优化前
addi x1, x0, 0

# 优化后
li x1, 0
```

## 参考资源

- [课程主页](https://pku-minic.github.io/online-doc/#/)
- [Flex 手册](https://westes.github.io/flex/manual/)
- [Bison 手册](https://www.gnu.org/software/bison/manual/)
- [RISC-V 指令集](https://riscv.org/technical/specifications/)
- [Compiler Explorer](https://godbolt.org/) - 在线编译器对比

## 提交检查清单

- [ ] 代码能通过所有公开测试用例
- [ ] 没有编译警告
- [ ] 代码风格一致
- [ ] 关键函数有注释
- [ ] 实验报告已完成
- [ ] 报告包含设计思路和测试结果
