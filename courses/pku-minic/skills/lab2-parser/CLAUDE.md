# Lab 2: 语法分析器 (Parser)

## 实验目标

实现 MiniC 语言的语法分析器，将 Token 序列解析为抽象语法树 (AST)。

## 核心概念

### 什么是语法分析

语法分析是编译器的第二个阶段，根据文法规则将 Token 序列组织成语法树。

```
Tokens: [INT, IDENT("main"), LPAREN, RPAREN, LBRACE,
         RETURN, NUMBER(42), SEMICOLON, RBRACE]
         ↓
AST:
Program
└── Function (name="main", return_type=int)
    └── Block
        └── ReturnStatement
            └── NumberLiteral (value=42)
```

### 上下文无关文法 (CFG)

MiniC 的文法（简化版）：

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
            |   "break" ";"
            |   "continue" ";"
Decl        ::= Type IDENT ["=" Expr] ";"
Expr        ::= Primary
            |   Expr BinOp Expr
            |   UnaryOp Expr
            |   IDENT "(" ")"
Primary     ::= NUMBER | IDENT | "(" Expr ")"
BinOp       ::= "+" | "-" | "*" | "/" | "%"
            |   "==" | "!=" | "<" | ">" | "<=" | ">="
            |   "&&" | "||"
UnaryOp     ::= "+" | "-" | "!"
```

### 递归下降分析

手写递归下降解析器的基本模式：

```c
typedef struct Node {
    enum { NODE_FUNC, NODE_RETURN, NODE_BINOP, ... } type;
    struct Node *children[10];
    int child_count;
    union {
        int num_val;
        char *str_val;
    };
} Node;

// 前瞻 token
token_t lookahead;

void match(token_t expected) {
    if (lookahead == expected) {
        lookahead = next_token();
    } else {
        error("Expected %d, got %d", expected, lookahead);
    }
}

Node *parse_program() {
    Node *node = new_node(NODE_PROGRAM);
    node->children[0] = parse_func_def();
    node->child_count = 1;
    return node;
}

Node *parse_func_def() {
    Node *node = new_node(NODE_FUNC);

    // Type
    node->children[0] = parse_type();

    // IDENT
    if (lookahead == IDENT) {
        node->str_val = strdup(yytext);
        match(IDENT);
    }

    // "("
    match(LPAREN);
    // ")"
    match(RPAREN);

    // Block
    node->children[1] = parse_block();
    node->child_count = 2;

    return node;
}

Node *parse_block() {
    match(LBRACE);
    Node *node = new_node(NODE_BLOCK);

    while (lookahead != RBRACE) {
        node->children[node->child_count++] = parse_stmt();
    }

    match(RBRACE);
    return node;
}

Node *parse_stmt() {
    switch (lookahead) {
        case RETURN:
            return parse_return_stmt();
        case IF:
            return parse_if_stmt();
        case WHILE:
            return parse_while_stmt();
        case LBRACE:
            return parse_block();
        // ...
    }
}

Node *parse_return_stmt() {
    match(RETURN);
    Node *node = new_node(NODE_RETURN);
    node->children[0] = parse_expr();
    match(SEMICOLON);
    return node;
}

Node *parse_expr() {
    // 处理二元表达式（需要处理优先级）
    return parse_or_expr();
}

// 处理优先级：|| -> && -> == != -> < > <= >= -> + - -> * / %
Node *parse_or_expr() {
    Node *left = parse_and_expr();
    while (lookahead == OR) {
        match(OR);
        Node *node = new_node(NODE_BINOP);
        node->str_val = "||";
        node->children[0] = left;
        node->children[1] = parse_and_expr();
        left = node;
    }
    return left;
}

// 类似地实现其他优先级...
```

## Bison 实现

### 基本结构

```bison
%{
#include <stdio.h>
#include <stdlib.h>
#include "ast.h"

extern int yylex(void);
void yyerror(const char *s);
%}

%union {
    int num;
    char *str;
    struct Node *node;
}

%token <num> NUMBER
%token <str> IDENT
%token INT VOID RETURN IF ELSE WHILE BREAK CONTINUE
%token EQ NE LT GT LE GE AND OR

%type <node> CompUnit FuncDef Type Block Stmt Expr Primary

%%

CompUnit
    : FuncDef { root = $1; }
    ;

FuncDef
    : Type IDENT '(' ')' Block {
        $$ = create_func_node($1, $2, $5);
    }
    ;

