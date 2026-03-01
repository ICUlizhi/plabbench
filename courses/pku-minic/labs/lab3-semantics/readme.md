# Lab 3: 语义分析与中间代码生成

## 实验概述

实现语义分析和中间代码（Koopa IR）生成。

## 文档链接

- [Lab 3 文档](https://pku-minic.github.io/online-doc/#/labs/lab3/)

## Skill 文件

查看 [`../../skills/lab3-semantics/CLAUDE.md`](../../skills/lab3-semantics/CLAUDE.md) 获取详细的实现指南。

## 实验目标

1. 实现类型检查
2. 管理符号表和作用域
3. 生成 Koopa IR
4. 检查语义错误

## 语义检查内容

- 变量声明检查（重复声明、未声明使用）
- 类型匹配检查
- 函数调用检查
- 返回值检查

## Koopa IR 示例

### 输入 (MiniC)
```c
int main() {
    int x = 42;
    return x;
}
```

### 输出 (Koopa IR)
```
fun @main(): i32 {
%entry:
  @x = alloc i32
  store 42, @x
  %0 = load @x
  ret %0
}
```

## 运行测试

```bash
# 编译
cd lab3-semantics/source
make

# 生成 IR
./compiler test.c > test.koopa

# 验证 IR
koopac test.koopa
```

## 提交要求

- 完整的语义分析实现
- 实验报告（符号表设计和 IR 生成策略）

## 参考资源

- [Koopa IR 文档](https://github.com/pku-minic/koopa)
