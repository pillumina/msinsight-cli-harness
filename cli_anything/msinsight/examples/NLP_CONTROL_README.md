# 自然语言控制 - MindStudio Insight

## 概述

这个模块实现了对 MindStudio Insight 前端的**自然语言控制**，允许用户通过自然语言命令（如"定位到慢算子"、"对比 rank 0 和 rank 1"）来操作前端界面。

## 架构

```
自然语言控制架构
├── protocol/              # 协议层
│   ├── websocket_client.py    # WebSocket 客户端
│   └── protocol_analyzer.py   # 协议分析器
├── control/               # 控制层
│   ├── timeline_controller.py # Timeline 控制器
│   └── data_query.py          # 数据查询
├── nlp/                   # 自然语言层
│   ├── intent_recognizer.py   # 意图识别
│   └── command_executor.py    # 命令执行
└── nlp_interface.py       # 统一接口
```

### 1. 协议层 (Protocol Layer)

**WebSocketClient**: 与后端服务器通信
- 自动启动后端服务器
- 管理连接生命周期
- 发送请求并接收响应

**ProtocolAnalyzer**: 分析 WebSocket 消息
- 记录所有消息
- 提取命令模式
- 生成协议文档

### 2. 控制层 (Control Layer)

**TimelineController**: Timeline 操作
- `zoom_to_time()`: 缩放到时间范围
- `pin_swimlanes()`: 置顶泳道
- `compare_ranks()`: 对比 rank
- `filter_swimlanes()`: 过滤泳道
- `go_to_operator()`: 跳转到算子

**DataQuery**: 数据查询
- `get_top_n_operators()`: 查询最慢算子
- `get_memory_summary()`: 内存统计
- `get_communication_matrix()`: 通信矩阵
- `get_bottleneck_analysis()`: 瓶颈分析

### 3. 自然语言层 (NLP Layer)

**IntentRecognizer**: 意图识别
- 基于正则表达式模式匹配
- 支持中英文命令
- 提取参数（时间范围、算子名称等）

**CommandExecutor**: 命令执行
- 将意图映射到具体操作
- 调用控制层 API
- 返回结构化结果

## 使用示例

### Python API

```python
from cli_anything.msinsight.nlp_interface import NaturalLanguageInterface

# 创建接口
nlp = NaturalLanguageInterface()

# 处理自然语言命令
result = nlp.process("最慢的10个算子")

if result["success"]:
    print("执行成功！")
    for op in result["result"]["operators"]:
        print(f"{op['name']}: {op['duration_ms']} ms")
else:
    print(f"执行失败: {result['error']}")
```

### 交互模式

```python
# 启动交互式会话
nlp.interactive()

# 进入 REPL
msinsight> 最慢的5个算子
✓ 执行成功
1. MatMul_123: 45.23 ms
2. Conv2d_456: 32.10 ms
3. Softmax_789: 28.50 ms
4. BatchNorm_234: 22.30 ms
5. ReLU_567: 18.90 ms

msinsight> 定位到 100ms 到 200ms
✓ 执行成功

msinsight> 对比 rank 0 和 rank 1
✓ 执行成功
对比对象: ['rank 0', 'rank 1']

msinsight> quit
再见！
```

### CLI 命令

```bash
# 启动自然语言交互模式
cli-anything-msinsight nlp interactive

# 执行单个自然语言命令
cli-anything-msinsight nlp execute "最慢的10个算子"

# 查看支持的命令
cli-anything-msinsight nlp help
```

## 支持的命令

### 导航命令

| 命令 | 描述 |
|------|------|
| `定位到 100ms 到 200ms` | 缩放到时间范围 |
| `定位到算子：MatMul_123` | 跳转到指定算子 |
| `置顶泳道：rank 0, rank 1` | 置顶泳道 |
| `对比 rank 0 和 rank 1` | 对比不同 rank |
| `只显示类型：MatMul` | 过滤泳道类型 |

### 查询命令

| 命令 | 描述 |
|------|------|
| `最慢的10个算子` | 查询最慢算子 |
| `慢算子` | 查询慢算子（默认 10 个） |
| `算子 MatMul_123 的详情` | 查询算子详情 |
| `内存使用情况` | 内存统计 |
| `通信矩阵` | 通信矩阵 |

### 分析命令

| 命令 | 描述 |
|------|------|
| `性能瓶颈` | 瓶颈分析 |
| `内存泄漏` | 内存泄漏检测 |

### 导出命令

| 命令 | 描述 |
|------|------|
| `导出timeline到 timeline.png` | 导出 timeline 图像 |

## 扩展命令

要添加新的自然语言命令：

