# Plabbench

## 项目简介

Plabbench 是一个用于评测 AI 编程助手在北大计算机课程 lab 上表现的基准测试平台。我们收集并管理课程 lab 内容，构建 AI 辅助技能库，并提供详细的使用教程。

## 支持的课程

| 课程 | 学期 | 状态 |
|------|------|------|
| [操作系统（实验班）](courses/pku-os/) | 2025 Spring | 进行中 |

## 项目结构

```
plabbench/
├── docs/                   # 文档和教程
│   ├── tutorials/          # 使用教程
│   │   ├── claude-code-guide.md
│   │   ├── kimi-code-guide.md
│   │   └── pku-os/         # OS 课程教程
│   └── benchmarks/         # 评测报告
├── courses/                # 课程目录
│   └── pku-os/             # 北大操作系统
│       ├── skills/         # Claude Code Skills
│       ├── labs/           # Lab 内容
│       └── benchmark/      # 评测相关
├── skills/                 # 全局 Skills
└── scripts/                # 工具脚本
```

## 快速开始

### 1. 环境准备

确保已安装：
- Python 3.8+
- Git
- [Claude Code](https://claude.ai/code) 或 [Kimi Code](https://kimi.moonshot.cn/)

### 2. 使用 Claude Code 完成 Lab

```bash
# 进入课程目录
cd courses/pku-os

# 启动 Claude Code（会自动加载 skills/CLAUDE.md）
claude

# 在 Claude Code 中请求帮助
> 帮我完成 Lab 1 的线程调度部分
```

### 3. 运行评测

```bash
# 运行特定 lab 的评测
python courses/pku-os/benchmark/runner.py --lab lab1-threads --track pintos

# 查看评测报告
cat courses/pku-os/benchmark/results/latest.json
```

## 评测指标

| 指标 | 说明 |
|------|------|
| 通过率 | 通过测试数 / 总测试数 |
| 代码质量 | 编译警告数 |
| 代码行数 | 修改的代码量 |
| 完成时间 | AI 解题耗时（分钟）|

## 贡献指南

1. **添加新 Lab**: 在 `courses/<course>/labs/` 下创建目录结构
2. **优化 Skill**: 修改 `courses/<course>/skills/` 下的 CLAUDE.md 文件
3. **提交评测**: 将评测结果保存到 `courses/<course>/benchmark/results/`

## 相关链接

- [PKU OS 2025 Spring](https://pku-os.github.io/sp25/)
- [Pintos 文档](https://pkuflyingpig.gitbook.io/pintos/)
- [Tacos 文档](https://pku-tacos.pages.dev/)

## License

MIT License
