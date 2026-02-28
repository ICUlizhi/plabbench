#!/bin/bash
# Plabbench 环境初始化脚本

set -e

echo "====================================="
echo "Plabbench Setup Script"
echo "====================================="

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

echo "[1/4] Python version: $(python3 --version)"

# 检查 Git
if ! command -v git &> /dev/null; then
    echo "Error: Git is required but not installed."
    exit 1
fi

echo "[2/4] Git version: $(git --version)"

# 创建必要的目录
echo "[3/4] Creating directories..."
mkdir -p courses/pku-os/labs/{lab0-booting,lab1-threads,lab2-userprog,lab3a-vm,lab3b-mmap}/{pintos,tacos}
mkdir -p courses/pku-os/benchmark/results

echo "[4/4] Directories created."

echo ""
echo "====================================="
echo "Setup complete!"
echo "====================================="
echo ""
echo "Next steps:"
echo "1. Clone lab repositories:"
echo "   cd courses/pku-os/labs/lab0-booting/pintos"
echo "   git clone https://github.com/pku-os/Pintos.git source"
echo ""
echo "2. Setup development environment:"
echo "   See docs/tutorials/pku-os/pintos-setup.md"
echo ""
echo "3. Run benchmark:"
echo "   python courses/pku-os/benchmark/runner.py --lab lab1-threads --track pintos"
echo ""