Type
    : INT  { $$ = create_type_node(TYPE_INT); }
    | VOID { $$ = create_type_node(TYPE_VOID); }
    ;

Block
    : '{' StmtList '}' { $$ = $2; }
    ;

StmtList
    : /* empty */ { $$ = create_block_node(); }
    | StmtList Stmt { add_stmt($1, $2); $$ = $1; }
    ;

Stmt
    : RETURN Expr ';' { $$ = create_return_node($2); }
    | IF '(' Expr ')' Stmt { $$ = create_if_node($3, $5, NULL); }
    | IF '(' Expr ')' Stmt ELSE Stmt { $$ = create_if_node($3, $5, $7); }
    | WHILE '(' Expr ')' Stmt { $$ = create_while_node($3, $5); }
    | Block { $$ = $1; }
    ;

Expr
    : Expr OR Expr  { $$ = create_binop_node("||", $1, $3); }
    | Expr AND Expr { $$ = create_binop_node("&&", $1, $3); }
    | Expr EQ Expr  { $$ = create_binop_node("==", $1, $3); }
    | Expr NE Expr  { $$ = create_binop_node("!=", $1, $3); }
    | Expr LT Expr  { $$ = create_binop_node("<", $1, $3); }
    | Expr GT Expr  { $$ = create_binop_node(">", $1, $3); }
    | Expr LE Expr  { $$ = create_binop_node("<=", $1, $3); }
    | Expr GE Expr  { $$ = create_binop_node(">=", $1, $3); }
    | Expr '+' Expr { $$ = create_binop_node("+", $1, $3); }
    | Expr '-' Expr { $$ = create_binop_node("-", $1, $3); }
    | Expr '*' Expr { $$ = create_binop_node("*", $1, $3); }
    | Expr '/' Expr { $$ = create_binop_node("/", $1, $3); }
    | Expr '%' Expr { $$ = create_binop_node("%", $1, $3); }
    | '!' Expr      { $$ = create_unary_node("!", $2); }
    | '-' Expr      { $$ = create_unary_node("-", $2); }
    | Primary       { $$ = $1; }
    ;

Primary
    : NUMBER { $$ = create_num_node($1); }
    | IDENT  { $$ = create_ident_node($1); }
    | '(' Expr ')' { $$ = $2; }
    ;

%%

void yyerror(const char *s) {
    fprintf(stderr, "Error: %s\n", s);
}
```

### 处理优先级和结合性

```bison
%left OR
%left AND
%left EQ NE
%left LT GT LE GE
%left '+' '-'
%left '*' '/' '%'
%right '!'
%nonassoc UMINUS
```

## AST 节点定义

```c
// ast.h
#ifndef AST_H
#define AST_H

typedef enum {
    NODE_PROGRAM,
    NODE_FUNC,
    NODE_BLOCK,
    NODE_RETURN,
    NODE_IF,
    NODE_WHILE,
    NODE_BINOP,
    NODE_UNARY,
    NODE_NUM,
    NODE_IDENT,
    NODE_DECL,
} NodeType;

typedef struct Node {
    NodeType type;
    struct Node **children;
    int child_count;
    int child_capacity;

    // 数据
    int num_val;
    char *str_val;

    // 源代码位置
    int line, column;
} Node;

// 创建函数
Node *create_node(NodeType type);
Node *create_func_node(Node *ret_type, char *name, Node *body);
Node *create_block_node();
Node *create_return_node(Node *expr);
Node *create_if_node(Node *cond, Node *then_stmt, Node *else_stmt);
Node *create_while_node(Node *cond, Node *body);
Node *create_binop_node(char *op, Node *left, Node *right);
Node *create_unary_node(char *op, Node *operand);
Node *create_num_node(int val);
Node *create_ident_node(char *name);

// 操作函数
void add_child(Node *parent, Node *child);
void free_node(Node *node);
void print_ast(Node *node, int indent);

#endif
```

```c
// ast.c
#include "ast.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

Node *create_node(NodeType type) {
    Node *node = calloc(1, sizeof(Node));
    node->type = type;
    node->child_capacity = 4;
    node->children = malloc(sizeof(Node*) * node->child_capacity);
    return node;
}

Node *create_func_node(Node *ret_type, char *name, Node *body) {
    Node *node = create_node(NODE_FUNC);
    node->str_val = strdup(name);
    add_child(node, ret_type);
    add_child(node, body);
    return node;
}

