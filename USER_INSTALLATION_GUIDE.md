# 用户安装指南 - MindStudio Insight CLI

## 📋 前提条件

**只需两样东西**：
1. ✅ MindStudio Insight GUI应用（已安装）
2. ✅ Python 3.10+

**无需源码！** ✅

---

## 🚀 快速安装（3步）

### 步骤1: 安装 MindStudio Insight GUI

如果你还没有安装MindStudio Insight：

**Windows:**
```bash
# 1. 下载安装包
https://gitcode.com/Ascend/msinsight/releases

# 2. 双击 .exe 文件安装
# 例如: MindStudio-Insight-1.0.0-win-x86_64.exe

# 3. 按照安装向导完成安装
# 默认路径: C:\Program Files\MindStudio Insight\
```

**macOS:**
```bash
# 1. 下载 .dmg 文件
https://gitcode.com/Ascend/msinsight/releases

# 2. 打开 .dmg，拖动到 Applications
# 例如: MindStudio-Insight-1.0.0-macos.dmg

# 3. 安装位置
# /Applications/MindStudio Insight.app/
```

**Linux:**
```bash
# 1. 下载 .tar.gz 包
wget https://gitcode.com/Ascend/msinsight/releases/download/v1.0.0/MindStudio-Insight-1.0.0-linux-x86_64.tar.gz

# 2. 解压
tar -xzf MindStudio-Insight-1.0.0-linux-x86_64.tar.gz

# 3. 安装（可选）
sudo mv MindStudio-Insight-1.0.0 /opt/mindstudio-insight

# 或添加到PATH
export PATH=$PATH:$(pwd)/MindStudio-Insight-1.0.0/bin
```

### 步骤2: 安装CLI

```bash
# 使用pip安装CLI（从PyPI）
pip install cli-anything-msinsight

# 或从本地安装（如果你有wheel文件）
pip install cli_anything_msinsight-1.0.0-py3-none-any.whl
```

### 步骤3: 验证安装

```bash
# 检查CLI版本
cli-anything-msinsight --version

# 查看帮助
cli-anything-msinsight --help

# 测试命令
cli-anything-msinsight project new -o test.json
```

**输出示例**:
```
cli-anything-msinsight version 1.0.0
```

---

## ✅ 验证后端服务器

CLI会自动查找已安装的MindStudio Insight后端服务器。

**验证后端可用**:
```bash
# 直接运行后端（检查是否在PATH中）
msinsight-server --help

# 或查看安装位置
# Windows: C:\Program Files\MindStudio Insight\bin\msinsight-server.exe
# macOS: /Applications/MindStudio Insight.app/Contents/MacOS/msinsight-server
# Linux: /opt/mindstudio-insight/bin/msinsight-server
```

---

## 🎯 完整示例

### 场景: 验证性能数据

```bash
# 1. 安装MindStudio Insight GUI（如果未安装）
# ... 从release页面下载并安装 ...

# 2. 安装CLI
pip install cli-anything-msinsight

# 3. 验证你的性能数据
cli-anything-msinsight import validate /path/to/profiler_output

# 输出:
# ✓ Valid profiling data: /path/to/profiler_output
# Total files: 12
#   - json: 4 files
#   - db: 3 files
#   - bin: 5 files

# 4. 创建分析项目
cli-anything-msinsight project new --name "我的分析" -o analysis.json

# 5. 使用项目
cli-anything-msinsight --project analysis.json project info
```

---

## 🔧 故障排除

### 问题1: CLI找不到后端服务器

**错误信息**:
```
ERROR: MindStudio Insight backend server not found.
```

**解决方案**:

**方法A: 验证MindStudio Insight已安装**
```bash
# Windows
dir "C:\Program Files\MindStudio Insight\bin\msinsight-server.exe"

# macOS
ls -l "/Applications/MindStudio Insight.app/Contents/MacOS/msinsight-server"

# Linux
ls -l /opt/mindstudio-insight/bin/msinsight-server
```

**方法B: 添加到PATH（如果不在标准位置）**

```bash
# Windows (PowerShell)
$env:PATH += ";C:\Path\To\MindStudio Insight\bin"

# macOS/Linux
export PATH=$PATH:/path/to/mindstudio-insight/bin
```

