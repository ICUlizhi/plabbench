# 全局 Skills

本目录包含跨课程通用的 Claude Code Skills。

## 什么是 Skills

Skills 是 Claude Code 的上下文文件，放在 `CLAUDE.md` 中。当 Claude Code 启动时，会自动读取当前目录和父目录中的 `CLAUDE.md` 文件，获取相关上下文。

## 目录结构

```
skills/
├── README.md           # 本文件
└── {skill-name}/       # 特定 skill
    └── CLAUDE.md       # Skill 内容
```

## 使用方式

在课程目录下创建 `CLAUDE.md`：

```markdown
# 课程上下文

## 基本信息
- 课程名称: ...
- 编程语言: ...

## 常用命令
- 编译: ...
- 测试: ...

## 关键概念
...
```

## 课程特定 Skills

课程特定的 skills 位于 `courses/{course}/skills/` 目录下。

### PKU OS Skills

- `courses/pku-os/skills/CLAUDE.md` - 课程级上下文
- `courses/pku-os/skills/lab0/CLAUDE.md` - Lab 0 提示
- `courses/pku-os/skills/lab1/CLAUDE.md` - Lab 1 提示
- ...

## 编写 Effective Skills 的建议

1. **结构化信息**: 使用标题和列表组织内容
2. **包含代码示例**: 展示关键函数和用法
3. **列出常见陷阱**: 帮助避免常见错误
4. **提供调试技巧**: 快速定位问题
5. **保持简洁**: 聚焦最关键的信息

## 参考

- [Claude Code 文档](https://docs.anthropic.com/en/docs/claude-code/overview)
