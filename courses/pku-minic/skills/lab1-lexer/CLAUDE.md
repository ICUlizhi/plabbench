# Lab 1: 词法分析器 (Lexer)

## 实验目标

实现 MiniC 语言的词法分析器，将源代码转换为 Token 序列。

## 核心概念

### 什么是词法分析

词法分析是编译器的第一个阶段，将字符流转换为有意义的词法单元 (Token) 序列。

```
源代码: int main() { return 0; }
         ↓
Tokens: [INT, IDENT("main"), LPAREN, RPAREN, LBRACE,
         RETURN, NUMBER(0), SEMICOLON, RBRACE]
```

### Token 类型

| Token | 示例 | 说明 |
|-------|------|------|
| INT | `int` | 整型关键字 |
| VOID | `void` | 空类型关键字 |
| IF | `if` | 条件关键字 |
| ELSE | `else` | 否则关键字 |
| WHILE | `while` | 循环关键字 |
| RETURN | `return` | 返回关键字 |
| IDENT | `foo`, `x1` | 标识符 |
| NUMBER | `42`, `0x2A` | 整数常量 |
| ASSIGN | `=` | 赋值 |
| PLUS | `+` | 加 |
| MINUS | `-` | 减 |
| MUL | `*` | 乘 |
| DIV | `/` | 除 |
| MOD | `%` | 取模 |
| EQ | `==` | 等于 |
| NE | `!=` | 不等于 |
| LT | `<` | 小于 |
| GT | `>` | 大于 |
| LE | `<=` | 小于等于 |
| GE | `>=` | 大于等于 |
| AND | `&&` | 逻辑与 |
| OR | `\|\|` | 逻辑或 |
| NOT | `!` | 逻辑非 |
| LPAREN | `(` | 左括号 |
| RPAREN | `)` | 右括号 |
| LBRACE | `{` | 左花括号 |
| RBRACE | `}` | 右花括号 |
| SEMICOLON | `;` | 分号 |
| COMMA | `,` | 逗号 |
| COLON | `:` | 冒号 |

## Flex 实现

### 基本结构

```c
%{
#include <stdio.h>
#include "token.h"
%}

%option noyywrap

%%

 /* 关键字 */
int         { return INT; }
void        { return VOID; }
if          { return IF; }
else        { return ELSE; }
while       { return WHILE; }
break       { return BREAK; }
continue    { return CONTINUE; }
return      { return RETURN; }

 /* 标识符 */
[a-zA-Z_][a-zA-Z0-9_]*  { return IDENT; }

 /* 数字 */
[0-9]+      { return NUMBER; }
0x[0-9a-fA-F]+  { return NUMBER; }  /* 十六进制 */
0[0-7]*     { return NUMBER; }      /* 八进制 */

 /* 运算符 */
"+"         { return PLUS; }
"-"         { return MINUS; }
"*"         { return MUL; }
"/"         { return DIV; }
"%"         { return MOD; }
"="         { return ASSIGN; }
"=="        { return EQ; }
"!="        { return NE; }
"<"         { return LT; }
">"         { return GT; }
"<="        { return LE; }
">="        { return GE; }
"&&"        { return AND; }
"||"        { return OR; }
"!"         { return NOT; }

 /* 分隔符 */
"("         { return LPAREN; }
")"         { return RPAREN; }
"{"         { return LBRACE; }
"}"         { return RBRACE; }
";"         { return SEMICOLON; }
","         { return COMMA; }
":"         { return COLON; }

 /* 空白字符 */
[ \t\n]+    { /* 忽略 */ }

 /* 注释 */
"//".*      { /* 忽略单行注释 */ }
"/*"([^*]|\*+[^*/])*"*+""/"  { /* 忽略多行注释 */ }

 /* 错误处理 */
.           { printf("Error: unknown character %s\n", yytext); exit(1); }

%%
```

### 获取 Token 值

```c
// 使用 yylval 传递值
%{
#include "token.h"
%}

%union {
    int num;
    char *str;
}

%token <num> NUMBER
%token <str> IDENT
```

### 位置追踪

```c
%{
#define YY_USER_ACTION \
    yylloc.first_line = yylloc.last_line; \
    yylloc.first_column = yylloc.last_column; \
    if (yylloc.last_line == yylineno) \
        yylloc.last_column += yyleng; \
    else { \
        yylloc.last_line = yylineno; \
        yylloc.last_column = yyleng; \
    }
%}
%option yylineno
```

## 手动实现 (可选)

如果不使用 Flex，可以手写词法分析器：

```c
typedef enum {
    TOK_INT, TOK_IDENT, TOK_NUMBER, TOK_PLUS, /* ... */
} TokenType;

typedef struct {
    TokenType type;
    char *text;
    int line, column;
} Token;

Token next_token(const char **p) {
    // 跳过空白
    while (isspace(**p)) (*p)++;

    // 识别关键字和标识符
    if (isalpha(**p)) {
        const char *start = *p;
        while (isalnum(**p)) (*p)++;
        int len = *p - start;

        if (strncmp(start, "int", len) == 0) return (Token){TOK_INT};
        if (strncmp(start, "if", len) == 0) return (Token){TOK_IF};
        // ...
        return (Token){TOK_IDENT, strndup(start, len)};
    }

    // 识别数字
    if (isdigit(**p)) {
        int val = 0;
        while (isdigit(**p)) {
            val = val * 10 + (**p - '0');
            (*p)++;
        }
        return (Token){TOK_NUMBER, .value = val};
    }

    // 识别运算符
    switch (**p) {
        case '+': (*p)++; return (Token){TOK_PLUS};
        case '-': (*p)++; return (Token){TOK_MINUS};
        // ...
    }

    return (Token){TOK_EOF};
}
```

## 测试

### 测试文件

```c
// test1.c
int main() {
    return 42;
}
```

### 期望输出

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
EOF
```

### 运行测试

```bash
flex lexer.l
gcc lex.yy.c -lfl
./a.out < test1.c
```

## 常见陷阱

### 1. 注释嵌套

```c
/* 外层 /* 内层 */ 结束 */
```

Flex 的正则表达式不支持嵌套注释，需要特殊处理。

### 2. 保留字 vs 标识符

```c
int int = 1;  // 错误：int 是关键字
```

确保关键字在标识符规则之前匹配。

### 3. 最长的匹配

```c
int foo;
```

应该匹配 `int` + `foo`，而不是 `i` + `nt` + `foo`。

Flex 默认选择最长匹配，但需要确保规则正确。

### 4. 数字格式

```c
0xGG   // 错误：无效十六进制
09     // 错误：无效八进制
```

需要在词法阶段还是语法阶段检查？

## 调试技巧

```c
/* 在 lexer.l 中添加调试输出 */
#ifdef DEBUG
#define LOG(msg) printf("[LEXER] %s: %s\n", msg, yytext)
#else
#define LOG(msg)
#endif

%%
int     { LOG("INT"); return INT; }
[0-9]+  { LOG("NUMBER"); return NUMBER; }
```

## 参考资源

- [Lab 1 文档](https://pku-minic.github.io/online-doc/#/labs/lab1/)
- [Flex 手册](https://westes.github.io/flex/manual/)
- [正则表达式教程](https://regexone.com/)
