# 独立部署指南 - 让其他用户使用 CLI

## 问题说明

当前CLI依赖源码目录中的后端服务器。其他用户需要：
1. 安装Python CLI包
2. 安装MindStudio Insight后端服务器（独立）

## 解决方案

### 方案1: 后端服务器作为系统包（推荐）

#### 步骤1: 打包后端服务器

```bash
# 在源码目录创建后端服务器发布包
cd /path/to/msinsight/server

# 构建后端
python build/build.py build --release

# 创建发布包结构
mkdir -p msinsight-server-linux-x86_64/bin
cp output/linux-x86_64/bin/msinsight-server msinsight-server-linux-x86_64/bin/

# 创建安装脚本
cat > msinsight-server-linux-x86_64/install.sh << 'EOF'
#!/bin/bash
# 安装MindStudio Insight后端服务器

INSTALL_DIR="/usr/local/bin"
echo "安装msinsight-server到 $INSTALL_DIR ..."

sudo cp bin/msinsight-server "$INSTALL_DIR/"
sudo chmod +x "$INSTALL_DIR/msinsight-server"

echo "✓ 安装完成"
echo "验证: msinsight-server --help"
EOF

chmod +x msinsight-server-linux-x86_64/install.sh

# 打包
tar -czf msinsight-server-linux-x86_64.tar.gz msinsight-server-linux-x86_64/

echo "发布包已创建: msinsight-server-linux-x86_64.tar.gz"
```

#### 步骤2: 修改CLI的README

更新 `cli_anything/msinsight/README.md`:

```markdown
## 安装

### 1. 安装后端服务器（必需）

**系统要求**: MindStudio Insight后端服务器

**安装方式A: 使用发布包**
```bash
# 下载发布包
wget https://your-repo/msinsight-server-linux-x86_64.tar.gz
tar -xzf msinsight-server-linux-x86_64.tar.gz
cd msinsight-server-linux-x86_64
sudo ./install.sh
```

**安装方式B: 从源码构建**
```bash
git clone https://github.com/your-org/msinsight.git
cd msinsight/server
python build/build.py build --release
sudo cp output/linux-x86_64/bin/msinsight-server /usr/local/bin/
```

**验证安装**:
```bash
msinsight-server --help
```

### 2. 安装CLI

```bash
pip install cli-anything-msinsight
```

### 3. 验证

```bash
cli-anything-msinsight --version
```
```

---

### 方案2: 发布到PyPI（最简单）

#### 当前项目结构已满足要求

```
agent-harness/
├── setup.py                    # PyPI配置
└── cli_anything/               # 命名空间包（PEP 420）
    └── msinsight/
        ├── msinsight_cli.py    # CLI入口
        ├── core/
        ├── utils/
        └── README.md
```

#### 发布到PyPI

```bash
# 1. 构建发布包
cd agent-harness
python setup.py sdist bdist_wheel

# 2. 上传到PyPI
pip install twine
twine upload dist/*

# 3. 用户安装（发布后）
pip install cli-anything-msinsight
```

#### 用户安装说明

```markdown
## 安装

```bash
# 1. 安装CLI
pip install cli-anything-msinsight

# 2. 安装后端服务器（必需）
# 下载并安装msinsight-server
wget https://your-repo/msinsight-server-linux-x86_64.tar.gz
tar -xzf msinsight-server-linux-x86_64.tar.gz
cd msinsight-server-linux-x86_64
sudo ./install.sh

# 3. 验证
cli-anything-msinsight --version
```
```

---

### 方案3: 完整发布包（包含后端）

创建一个包含CLI和后端的完整发布包。

#### 步骤1: 创建完整发布包

```bash
#!/bin/bash
# create_full_package.sh

VERSION="1.0.0"
PACKAGE_NAME="msinsight-cli-full-${VERSION}"

# 创建包目录
mkdir -p "$PACKAGE_NAME"

# 1. 构建后端服务器
cd /path/to/msinsight/server
python build/build.py build --release
cd -

# 2. 复制后端服务器
cp -r /path/to/msinsight/server/output/linux-x86_64/bin "$PACKAGE_NAME/msinsight-server"

# 3. 复制Python CLI源码
cp -r agent-harness/cli_anything "$PACKAGE_NAME/"
cp agent-harness/setup.py "$PACKAGE_NAME/"

# 4. 创建安装脚本
cat > "$PACKAGE_NAME/install.sh" << 'EOF'
#!/bin/bash
set -e

echo "安装 MindStudio Insight CLI 完整包..."

# 安装后端服务器
echo "1. 安装后端服务器..."
sudo cp msinsight-server/msinsight-server /usr/local/bin/
sudo chmod +x /usr/local/bin/msinsight-server

# 安装Python CLI
echo "2. 安装Python CLI..."
pip install -e .

echo ""
echo "✓ 安装完成！"
echo ""
echo "验证安装:"
echo "  msinsight-server --help"
echo "  cli-anything-msinsight --version"
EOF

chmod +x "$PACKAGE_NAME/install.sh"

# 5. 创建README
cat > "$PACKAGE_NAME/README.md" << 'EOF'
# MindStudio Insight CLI 完整包

## 安装

```bash
./install.sh
```

## 使用

```bash
cli-anything-msinsight --help
```
EOF

# 6. 打包
tar -czf "$PACKAGE_NAME.tar.gz" "$PACKAGE_NAME"

echo "完整发布包已创建: $PACKAGE_NAME.tar.gz"
```

---

## 推荐方案对比

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **方案1: 系统包** | 清晰分离，灵活 | 需要用户安装两个包 | 生产环境、团队使用 |
| **方案2: PyPI** | 标准化，易安装 | 需要单独安装后端 | 开源项目、公开分发 |
| **方案3: 完整包** | 一键安装 | 包体积大，更新麻烦 | 离线环境、内部部署 |

---

## 我的推荐

### 对于内部团队使用：
**方案1（系统包）** - 最清晰
1. 发布后端服务器为独立的系统包
2. 发布CLI到内部PyPI或直接给wheel文件
3. 用户分两步安装

### 对于开源项目：
**方案2（PyPI + 后端下载）** - 最标准
1. CLI发布到PyPI
2. 后端服务器作为单独的下载项
3. README中说明依赖关系

### 对于离线部署：
**方案3（完整包）** - 最方便
1. 打包所有内容
2. 一键安装
3. 适合内网环境

---

## 立即可用的临时方案

**当前状态下的使用方法**：

```bash
# 用户A（有源码访问权限）
cd /path/to/msinsight/agent-harness
pip install -e .
cli-anything-msinsight --version  # 可以工作

# 用户B（无源码）- 需要以下步骤：
# 1. 获取源码
git clone <repo>
cd msinsight

# 2. 构建后端
cd server
python build/build.py build --release

# 3. 安装CLI
cd ../agent-harness
pip install -e .

# 4. 使用
cli-anything-msinsight --version
```

---

## 下一步建议

1. **短期**（立即可用）：
   - 在README中说明需要先构建后端
   - 提供构建脚本

2. **中期**（团队使用）：
   - 实施方案1（系统包）
   - 发布后端为独立包

3. **长期**（公开发布）：
   - 实施方案2（PyPI发布）
   - 提供预编译的后端下载

需要我帮你实施哪个方案？我可以：
1. 修改代码支持独立部署
2. 创建发布包
3. 编写安装文档
4. 设置CI/CD自动发布
