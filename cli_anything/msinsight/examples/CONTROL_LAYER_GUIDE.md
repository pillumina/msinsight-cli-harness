# MindStudio Insight 控制层使用指南

## 架构概览

```
用户自然语言命令
      ↓
   AI Agent (通过 Skill)
      ↓
   CLI 命令 / 控制层 API
      ↓
   Backend WebSocket API
      ↓
   MindStudio Insight 前端
```

**核心理念**:
- ✅ **AI Agent 提供自然语言理解**
- ✅ **CLI 和控制层提供精确的编程接口**
- ✅ **Skill 连接 AI Agent 和 CLI**

## 三层架构

### 1. Protocol Layer (协议层)
**用途**: 与 MindStudio Insight 后端通信

**关键组件**:
- `MindStudioWebSocketClient`: WebSocket 客户端
- `ProtocolAnalyzer`: 协议分析器（用于开发调试）

**示例**:
```python
from cli_anything.msinsight.protocol import MindStudioWebSocketClient

client = MindStudioWebSocketClient(port=9000)
response = client.send_command(
    module="timeline",
    command="zoomToRange",
    params={"startTime": 100, "endTime": 200, "unit": "ms"}
)
```

### 2. Control Layer (控制层)
**用途**: 提供高级控制 API

**关键组件**:
- `TimelineController`: Timeline 视图控制
- `DataQuery`: 数据查询接口

**示例**:
```python
from cli_anything.msinsight.control import TimelineController, DataQuery
from cli_anything.msinsight.protocol import MindStudioWebSocketClient

client = MindStudioWebSocketClient()
timeline = TimelineController(client)
query = DataQuery(client)

# Timeline 控制
timeline.zoom_to_time(100, 200, unit="ms")
timeline.pin_swimlanes(["rank 0", "rank 1"])
timeline.compare_ranks(["rank 0", "rank 1"])

# 数据查询
top_ops = query.get_top_n_operators(n=10, metric="duration")
memory = query.get_memory_summary()
```

### 3. CLI Layer (命令行层)
**用途**: 提供命令行接口给用户和 AI Agent

**示例**:
```bash
# 用户直接使用
cli-anything-msinsight timeline zoom --start 100 --end 200 --unit ms
cli-anything-msinsight operator top --n 10 --metric duration

# AI Agent 通过 Skill 调用
# (AI 理解用户意图，生成相应的 CLI 命令)
```

## 使用场景

### 场景 1: 用户使用 CLI
```bash
# 1. 创建项目
cli-anything-msinsight project new -o analysis.json

# 2. 加载数据
cli-anything-msinsight --project analysis.json import load-profiling /data/profiler_output

# 3. 查询最慢算子
cli-anything-msinsight --project analysis.json operator top --n 10

# 4. 控制 Timeline
cli-anything-msinsight --project analysis.json timeline zoom --start 100 --end 200

# 5. 对比 rank
cli-anything-msinsight --project analysis.json timeline compare --ranks "rank 0,rank 1"
```

### 场景 2: AI Agent 使用 (通过 Skill)

**用户**: "帮我定位到最慢的算子"

**AI Agent** (通过 SKILL.md 理解):
1. 首先查询最慢算子:
   ```bash
   cli-anything-msinsight --project analysis.json operator top --n 1 --json
   ```
2. 获取算子信息 (例如: MatMul_123, 开始时间: 150ms)
3. 控制 Timeline 跳转:
   ```bash
   cli-anything-msinsight --project analysis.json timeline goto-operator --id MatMul_123
   ```

**用户**: "对比 rank 0 和 rank 1 的性能"

**AI Agent**:
```bash
cli-anything-msinsight --project analysis.json timeline compare --ranks "rank 0,rank 1"
```

### 场景 3: Python 脚本使用控制层

```python
#!/usr/bin/env python3
"""自动化性能分析脚本"""

from cli_anything.msinsight.protocol import MindStudioWebSocketClient
from cli_anything.msinsight.control import TimelineController, DataQuery

# 连接到后端
client = MindStudioWebSocketClient(port=9000)

# 创建控制器
timeline = TimelineController(client)
query = DataQuery(client)

# 1. 查询最慢的 10 个算子
print("=== Top 10 Slowest Operators ===")
top_ops = query.get_top_n_operators(n=10, metric="duration")
for i, op in enumerate(top_ops["operators"], 1):
    print(f"{i}. {op['name']}: {op['duration_ms']:.2f} ms")

# 2. 定位到最慢算子
if top_ops["operators"]:
    slowest = top_ops["operators"][0]
    print(f"\n=== Navigating to {slowest['name']} ===")
    timeline.go_to_operator(slowest["id"], zoom_to_fit=True)

# 3. 查询内存使用
print("\n=== Memory Summary ===")
memory = query.get_memory_summary()
print(f"Peak Memory: {memory['peak_memory_mb']:.2f} MB")
print(f"Memory Leaks: {memory['leak_count']}")

# 4. 检测性能瓶颈
print("\n=== Bottleneck Analysis ===")
bottleneck = query.get_bottleneck_analysis()
print(f"Main Bottleneck: {bottleneck['type']}")
print(f"Recommendation: {bottleneck['recommendation']}")

# 断开连接
client.disconnect()
```

## 控制层 API 参考

### TimelineController

#### 导航控制
- `zoom_to_time(start, end, unit="ms")`: 缩放到时间范围
- `pan_left(amount=None)`: 左移
- `pan_right(amount=None)`: 右移
- `reset_zoom()`: 重置缩放
- `go_to_operator(operator_id, zoom_to_fit=True)`: 跳转到算子

