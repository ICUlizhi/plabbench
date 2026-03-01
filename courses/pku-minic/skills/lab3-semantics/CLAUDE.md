# Lab 3: 语义分析与中间代码生成

## 实验目标

实现语义分析和中间代码（IR）生成：
- 类型检查
- 符号表管理
- 作用域分析
- 生成 Koopa IR

## 核心概念

### 语义分析阶段

语法分析只检查结构是否正确，语义分析检查：
- 变量是否声明
- 类型是否匹配
- 函数调用是否正确
- 返回值是否匹配

### 符号表

符号表存储标识符的信息：

```c
typedef struct Symbol {
    char *name;
    enum { SYM_VAR, SYM_FUNC } kind;
    Type *type;
    int scope_level;      // 作用域层级
    struct Symbol *next;  // 链表中下一个
} Symbol;

typedef struct SymbolTable {
    Symbol *buckets[HASH_SIZE];
    struct SymbolTable *parent;  // 父作用域
} SymbolTable;
```

### 类型系统

MiniC 的类型：

```c
typedef enum {
    TYPE_INT,
    TYPE_VOID,
    TYPE_FUNC,
    TYPE_PTR,    // 可选
} TypeKind;

typedef struct Type {
    TypeKind kind;
    union {
        struct {
            struct Type *ret_type;
            struct Type **param_types;
            int param_count;
        } func;
        struct Type *ptr_to;  // 指针指向的类型
    };
} Type;
```

## 语义检查实现

### 遍历 AST

```c
void semantic_analysis(Node *node, SymbolTable *symtab) {
    switch (node->type) {
        case NODE_FUNC:
            check_func(node, symtab);
            break;
        case NODE_DECL:
            check_decl(node, symtab);
            break;
        case NODE_IDENT:
            check_ident(node, symtab);
            break;
        case NODE_BINOP:
            check_binop(node, symtab);
            break;
        // ...
    }
}
```

### 变量声明检查

```c
void check_decl(Node *node, SymbolTable *symtab) {
    char *name = node->str_val;
    Type *var_type = node->children[0]->type_info;

    // 检查是否已声明
    Symbol *existing = lookup(symtab, name);
    if (existing != NULL) {
        error(node->line, "Variable '%s' already declared", name);
    }

    // 检查初始值类型
    if (node->child_count > 1) {
        Type *init_type = check_expr(node->children[1], symtab);
        if (!types_compatible(var_type, init_type)) {
            error(node->line, "Type mismatch in initialization");
        }
    }

    // 添加到符号表
    Symbol *sym = add_symbol(symtab, name, SYM_VAR, var_type);
    node->sym = sym;
}
```

### 表达式类型检查

```c
Type *check_expr(Node *node, SymbolTable *symtab) {
    switch (node->type) {
        case NODE_NUM:
            return type_int;

        case NODE_IDENT:
            Symbol *sym = lookup(symtab, node->str_val);
            if (sym == NULL) {
                error(node->line, "Undefined variable '%s'", node->str_val);
            }
            if (sym->kind != SYM_VAR) {
                error(node->line, "'%s' is not a variable", node->str_val);
            }
            node->sym = sym;
            return sym->type;

        case NODE_BINOP:
            return check_binop(node, symtab);

        case NODE_CALL:
            return check_call(node, symtab);

        default:
            return type_void;
    }
}

Type *check_binop(Node *node, SymbolTable *symtab) {
    Type *left = check_expr(node->children[0], symtab);
    Type *right = check_expr(node->children[1], symtab);
    char *op = node->str_val;

    if (strcmp(op, "==") == 0 || strcmp(op, "!=") == 0) {
        if (!types_compatible(left, right)) {
            error(node->line, "Cannot compare different types");
        }
        return type_int;
    }

    if (is_arithmetic_op(op)) {
        if (left->kind != TYPE_INT || right->kind != TYPE_INT) {
            error(node->line, "Arithmetic operations require int operands");
        }
        return type_int;
    }

    return type_int;
}
```

