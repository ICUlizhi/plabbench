# Lab 2: 语法分析器 (Parser)

## 实验概述

实现 MiniC 语言的语法分析器，将 Token 序列解析为抽象语法树 (AST)。

## 文档链接

- [Lab 2 文档](https://pku-minic.github.io/online-doc/#/labs/lab2/)

## Skill 文件

查看 [`../../skills/lab2-parser/CLAUDE.md`](../../skills/lab2-parser/CLAUDE.md) 获取详细的实现指南。

## 实验目标

1. 使用 Bison/Yacc 或手写递归下降实现语法分析
2. 处理运算符优先级和结合性
3. 构建抽象语法树 (AST)
4. 实现错误恢复

## 文法结构

```
CompUnit    ::= FuncDef
FuncDef     ::= Type IDENT "(" ")" Block
Type        ::= "int" | "void"
Block       ::= "{" {Stmt} "}"
Stmt        ::= "return" Expr ";"
            |   "if" "(" Expr ")" Stmt ["else" Stmt]
            |   "while" "(" Expr ")" Stmt
            |   Block
            |   Decl
            |   Expr ";"
Decl        ::= Type IDENT ["=" Expr] ";"
Expr        ::= Primary
            |   Expr BinOp Expr
            |   UnaryOp Expr
Primary     ::= NUMBER | IDENT | "(" Expr ")"
```

## 测试示例

### 输入
```c
int main() {
    return 1 + 2 * 3;
}
```

### AST 输出
```
Program
└── Function(main)
    └── Block
        └── Return
            └── BinOp(+)
                ├── Number(1)
                └── BinOp(*)
                    ├── Number(2)
                    └── Number(3)
```

## 运行测试

```bash
# 编译（使用 Bison + Flex）
cd lab2-parser/source
bison -d parser.y
flex lexer.l
gcc parser.tab.c lex.yy.c -o parser

# 运行测试
./parser test.c
```

## 提交要求

- 完整的 parser.y、lexer.l 和 ast.c/h 文件
- 实验报告（文法设计和 AST 结构）

## 参考资源

- [Bison 手册](https://www.gnu.org/software/bison/manual/)
- [Dragon Book](https://en.wikipedia.org/wiki/Compilers:_Principles,_Techniques,_and_Tools)