#### 泳道控制
- `pin_swimlanes(lane_ids, unpin_others=True)`: 置顶泳道
- `unpin_all_swimlanes()`: 取消所有置顶
- `highlight_swimlane(lane_id, highlight=True)`: 高亮泳道
- `filter_swimlanes(filter_type, pattern=None, show_only=True)`: 过滤泳道
- `clear_filters()`: 清除过滤

#### 对比分析
- `compare_ranks(rank_ids, align_mode="time")`: 对比多个 rank

#### 选择和导出
- `select_time_range(start, end, unit="ms")`: 选择时间范围
- `clear_selection()`: 清除选择
- `export_timeline_image(output_path, format="png", width=None, height=None)`: 导出图像

#### 查询
- `get_visible_range()`: 获取可见范围
- `get_swimlane_list()`: 获取泳道列表

### DataQuery

#### 算子查询
- `get_operators(filters=None, sort_by="duration", sort_order="desc", limit=None)`: 获取算子列表
- `get_top_n_operators(n=10, metric="duration")`: 获取最慢的 N 个算子
- `get_operator_by_id(operator_id)`: 根据 ID 获取算子详情
- `get_operator_statistics()`: 算子统计

#### 内存查询
- `get_memory_summary()`: 内存摘要
- `get_memory_timeline(start_time=None, end_time=None)`: 内存时间线
- `get_memory_blocks(filters=None)`: 内存块
- `get_memory_leaks()`: 内存泄漏检测

#### 通信查询
- `get_communication_matrix(rank_ids=None)`: 通信矩阵
- `get_communication_events(rank_id=None, event_type=None)`: 通信事件
- `get_communication_hotspots(n=10)`: 通信热点

#### 分析查询
- `get_performance_summary()`: 性能摘要
- `get_bottleneck_analysis()`: 瓶颈分析
- `get_optimization_suggestions()`: 优化建议

#### 源码查询
- `get_source_location(operator_id)`: 源码位置
- `get_call_stack(operator_id)`: 调用栈

## 协议分析工具

用于开发调试，捕获真实的 WebSocket 消息：

```python
from cli_anything.msinsight.protocol import (
    MindStudioWebSocketClient,
    ProtocolAnalyzer,
    MessageInterceptor
)

# 创建客户端和分析器
client = MindStudioWebSocketClient(port=9000)
analyzer = ProtocolAnalyzer(log_file="protocol.log")

# 包装客户端，自动记录消息
interceptor = MessageInterceptor(client, analyzer)

# 正常使用（所有消息会被记录）
interceptor.send_command("timeline", "zoomToRange", {...})

# 生成协议文档
analyzer.export_protocol_doc("protocol_doc.md")

# 查看统计
summary = analyzer.get_command_summary()
print(f"捕获 {summary['total_messages']} 条消息")
print(f"发现 {summary['unique_commands']} 个命令")
```

## 开发和调试

### 1. 验证协议格式

**步骤**:
1. 启动 MindStudio Insight 后端
2. 使用 ProtocolAnalyzer 捕获真实消息
3. 对比实际格式与我们的实现
4. 修正 `Request`/`Response` 数据结构

**示例**:
```python
from cli_anything.msinsight.protocol import ProtocolAnalyzer

# 加载之前捕获的日志
analyzer = ProtocolAnalyzer()
analyzer.load_logs("protocol.log")

# 查看命令模式
summary = analyzer.get_command_summary()
for cmd_key, pattern in summary["commands"].items():
    print(f"\n{cmd_key}:")
    print(f"  调用次数: {pattern['call_count']}")
    print(f"  参数示例: {pattern['param_examples'][:2]}")
```

### 2. 测试连接

```python
from cli_anything.msinsight.protocol import MindStudioWebSocketClient

try:
    client = MindStudioWebSocketClient(port=9000, auto_start=False)
    client.connect()

    # 测试简单命令
    response = client.send_command("timeline", "getSwimlaneList")
    print("连接成功！")
    print(f"泳道数量: {len(response.data.get('lanes', []))}")

    client.disconnect()
except Exception as e:
    print(f"连接失败: {e}")
```

## 下一步工作

### Phase 3: 验证和完善
1. ✅ 启动后端服务器
2. ✅ 使用 ProtocolAnalyzer 捕获真实消息
3. ✅ 验证命令格式
4. ✅ 修正 API 调用

### Phase 4: CLI 集成
1. 在 CLI 中添加 timeline 和 operator 命令
2. 添加 --json 输出支持
3. 完善错误处理

### Phase 5: Skill 完善
1. 更新 SKILL.md，添加控制命令说明
2. 添加使用示例
3. 添加最佳实践

## 示例脚本

查看更多示例:
- `examples/basic_usage.py`: 基本使用
- `examples/automation_script.py`: 自动化脚本
- `examples/protocol_capture.py`: 协议捕获

## 总结

**架构优势**:
- ✅ **清晰的分层**: 协议层 → 控制层 → CLI
- ✅ **AI Agent 友好**: 通过 Skill 使用 CLI
- ✅ **可编程**: 控制层可被 Python 脚本调用
- ✅ **可调试**: 协议分析器帮助开发

**使用方式**:
- **用户**: 使用 CLI 命令
- **AI Agent**: 通过 Skill 理解意图，调用 CLI
- **脚本**: 直接使用控制层 API

---

**准备好验证协议了吗？** 开始 Phase 3！🚀