### 函数检查

```c
void check_func(Node *node, SymbolTable *symtab) {
    char *name = node->str_val;
    Type *ret_type = node->children[0]->type_info;

    // 添加函数到符号表
    Type *func_type = create_func_type(ret_type);
    Symbol *sym = add_symbol(symtab, name, SYM_FUNC, func_type);

    // 创建新作用域
    SymbolTable *func_symtab = create_symtab(symtab);

    // 检查函数体
    Node *body = node->children[1];
    semantic_analysis(body, func_symtab);

    // 检查返回值
    if (!has_return_stmt(body) && ret_type->kind != TYPE_VOID) {
        error(node->line, "Function '%s' must return a value", name);
    }
}

bool has_return_stmt(Node *node) {
    if (node->type == NODE_RETURN) return true;

    for (int i = 0; i < node->child_count; i++) {
        if (has_return_stmt(node->children[i])) return true;
    }
    return false;
}
```

## Koopa IR

Koopa 是一种结构化中间表示，类似于 LLVM IR 但更简化。

### IR 基本结构

```
fun @main(): i32 {
%entry:
  %x = alloc i32
  store 42, %x
  %0 = load %x
  ret %0
}
```

### IR 生成

```c
typedef struct {
    FILE *out;
    int temp_count;  // 临时变量计数器
    int label_count; // 标签计数器
} IRContext;

const char *new_temp(IRContext *ctx) {
    static char buf[32];
    snprintf(buf, sizeof(buf), "%%%d", ctx->temp_count++);
    return strdup(buf);
}

const char *new_label(IRContext *ctx) {
    static char buf[32];
    snprintf(buf, sizeof(buf), "%%L%d", ctx->label_count++);
    return strdup(buf);
}

// 生成表达式的 IR，返回结果值
const char *gen_expr(Node *node, IRContext *ctx) {
    switch (node->type) {
        case NODE_NUM:
            return format("%d", node->num_val);

        case NODE_IDENT: {
            const char *tmp = new_temp(ctx);
            fprintf(ctx->out, "  %s = load @%s\n", tmp, node->str_val);
            return tmp;
        }

        case NODE_BINOP: {
            const char *left = gen_expr(node->children[0], ctx);
            const char *right = gen_expr(node->children[1], ctx);
            const char *result = new_temp(ctx);

            const char *op;
            if (strcmp(node->str_val, "+") == 0) op = "add";
            else if (strcmp(node->str_val, "-") == 0) op = "sub";
            else if (strcmp(node->str_val, "*") == 0) op = "mul";
            else if (strcmp(node->str_val, "/") == 0) op = "div";
            else if (strcmp(node->str_val, "%") == 0) op = "mod";
            else if (strcmp(node->str_val, "==") == 0) op = "eq";
            else if (strcmp(node->str_val, "!=") == 0) op = "ne";
            else if (strcmp(node->str_val, "<") == 0) op = "lt";
            else if (strcmp(node->str_val, ">") == 0) op = "gt";
            else if (strcmp(node->str_val, "<=") == 0) op = "le";
            else if (strcmp(node->str_val, ">=") == 0) op = "ge";

            fprintf(ctx->out, "  %s = %s %s, %s\n", result, op, left, right);
            return result;
        }

        case NODE_UNARY: {
            const char *operand = gen_expr(node->children[0], ctx);
            const char *result = new_temp(ctx);

            if (strcmp(node->str_val, "-") == 0) {
                fprintf(ctx->out, "  %s = sub 0, %s\n", result, operand);
            } else if (strcmp(node->str_val, "!") == 0) {
                fprintf(ctx->out, "  %s = eq %s, 0\n", result, operand);
            }
            return result;
        }
    }
}

// 生成语句的 IR
void gen_stmt(Node *node, IRContext *ctx) {
    switch (node->type) {
        case NODE_DECL: {
            fprintf(ctx->out, "  @%s = alloc i32\n", node->str_val);
            if (node->child_count > 1) {
                const char *init = gen_expr(node->children[1], ctx);
                fprintf(ctx->out, "  store %s, @%s\n", init, node->str_val);
            }
            break;
        }

        case NODE_RETURN: {
            const char *val = gen_expr(node->children[0], ctx);
            fprintf(ctx->out, "  ret %s\n", val);
            break;
        }

        case NODE_IF: {
            const char *cond = gen_expr(node->children[0], ctx);
            const char *then_label = new_label(ctx);
            const char *end_label = new_label(ctx);
            const char *else_label = node->child_count > 2 ? new_label(ctx) : end_label;

            fprintf(ctx->out, "  br %s, %s, %s\n", cond, then_label, else_label);
            fprintf(ctx->out, "%s:\n", then_label);
            gen_stmt(node->children[1], ctx);

            if (node->child_count > 2) {
                fprintf(ctx->out, "  jump %s\n", end_label);
                fprintf(ctx->out, "%s:\n", else_label);
                gen_stmt(node->children[2], ctx);
            }
            fprintf(ctx->out, "%s:\n", end_label);
            break;
        }

        case NODE_WHILE: {
            const char *entry_label = new_label(ctx);
            const char *body_label = new_label(ctx);
            const char *end_label = new_label(ctx);

            // 保存循环标签用于 break/continue
            ctx->current_loop_end = end_label;
            ctx->current_loop_entry = entry_label;

            fprintf(ctx->out, "  jump %s\n", entry_label);
            fprintf(ctx->out, "%s:\n", entry_label);
            const char *cond = gen_expr(node->children[0], ctx);
            fprintf(ctx->out, "  br %s, %s, %s\n", cond, body_label, end_label);
            fprintf(ctx->out, "%s:\n", body_label);
            gen_stmt(node->children[1], ctx);
            fprintf(ctx->out, "  jump %s\n", entry_label);
            fprintf(ctx->out, "%s:\n", end_label);
            break;
        }

        case NODE_BLOCK:
            for (int i = 0; i < node->child_count; i++) {
                gen_stmt(node->children[i], ctx);
            }
            break;
    }
}

// 生成函数的 IR
void gen_func(Node *node, IRContext *ctx) {
    fprintf(ctx->out, "fun @%s(): i32 {\n", node->str_val);
    fprintf(ctx->out, "%%entry:\n");

    gen_stmt(node->children[1], ctx);

    fprintf(ctx->out, "}\n\n");
}
```

