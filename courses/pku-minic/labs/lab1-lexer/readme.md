# Lab 1: 词法分析器 (Lexer)

## 实验概述

实现 MiniC 语言的词法分析器，将源代码字符流转换为 Token 序列。

## 文档链接

- [Lab 1 文档](https://pku-minic.github.io/online-doc/#/labs/lab1/)

## Skill 文件

查看 [`../../skills/lab1-lexer/CLAUDE.md`](../../skills/lab1-lexer/CLAUDE.md) 获取详细的实现指南。

## 实验目标

1. 使用 Flex/Lex 编写词法规则
2. 识别 MiniC 的关键字、标识符、常量和运算符
3. 处理注释和空白字符
4. 实现错误处理

## Token 类型

- **关键字**: `int`, `void`, `if`, `else`, `while`, `break`, `continue`, `return`
- **标识符**: 变量名、函数名
- **常量**: 整数（十进制、八进制、十六进制）
- **运算符**: `+`, `-`, `*`, `/`, `%`, `=`, `==`, `!=`, `<`, `>`, `<=`, `>=`, `&&`, `||`, `!`
- **分隔符**: `(`, `)`, `{`, `}`, `;`, `,`, `:`

## 测试示例

### 输入
```c
int main() {
    return 42;
}
```

### 输出
```
INT
IDENT(main)
LPAREN
RPAREN
LBRACE
RETURN
NUMBER(42)
SEMICOLON
RBRACE
```

## 运行测试

```bash
# 编译词法分析器
cd lab1-lexer/source
flex lexer.l
gcc lex.yy.c -lfl -o lexer

# 运行测试
./lexer < test.c

# 或使用评测脚本
python ../../benchmark/runner.py --lab lab1-lexer
```

## 提交要求

- 完整的 lexer.l 文件
- 实验报告（设计思路和测试结果）

## 参考资源

- [Flex 手册](https://westes.github.io/flex/manual/)
- [正则表达式教程](https://regexone.com/)