Node *create_block_node() {
    return create_node(NODE_BLOCK);
}

Node *create_return_node(Node *expr) {
    Node *node = create_node(NODE_RETURN);
    add_child(node, expr);
    return node;
}

Node *create_if_node(Node *cond, Node *then_stmt, Node *else_stmt) {
    Node *node = create_node(NODE_IF);
    add_child(node, cond);
    add_child(node, then_stmt);
    if (else_stmt) add_child(node, else_stmt);
    return node;
}

Node *create_while_node(Node *cond, Node *body) {
    Node *node = create_node(NODE_WHILE);
    add_child(node, cond);
    add_child(node, body);
    return node;
}

Node *create_binop_node(char *op, Node *left, Node *right) {
    Node *node = create_node(NODE_BINOP);
    node->str_val = strdup(op);
    add_child(node, left);
    add_child(node, right);
    return node;
}

Node *create_unary_node(char *op, Node *operand) {
    Node *node = create_node(NODE_UNARY);
    node->str_val = strdup(op);
    add_child(node, operand);
    return node;
}

Node *create_num_node(int val) {
    Node *node = create_node(NODE_NUM);
    node->num_val = val;
    return node;
}

Node *create_ident_node(char *name) {
    Node *node = create_node(NODE_IDENT);
    node->str_val = strdup(name);
    return node;
}

void add_child(Node *parent, Node *child) {
    if (parent->child_count >= parent->child_capacity) {
        parent->child_capacity *= 2;
        parent->children = realloc(parent->children,
                                   sizeof(Node*) * parent->child_capacity);
    }
    parent->children[parent->child_count++] = child;
}

void print_ast(Node *node, int indent) {
    for (int i = 0; i < indent; i++) printf("  ");

    switch (node->type) {
        case NODE_FUNC:
            printf("Func(%s)\n", node->str_val);
            break;
        case NODE_RETURN:
            printf("Return\n");
            break;
        case NODE_BINOP:
            printf("BinOp(%s)\n", node->str_val);
            break;
        case NODE_NUM:
            printf("Num(%d)\n", node->num_val);
            break;
        case NODE_IDENT:
            printf("Ident(%s)\n", node->str_val);
            break;
        default:
            printf("Node(%d)\n", node->type);
    }

    for (int i = 0; i < node->child_count; i++) {
        print_ast(node->children[i], indent + 1);
    }
}
```

## 常见陷阱

### 1. 左递归文法

```bison
// 错误：左递归会导致无限递归
Expr: Expr '+' Term
    | Term
    ;

// 正确：改写为右递归或使用优先级声明
Expr: Term '+' Expr
    | Term
    ;
```

### 2. 悬空 else

```c
if (a) if (b) x; else y;  // else 属于哪个 if？
```

Bison 默认规则：`else` 匹配最近的未匹配的 `if`。

### 3. 优先级冲突

```bison
// 确保声明了正确的优先级
%left '+' '-'
%left '*' '/'
```

### 4. 内存泄漏

```c
// 确保在错误处理时释放内存
void yyerror(const char *s) {
    // 可能需要清理已分配的 AST 节点
    free_ast(root);
}
```

## 调试技巧

### Bison 调试

```bash
# 生成详细报告
bison --verbose --report=all parser.y

# 启用运行时调试
# 在 main 中设置 yydebug = 1;
```

### AST 可视化

```c
void print_dot(Node *node, FILE *fp) {
    static int id = 0;
    int my_id = id++;

    fprintf(fp, "  n%d [label=\"", my_id);
    switch (node->type) {
        case NODE_BINOP: fprintf(fp, "%s", node->str_val); break;
        case NODE_NUM: fprintf(fp, "%d", node->num_val); break;
        default: fprintf(fp, "%d", node->type);
    }
    fprintf(fp, "\"];\n");

    for (int i = 0; i < node->child_count; i++) {
        int child_id = id;
        print_dot(node->children[i], fp);
        fprintf(fp, "  n%d -> n%d;\n", my_id, child_id);
    }
}

// 使用：dot -Tpng ast.dot -o ast.png
```

## 参考资源

- [Lab 2 文档](https://pku-minic.github.io/online-doc/#/labs/lab2/)
- [Bison 手册](https://www.gnu.org/software/bison/manual/)
- [Dragon Book](https://en.wikipedia.org/wiki/Compilers:_Principles,_Techniques,_and_Tools)
