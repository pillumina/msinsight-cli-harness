# 自然语言控制 - 快速开始指南

## 🎉 已实现功能

Phase 1 (协议层) 和 Phase 2 (控制层) 的核心功能已经完成！

### ✅ 已完成模块

#### 1. **Protocol Layer** (协议层)
- ✅ `MindStudioWebSocketClient`: WebSocket 客户端
  - 自动启动后端服务器
  - 连接管理
  - 请求/响应机制

- ✅ `ProtocolAnalyzer`: 协议分析器
  - 消息记录
  - 命令模式提取
  - 协议文档生成

#### 2. **Control Layer** (控制层)
- ✅ `TimelineController`: Timeline 控制器
  - `zoom_to_time()`: 缩放到时间范围
  - `pin_swimlanes()`: 置顶泳道
  - `compare_ranks()`: 对比 rank
  - `filter_swimlanes()`: 过滤泳道
  - `go_to_operator()`: 跳转到算子
  - `export_timeline_image()`: 导出图像

- ✅ `DataQuery`: 数据查询
  - `get_top_n_operators()`: 查询最慢算子
  - `get_memory_summary()`: 内存统计
  - `get_communication_matrix()`: 通信矩阵
  - `get_bottleneck_analysis()`: 瓶颈分析
  - `get_memory_leaks()`: 内存泄漏检测

#### 3. **NLP Layer** (自然语言层)
- ✅ `IntentRecognizer`: 意图识别
  - 正则表达式模式匹配
  - 支持中英文命令
  - 参数提取

- ✅ `CommandExecutor`: 命令执行
  - 意图到操作的映射
  - 结构化结果返回

- ✅ `NaturalLanguageInterface`: 统一接口
  - 简单的 API
  - 交互模式
  - 命令帮助

## 🚀 快速开始

### 安装依赖

```bash
cd agent-harness
pip install websocket-client
```

### Python API 使用

```python
from cli_anything.msinsight.nlp_interface import NaturalLanguageInterface

# 创建接口
nlp = NaturalLanguageInterface()

# 执行命令
result = nlp.process("最慢的10个算子")

if result["success"]:
    print("执行成功！")
    for op in result["result"]["operators"]:
        print(f"{op['name']}: {op['duration_ms']} ms")
```

### 交互模式

```python
nlp = NaturalLanguageInterface()
nlp.interactive()

# 进入 REPL
msinsight> 最慢的5个算子
✓ 执行成功
1. MatMul_123: 45.23 ms
2. Conv2d_456: 32.10 ms
...

msinsight> 对比 rank 0 和 rank 1
✓ 执行成功

msinsight> quit
```

### 运行 Demo

```bash
# 基本命令演示
python cli_anything/msinsight/examples/demo_nlp_control.py

# 交互式演示
python cli_anything/msinsight/examples/demo_nlp_control.py --interactive
```

## 📝 支持的命令示例

### 中文命令
- `最慢的10个算子`
- `定位到 100ms 到 200ms`
- `对比 rank 0 和 rank 1`
- `置顶泳道：rank 0, rank 1`
- `内存使用情况`
- `性能瓶颈`
- `内存泄漏`
- `导出timeline到 timeline.png`

### 英文命令
- `top 10 operators`
- `zoom to 100ms to 200ms`
- `compare rank 0 and rank 1`
- `pin lanes: rank 0, rank 1`
- `memory summary`
- `bottleneck`

## 🔧 下一步：需要做什么

### Phase 3: 验证和调试（重要！）

当前实现**尚未连接到实际后端进行验证**。需要：

#### 1. 启动后端服务器
```bash
# 方法 A: 从已安装的 MindStudio Insight
# Windows: C:\Program Files\MindStudio Insight\bin\msinsight-server.exe
# macOS: /Applications/MindStudio Insight.app/Contents/MacOS/msinsight-server
# Linux: /opt/mindstudio-insight/bin/msinsight-server

# 方法 B: 从源码编译
cd server
python build/build.py build --release
./output/bin/msinsight-server --wsPort=9000
```

#### 2. 测试 WebSocket 连接
```python
from cli_anything.msinsight.protocol import MindStudioWebSocketClient

client = MindStudioWebSocketClient(port=9000)
response = client.send_command("timeline", "getSwimlaneList")
print(response)
```

#### 3. 捕获真实协议消息

**方法 A: 修改前端代码**
```typescript
// modules/framework/src/centralServer/websocket/connection.ts
// 在 send() 方法中添加日志
send(request: Request): void {
  console.log('[WS SEND]', JSON.stringify(request, null, 2));
  // ... existing code ...
}
```

