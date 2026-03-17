# MindStudio Insight CLI - 使用场景示例

## 📖 目录

1. [快速入门](#快速入门)
2. [日常分析场景](#日常分析场景)
3. [批量处理场景](#批量处理场景)
4. [CI/CD 集成场景](#cicd-集成场景)
5. [AI Agent 自动化场景](#ai-agent-自动化场景)
6. [高级应用场景](#高级应用场景)

---

## 快速入门

### 场景 1: 第一次使用 - 验证数据

**目标**: 快速验证你的性能数据是否有效

```bash
# 假设你的性能数据在这个目录
PROFILING_DIR="/path/to/your/profiler_output"

# 验证数据
cli-anything-msinsight import validate "$PROFILING_DIR"

# 输出示例：
# ✓ Valid profiling data: /path/to/your/profiler_output
# Total files: 12
#   - json: 4 files
#   - db: 3 files
#   - bin: 5 files
```

### 场景 2: 创建第一个分析项目

**目标**: 创建项目文件来管理你的分析

```bash
# 创建项目
cli-anything-msinsight project new \
    --name "ResNet50训练分析" \
    -o resnet50_analysis.json

# 查看项目信息
cli-anything-msinsight --project resnet50_analysis.json project info

# 输出示例：
# Project: ResNet50训练分析
# Path: resnet50_analysis.json
# Version: 1.0.0
# Created: 2026-03-16T12:00:00Z
```

---

## 日常分析场景

### 场景 3: 每日训练监控

**背景**: 每天训练结束后，自动验证性能数据

```bash
#!/bin/bash
# daily_check.sh - 每日训练数据检查脚本

TODAY=$(date +%Y%m%d)
PROFILING_DIR="/data/training/runs/$TODAY"
REPORT_DIR="/data/reports/$TODAY"

# 创建项目
cli-anything-msinsight project new \
    --name "每日训练检查-$TODAY" \
    -o "$REPORT_DIR/daily_check.json"

# 验证数据
cli-anything-msinsight --project "$REPORT_DIR/daily_check.json" \
    import validate "$PROFILING_DIR" > "$REPORT_DIR/validation.txt"

# 检查结果
if grep -q "Valid profiling data" "$REPORT_DIR/validation.txt"; then
    echo "✓ $TODAY 训练数据验证通过"
else
    echo "✗ $TODAY 训练数据验证失败"
    # 发送告警邮件或消息
fi
```

### 场景 4: 交互式探索分析

**背景**: 需要交互式地探索性能数据

```bash
# 启动交互模式
cli-anything-msinsight

# 在 REPL 中：
msinsight> project new -o explore.json
✓ Created project: explore.json

msinsight(Explore*)> import validate /data/profiler_run1
✓ Valid profiling data: /data/profiler_run1
  - json: 3 files
  - db: 2 files
  - bin: 8 files

msinsight(Explore*)> project save
✓ Saved project to: explore.json

msinsight(Explore)> session status
Session Status:
  Project: Explore
  Modified: false
  History: 3 commands

msinsight(Explore)> help
# 查看可用命令...

msinsight(Explore)> exit
Goodbye!
```

### 场景 5: 模型优化迭代

**背景**: 在模型优化过程中，对比多个版本的性能

```bash
# 创建对比分析项目
cli-anything-msinsight project new --name "模型优化对比" -o comparison.json

# 验证原始版本
cli-anything-msinsight --project comparison.json \
    import validate /data/model_v1.0

# 验证优化版本
cli-anything-msinsight --project comparison.json \
    import validate /data/model_v1.1

# 验证进一步优化版本
cli-anything-msinsight --project comparison.json \
    import validate /data/model_v1.2

# 保存对比分析
cli-anything-msinsight --project comparison.json project save

# 查看项目信息（包含所有数据源）
cli-anything-msinsight --project comparison.json project info
```

---

## 批量处理场景

### 场景 6: 批量分析多个训练Run

**背景**: 一次分析过去一周的所有训练run

```bash
#!/bin/bash
# batch_analyze.sh - 批量分析脚本

ANALYSIS_DIR="/data/analysis/$(date +%Y%m%d)"
mkdir -p "$ANALYSIS_DIR"

# 分析过去7天的训练数据
for i in {0..6}; do
    DATE=$(date -d "$i days ago" +%Y%m%d)
    PROFILING_DIR="/data/training/runs/$DATE"

    if [ -d "$PROFILING_DIR" ]; then
        echo "分析 $DATE 的数据..."

        # 创建项目
        cli-anything-msinsight project new \
            --name "训练分析-$DATE" \
            -o "$ANALYSIS_DIR/analysis_$DATE.json"

        # 验证数据
        cli-anything-msinsight --json \
            --project "$ANALYSIS_DIR/analysis_$DATE.json" \
            import validate "$PROFILING_DIR" \
            > "$ANALYSIS_DIR/validation_$DATE.json"

        echo "✓ 完成 $DATE"
    else
        echo "⚠ 跳过 $DATE (无数据)"
    fi
done

echo "批量分析完成！结果保存在: $ANALYSIS_DIR"
```

### 场景 7: 不同模型对比

**背景**: 对比不同模型的性能特征

```bash
#!/bin/bash
# model_comparison.sh - 模型对比分析

MODELS=("resnet50" "resnet101" "vgg16" "vgg19")
OUTPUT_DIR="/data/model_comparison"

mkdir -p "$OUTPUT_DIR"

for MODEL in "${MODELS[@]}"; do
    echo "分析模型: $MODEL"

    PROFILING_DIR="/data/models/$MODEL/profiler_output"
    PROJECT_FILE="$OUTPUT_DIR/${MODEL}_analysis.json"

    # 创建项目
    cli-anything-msinsight project new \
        --name "$MODEL 性能分析" \
        -o "$PROJECT_FILE"

    # 验证数据
    cli-anything-msinsight --json \
        --project "$PROJECT_FILE" \
        import validate "$PROFILING_DIR" \
        > "$OUTPUT_DIR/${MODEL}_validation.json"

    echo "✓ $MODEL 完成"
done

# 生成汇总报告
echo "模型对比分析完成！"
echo "结果保存在: $OUTPUT_DIR"
ls -lh "$OUTPUT_DIR"/*.json
```

---

## CI/CD 集成场景

### 场景 8: GitHub Actions 自动验证

**背景**: 在CI流水线中自动验证性能数据

```yaml
# .github/workflows/performance_check.yml
name: Performance Data Validation

on:
  push:
    paths:
      - 'profiler_output/**'

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install CLI
      run: |
        pip install cli-anything-msinsight

    - name: Validate profiling data
      run: |
        # 创建项目
        cli-anything-msinsight project new \
            --name "CI验证-${{ github.sha }}" \
            -o ci_validation.json

        # 验证数据
        cli-anything-msinsight --json \
            --project ci_validation.json \
            import validate ./profiler_output \
            > validation_result.json

        # 检查结果
        if [ $(jq -r '.status' validation_result.json) == "success" ]; then
          echo "✓ 性能数据验证通过"
          exit 0
        else
          echo "✗ 性能数据验证失败"
          cat validation_result.json
          exit 1
        fi

    - name: Upload results
      uses: actions/upload-artifact@v3
      with:
        name: validation-results
        path: |
          ci_validation.json
          validation_result.json
```

### 场景 9: Jenkins Pipeline 集成

**背景**: 在Jenkins中集成性能分析

```groovy
// Jenkinsfile
pipeline {
    agent any

    stages {
        stage('Validate Performance Data') {
            steps {
                script {
                    sh '''
                        # 安装CLI
                        pip install cli-anything-msinsight

                        # 创建项目
                        cli-anything-msinsight project new \
                            --name "Jenkins-Build-${BUILD_NUMBER}" \
                            -o "build_${BUILD_NUMBER}.json"

                        # 验证数据
                        cli-anything-msinsight --json \
                            --project "build_${BUILD_NUMBER}.json" \
                            import validate ./profiler_output \
                            > "validation_${BUILD_NUMBER}.json"
                    '''

                    // 读取并检查结果
                    def result = readJSON file: "validation_${BUILD_NUMBER}.json"

                    if (result.status != "success") {
                        error("性能数据验证失败: ${result}")
                    }

                    echo "✓ 性能数据验证通过"
                }
            }
        }

        stage('Archive Results') {
            steps {
                archiveArtifacts artifacts: '*.json', fingerprint: true
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
```

---

## AI Agent 自动化场景

### 场景 10: AI Agent 自动分析

**背景**: 让AI agent自动分析性能数据并生成报告

```python
#!/usr/bin/env python3
"""
AI Agent 自动化性能分析
"""
import subprocess
import json
import sys
from pathlib import Path

class PerformanceAnalyzer:
    """性能分析Agent"""

    def __init__(self, profiling_dir):
        self.profiling_dir = Path(profiling_dir)
        self.project_file = None

    def create_project(self, name="AI Analysis"):
        """创建分析项目"""
        result = subprocess.run([
            "cli-anything-msinsight", "--json",
            "project", "new",
            "--name", name,
            "-o", "ai_analysis.json"
        ], capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"创建项目失败: {result.stderr}")

        data = json.loads(result.stdout)
        self.project_file = data["project"]["path"]
        print(f"✓ 创建项目: {self.project_file}")
        return data

    def validate_data(self):
        """验证性能数据"""
        result = subprocess.run([
            "cli-anything-msinsight", "--json",
            "--project", self.project_file,
            "import", "validate",
            str(self.profiling_dir)
        ], capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"验证失败: {result.stderr}")

        data = json.loads(result.stdout)
        print(f"✓ 验证数据: {data['result']['total_files']} 个文件")

        # 输出详细信息
        for ftype, count in data['result']['files'].items():
            if count > 0:
                print(f"  - {ftype}: {count} files")

        return data

    def get_session_status(self):
        """获取会话状态"""
        result = subprocess.run([
            "cli-anything-msinsight", "--json",
            "--project", self.project_file,
            "session", "status"
        ], capture_output=True, text=True)

        data = json.loads(result.stdout)
        return data

    def generate_report(self):
        """生成分析报告"""
        print("\n" + "="*60)
        print("性能分析报告")
        print("="*60)

        # 获取会话状态
        status = self.get_session_status()
        print(f"项目: {status['session']['project']}")
        print(f"状态: {status['status']}")

        print("\n" + "="*60)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python ai_analyzer.py <profiling_dir>")
        sys.exit(1)

    profiling_dir = sys.argv[1]

    # 创建分析器
    analyzer = PerformanceAnalyzer(profiling_dir)

    try:
        # 执行分析流程
        analyzer.create_project("AI Automated Analysis")
        analyzer.validate_data()
        analyzer.generate_report()

        print("\n✓ AI自动化分析完成！")

    except Exception as e:
        print(f"\n✗ 错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**使用示例**:
```bash
# 运行AI agent分析
python ai_analyzer.py /path/to/profiler_output

# 输出示例：
# ✓ 创建项目: ai_analysis.json
# ✓ 验证数据: 15 个文件
#   - json: 4 files
#   - db: 3 files
#   - bin: 8 files
#
# ============================================================
# 性能分析报告
# ============================================================
# 项目: AI Automated Analysis
# 状态: success
#
# ============================================================
# ✓ AI自动化分析完成！
```

### 场景 11: 批量Agent分析

**背景**: Agent自动分析多个训练run并生成对比报告

```python
#!/usr/bin/env python3
"""
批量Agent分析 - 自动对比多个训练run
"""
import subprocess
import json
from pathlib import Path
from datetime import datetime

class BatchAnalyzer:
    """批量分析Agent"""

    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.results = []

    def analyze_run(self, run_dir):
        """分析单个run"""
        run_name = run_dir.name

        # 创建项目
        result = subprocess.run([
            "cli-anything-msinsight", "--json",
            "project", "new",
            "--name", f"Run-{run_name}",
            "-o", str(run_dir / "analysis.json")
        ], capture_output=True, text=True)

        if result.returncode != 0:
            return None

        project_data = json.loads(result.stdout)

        # 验证数据
        profiling_dir = run_dir / "profiler_output"
        result = subprocess.run([
            "cli-anything-msinsight", "--json",
            "--project", project_data["project"]["path"],
            "import", "validate",
            str(profiling_dir)
        ], capture_output=True, text=True)

        validation = json.loads(result.stdout)

        return {
            "run": run_name,
            "project": project_data,
            "validation": validation
        }

    def analyze_all(self):
        """分析所有run"""
        print("开始批量分析...")

        for run_dir in sorted(self.base_dir.iterdir()):
            if run_dir.is_dir():
                print(f"\n分析: {run_dir.name}")
                result = self.analyze_run(run_dir)

                if result:
                    self.results.append(result)
                    print(f"  ✓ 完成 - {result['validation']['result']['total_files']} 文件")
                else:
                    print(f"  ✗ 失败")

    def generate_summary(self):
        """生成汇总报告"""
        print("\n" + "="*70)
        print("批量分析汇总报告")
        print("="*70)
        print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总run数: {len(self.results)}")
        print("\n详细结果:")

        for i, result in enumerate(self.results, 1):
            print(f"\n{i}. {result['run']}")
            print(f"   文件数: {result['validation']['result']['total_files']}")
            print(f"   状态: {result['validation']['status']}")

        print("\n" + "="*70)

def main():
    """主函数"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python batch_analyzer.py <base_dir>")
        sys.exit(1)

    base_dir = sys.argv[1]

    analyzer = BatchAnalyzer(base_dir)
    analyzer.analyze_all()
    analyzer.generate_summary()

if __name__ == "__main__":
    main()
```

---

## 高级应用场景

### 场景 12: 实时监控仪表板

**背景**: 创建实时监控性能数据的仪表板

```bash
#!/bin/bash
# monitor_dashboard.sh - 实时监控脚本

WATCH_DIR="/data/training/current"
LOG_FILE="/var/log/msinsight_monitor.log"

echo "启动性能监控..."

while true; do
    # 检测新数据
    if [ -d "$WATCH_DIR" ]; then
        # 快速验证
        RESULT=$(cli-anything-msinsight --json import validate "$WATCH_DIR")

        # 提取关键信息
        STATUS=$(echo "$RESULT" | jq -r '.status')
        FILES=$(echo "$RESULT" | jq -r '.result.total_files')

        # 记录日志
        echo "[$(date)] Status: $STATUS, Files: $FILES" >> "$LOG_FILE"

        # 更新仪表板文件
        echo "$RESULT" > /var/www/dashboard/current_status.json

        # 检查异常
        if [ "$STATUS" != "success" ]; then
            echo "[$(date)] WARNING: Validation failed" >> "$LOG_FILE"
            # 发送告警...
        fi
    fi

    sleep 60  # 每分钟检查一次
done
```

### 场景 13: 数据质量检查

**背景**: 自动检查性能数据质量

```python
#!/usr/bin/env python3
"""
数据质量检查工具
"""
import subprocess
import json
import sys
from pathlib import Path

def check_data_quality(profiling_dir, min_files=5, required_types=['json', 'db']):
    """
    检查数据质量

    Args:
        profiling_dir: 性能数据目录
        min_files: 最小文件数
        required_types: 必需的文件类型
    """
    result = subprocess.run([
        "cli-anything-msinsight", "--json",
        "import", "validate",
        str(profiling_dir)
    ], capture_output=True, text=True)

    if result.returncode != 0:
        return {
            "valid": False,
            "error": "Validation command failed"
        }

    data = json.loads(result.stdout)

    # 检查基本验证
    if data['status'] != 'success':
        return {
            "valid": False,
            "error": "Validation failed"
        }

    # 检查文件数量
    total_files = data['result']['total_files']
    if total_files < min_files:
        return {
            "valid": False,
            "error": f"Insufficient files: {total_files} < {min_files}"
        }

    # 检查必需的文件类型
    files = data['result']['files']
    missing_types = []
    for req_type in required_types:
        if files.get(req_type, 0) == 0:
            missing_types.append(req_type)

    if missing_types:
        return {
            "valid": False,
            "error": f"Missing required file types: {missing_types}"
        }

    return {
        "valid": True,
        "total_files": total_files,
        "file_types": files
    }

def main():
    if len(sys.argv) < 2:
        print("用法: python quality_check.py <profiling_dir>")
        sys.exit(1)

    profiling_dir = sys.argv[1]

    print("检查数据质量...")
    result = check_data_quality(profiling_dir)

    if result['valid']:
        print(f"✓ 数据质量检查通过")
        print(f"  总文件数: {result['total_files']}")
        print(f"  文件类型: {result['file_types']}")
    else:
        print(f"✗ 数据质量检查失败")
        print(f"  错误: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 场景 14: 性能回归检测

**背景**: 检测性能回归

```bash
#!/bin/bash
# regression_check.sh - 性能回归检测

BASELINE_DIR="/data/baseline/profiler_output"
CURRENT_DIR="/data/current/profiler_output"

echo "性能回归检测..."

# 验证基线数据
echo "1. 验证基线数据..."
BASELINE=$(cli-anything-msinsight --json import validate "$BASELINE_DIR")
BASELINE_FILES=$(echo "$BASELINE" | jq -r '.result.total_files')

# 验证当前数据
echo "2. 验证当前数据..."
CURRENT=$(cli-anything-msinsight --json import validate "$CURRENT_DIR")
CURRENT_FILES=$(echo "$CURRENT" | jq -r '.result.total_files')

echo "3. 对比分析..."
echo "基线文件数: $BASELINE_FILES"
echo "当前文件数: $CURRENT_FILES"

# 简单的文件数对比
if [ "$CURRENT_FILES" -lt "$BASELINE_FILES" ]; then
    echo "⚠ 警告: 文件数减少，可能存在性能回归"
else
    echo "✓ 文件数正常"
fi

echo "回归检测完成！"
```

---

## 总结

这些场景展示了 MindStudio Insight CLI 的多种用途：

1. **日常分析**: 快速验证、交互式探索、模型对比
2. **批量处理**: 多run分析、模型对比、自动化报告
3. **CI/CD集成**: GitHub Actions、Jenkins等自动化流程
4. **AI Agent**: 完全自动化的性能分析
5. **高级应用**: 实时监控、质量检查、回归检测

### 最佳实践

1. **使用JSON输出**: 便于程序解析和自动化
2. **项目文件管理**: 使用项目文件保存分析状态
3. **错误处理**: 检查返回码和stderr
4. **批量化**: 编写脚本处理多个分析任务
5. **集成化**: 将CLI集成到现有工作流中

### 获取更多帮助

```bash
# 查看所有命令
cli-anything-msinsight --help

# 查看特定命令帮助
cli-anything-msinsight project --help
cli-anything-msinsight import --help

# 交互式帮助
cli-anything-msinsight
msinsight> help
```

需要更多特定场景的示例吗？我可以根据你的具体需求提供定制化的使用方案！