## 常见陷阱

### 1. 作用域嵌套

```c
{
    int x = 1;
    {
        int x = 2;  // 内层 x 遮蔽外层 x
        return x;   // 应该返回 2
    }
}
```

确保符号表正确处理嵌套作用域。

### 2. 短路求值

```c
if (a && b) { ... }  // a 为假时不计算 b
```

生成 IR 时需要正确实现短路逻辑。

### 3. 未初始化变量

```c
int x;
return x;  // 错误：x 未初始化
```

需要跟踪变量的初始化状态。

### 4. 类型转换

```c
int x = 1;
// 没有浮点数，但可能需要处理指针类型转换
```

## 调试技巧

### 打印符号表

```c
void dump_symtab(SymbolTable *symtab, int level) {
    for (int i = 0; i < HASH_SIZE; i++) {
        for (Symbol *s = symtab->buckets[i]; s; s = s->next) {
            printf("%*s%s: %s\n", level * 2, "", s->name,
                   s->kind == SYM_VAR ? "var" : "func");
        }
    }
    if (symtab->parent) {
        dump_symtab(symtab->parent, level + 1);
    }
}
```

### 验证 IR

```bash
# 使用 koopac 验证生成的 IR
koopac output.koopa -o output.json
```

## 参考资源

- [Lab 3 文档](https://pku-minic.github.io/online-doc/#/labs/lab3/)
- [Koopa IR 文档](https://github.com/pku-minic/koopa)