**方法C: 设置环境变量**

```bash
# 设置后端服务器路径
export MSINSIGHT_SERVER_PATH=/path/to/msinsight-server
```

### 问题2: Python版本不兼容

**错误信息**:
```
ERROR: Package 'cli-anything-msinsight' requires Python >=3.10
```

**解决方案**:
```bash
# 检查Python版本
python --version

# 如果版本过低，升级Python
# 或使用conda
conda create -n msinsight python=3.11
conda activate msinsight
pip install cli-anything-msinsight
```

### 问题3: CLI命令未找到

**错误信息**:
```
'cli-anything-msinsight' is not recognized as an internal or external command
```

**解决方案**:

```bash
# 验证pip安装位置
pip show cli-anything-msinsight

# 检查Scripts目录是否在PATH中
# Windows: C:\Users\<user>\AppData\Local\Programs\Python\Python311\Scripts\
# Linux/macOS: ~/.local/bin/

# 重新安装
pip install --force-reinstall cli-anything-msinsight

# 或使用python -m
python -m cli_anything.msinsight.msinsight_cli --help
```

---

## 📚 下一步

安装完成后，你可以：

1. **查看使用场景**:
   ```bash
   cat /path/to/USAGE_SCENARIOS.md
   ```

2. **阅读完整文档**:
   ```bash
   cli-anything-msinsight --help
   ```

3. **尝试交互模式**:
   ```bash
   cli-anything-msinsight
   msinsight> help
   ```

4. **运行示例**:
   ```bash
   # 创建项目
   cli-anything-msinsight project new -o my_first_project.json

   # 验证数据
   cli-anything-msinsight import validate /path/to/profiling/data

   # 查看项目信息
   cli-anything-msinsight --project my_first_project.json project info
   ```

---

## 🆘 获取帮助

- **命令行帮助**: `cli-anything-msinsight --help`
- **交互式帮助**: `cli-anything-msinsight` → `help`
- **文档**: 查看 `MSINSIGHT.md` 和 `README.md`
- **问题反馈**: https://gitcode.com/Ascend/msinsight/issues

---

## 💡 常见问题

### Q1: 我需要下载源码吗？
**A**: 不需要！只需要：
1. 安装MindStudio Insight GUI（从release下载）
2. 安装CLI（`pip install cli-anything-msinsight`）

### Q2: 后端服务器在哪里？
**A**: CLI会自动查找已安装的MindStudio Insight，位置：
- Windows: `C:\Program Files\MindStudio Insight\bin\`
- macOS: `/Applications/MindStudio Insight.app/Contents/MacOS/`
- Linux: `/opt/mindstudio-insight/bin/` 或 PATH

### Q3: 可以只用CLI不用GUI吗？
**A**: 可以！CLI是独立的命令行工具，但需要后端服务器（包含在GUI安装包中）。

### Q4: 如何更新？
**A**:
```bash
# 更新CLI
pip install --upgrade cli-anything-msinsight

# 更新MindStudio Insight
# 下载最新版本并重新安装
```

### Q5: 可以在服务器上使用吗（无GUI）？
**A**: 可以！只需安装MindStudio Insight（后端服务器），CLI就可以使用。不需要启动GUI。

---

## ✅ 安装检查清单

安装完成后，验证以下内容：

```bash
# 1. CLI已安装
cli-anything-msinsight --version
# ✓ 输出: cli-anything-msinsight version 1.0.0

# 2. 后端服务器可用（可选检查）
msinsight-server --version
# ✓ 输出: msinsight-server version 1.0.0

# 3. 基本功能正常
cli-anything-msinsight project new -o test.json
# ✓ 输出: ✓ Created project: test.json

# 4. 清理测试
rm test.json
```

全部通过？恭喜，安装成功！🎉

---

## 🎯 总结

**安装只需3步**：
1. ⬇️ 下载安装 MindStudio Insight GUI
2. 📦 `pip install cli-anything-msinsight`
3. ✅ `cli-anything-msinsight --version`

**无需源码！** 开始使用CLI进行性能分析吧！🚀