**方法 B: 使用 ProtocolAnalyzer**
```python
from cli_anything.msinsight.protocol import (
    MindStudioWebSocketClient,
    ProtocolAnalyzer,
    MessageInterceptor
)

# 创建客户端和分析器
client = MindStudioWebSocketClient(port=9000)
analyzer = ProtocolAnalyzer(log_file="protocol.log")

# 包装客户端
interceptor = MessageInterceptor(client, analyzer)

# 现在手动操作 GUI，所有命令会被记录
# ... 在 GUI 中执行操作 ...

# 生成协议文档
analyzer.export_protocol_doc("protocol_doc.md")
```

#### 4. 验证命令格式

检查实际的命令格式是否与我们的实现匹配：

```python
# 我们假设的格式
{
  "moduleName": "timeline",
  "command": "zoomToRange",
  "params": {
    "startTime": 100,
    "endTime": 200,
    "unit": "ms"
  }
}

# 实际格式可能是（需要验证）
{
  "module": "timeline",  # 可能是 "module" 而不是 "moduleName"
  "cmd": "zoomToRange",  # 可能是 "cmd" 而不是 "command"
  "args": {...}          # 可能是 "args" 而不是 "params"
}
```

#### 5. 修正命令格式

根据捕获的真实协议，修改：

```python
# cli_anything/msinsight/protocol/websocket_client.py

@dataclass
class Request:
    id: int
    type: str = "request"
    module_name: str = ""   # 根据实际情况修改字段名
    command: str = ""       # 根据实际情况修改字段名
    params: Optional[Dict[str, Any]] = None
```

### Phase 4: 扩展功能

1. **添加更多命令**
   - 在 `IntentRecognizer` 中添加新模式
   - 在 `CommandExecutor` 中实现新执行器

2. **改进 NLP**
   - 使用 LLM 进行意图识别
   - 支持更复杂的查询

3. **集成到 CLI**
   - 添加 `cli-anything-msinsight nlp` 命令
   - 支持批处理模式

### Phase 5: 测试和文档

1. **单元测试**
   - 测试意图识别
   - 测试命令执行
   - Mock 后端响应

2. **集成测试**
   - 连接真实后端
   - 验证所有命令

3. **文档**
   - API 文档
   - 用户指南
   - 示例代码

## 📚 文件结构

```
cli_anything/msinsight/
├── protocol/                      # 协议层
│   ├── __init__.py
│   ├── websocket_client.py        # WebSocket 客户端 ✅
│   └── protocol_analyzer.py       # 协议分析器 ✅
├── control/                       # 控制层
│   ├── __init__.py
│   ├── timeline_controller.py     # Timeline 控制 ✅
│   └── data_query.py              # 数据查询 ✅
├── nlp/                           # 自然语言层
│   ├── __init__.py
│   ├── intent_recognizer.py       # 意图识别 ✅
│   └── command_executor.py        # 命令执行 ✅
├── examples/                      # 示例
│   ├── demo_nlp_control.py        # Demo 脚本 ✅
│   └── NLP_CONTROL_README.md      # 详细文档 ✅
└── nlp_interface.py               # 统一接口 ✅
```

## 🎯 总结

### 已完成
- ✅ 完整的架构设计
- ✅ WebSocket 客户端
- ✅ 协议分析器
- ✅ Timeline 控制器
- ✅ 数据查询接口
- ✅ 意图识别（基于正则）
- ✅ 命令执行器
- ✅ 自然语言接口
- ✅ Demo 脚本
- ✅ 详细文档

### 待验证
- ⏳ 命令格式与实际后端匹配
- ⏳ WebSocket 连接测试
- ⏳ 协议消息捕获
- ⏳ 真实环境测试

### 下一步行动

**优先级 1: 验证协议**
1. 启动后端服务器
2. 使用 ProtocolAnalyzer 捕获真实消息
3. 对比并修正命令格式

**优先级 2: 功能扩展**
1. 添加更多命令模式
2. 改进错误处理
3. 集成到主 CLI

**优先级 3: 测试和文档**
1. 编写测试用例
2. 完善文档
3. 添加更多示例

## 🆘 遇到问题？

### 问题 1: 后端服务器未找到
```
ERROR: MindStudio Insight backend server not found.
```

**解决方案**: 安装 MindStudio Insight 或从源码编译后端

### 问题 2: WebSocket 连接失败
```
ERROR: Failed to connect to server at ws://127.0.0.1:9000
```

**解决方案**: 确保后端服务器正在运行

### 问题 3: 命令格式不匹配
```
ERROR: Unknown error from backend
```

**解决方案**: 使用 ProtocolAnalyzer 捕获真实协议，修正命令格式

## 📖 参考资料

- [IMPLEMENTATION_ROADMAP.md](../../IMPLEMENTATION_ROADMAP.md): 完整实现路线图
- [NLP_CONTROL_README.md](./NLP_CONTROL_README.md): 详细技术文档
- [MSINSIGHT.md](../../MSINSIGHT.md): CLI 使用文档

---

**准备好验证协议了吗？** 开始 Phase 3！🚀