### 1. 在 IntentRecognizer 中添加模式

```python
# cli_anything/msinsight/nlp/intent_recognizer.py

class IntentType(Enum):
    MY_NEW_COMMAND = "my_new_command"  # 添加新意图类型

class IntentRecognizer:
    def _build_patterns(self):
        return [
            # ... existing patterns ...
            {
                "pattern": r"我的新命令\s+(.+)",
                "intent_type": IntentType.MY_NEW_COMMAND,
                "extractor": lambda m: {"param": m.group(1)}
            }
        ]
```

### 2. 在 CommandExecutor 中添加执行器

```python
# cli_anything/msinsight/nlp/command_executor.py

class CommandExecutor:
    def execute(self, intent: Intent):
        executor_map = {
            # ... existing executors ...
            IntentType.MY_NEW_COMMAND: self._execute_my_new_command,
        }

    def _execute_my_new_command(self, params: Dict[str, Any]):
        # 实现命令逻辑
        return {"success": True, "result": "命令执行成功"}
```

### 3. 测试

```python
from cli_anything.msinsight.nlp_interface import NaturalLanguageInterface

nlp = NaturalLanguageInterface()
result = nlp.process("我的新命令 参数值")
print(result)
```

## 协议分析

要分析 GUI 和后端之间的通信协议：

```python
from cli_anything.msinsight.protocol import (
    MindStudioWebSocketClient,
    ProtocolAnalyzer,
    MessageInterceptor
)

# 创建客户端和分析器
client = MindStudioWebSocketClient()
analyzer = ProtocolAnalyzer(log_file="protocol.log")

# 使用拦截器包装客户端
interceptor = MessageInterceptor(client, analyzer)

# 正常使用客户端，所有消息会被自动记录
response = interceptor.send_command("timeline", "zoomToRange", {...})

# 生成协议文档
analyzer.export_protocol_doc("protocol_doc.md")

# 获取命令摘要
summary = analyzer.get_command_summary()
print(f"捕获 {summary['total_messages']} 条消息")
print(f"发现 {summary['unique_commands']} 个命令")
```

## 运行 Demo

```bash
# 运行基本命令演示
python cli_anything/msinsight/examples/demo_nlp_control.py

# 运行交互式演示
python cli_anything/msinsight/examples/demo_nlp_control.py --interactive
```

## 技术细节

### WebSocket 协议格式

**请求格式**:
```json
{
  "id": 1,
  "type": "request",
  "moduleName": "timeline",
  "command": "zoomToRange",
  "params": {
    "startTime": 100,
    "endTime": 200,
    "unit": "ms"
  }
}
```

**响应格式**:
```json
{
  "id": 1,
  "type": "response",
  "success": true,
  "data": {
    "zoomed": true
  }
}
```

### 意图识别流程

1. **输入**: 自然语言文本
2. **模式匹配**: 使用正则表达式匹配命令模式
3. **参数提取**: 从匹配中提取参数
4. **意图创建**: 创建 `Intent` 对象
5. **执行**: 调用 `CommandExecutor` 执行

### 支持的时间单位

- `ms`: 毫秒
- `us`: 微秒
- `ns`: 纳秒

## 局限性

### 当前不支持的操作（需要 GUI 交互）

- ❌ 拖拽操作
- ❌ 实时颜色编码
- ❌ 鼠标悬停提示
- ❌ 动态可视化效果

### 推荐使用模式

**混合模式**: CLI 控制 + GUI 可视化

1. 使用 CLI 进行数据查询、分析、导航
2. 使用 GUI 查看可视化结果
3. 两者结合，效率最高

## 未来改进

### Phase 2: 增强 NLP 能力

- 使用大语言模型（LLM）进行意图识别
- 支持更复杂的自然语言查询
- 支持上下文理解

### Phase 3: 更多控制命令

- 完整实现所有后端 API
- 支持批量操作
- 支持宏命令

### Phase 4: 智能建议

- 根据数据特征自动推荐分析方向
- 异常检测和告警
- 性能优化建议

## 参考

- [IMPLEMENTATION_ROADMAP.md](../../IMPLEMENTATION_ROADMAP.md): 完整实现路线图
- [MSINSIGHT.md](../../MSINSIGHT.md): CLI 使用文档
- [protocol_doc.md](../../protocol_doc.md): 协议文档（通过 ProtocolAnalyzer 生成）

## 贡献

欢迎贡献新的命令模式和功能！

1. 在 `intent_recognizer.py` 中添加新模式
2. 在 `command_executor.py` 中实现执行逻辑
3. 添加测试用例
4. 更新文档

## 许可证

Mulan PSL v2
