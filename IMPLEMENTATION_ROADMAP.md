# 完全控制前端 - 实现路线图

## 当前状态 vs 目标状态

### ✅ 已完成（80%）
- [x] CLI基础框架
- [x] Python包结构
- [x] WebSocket客户端框架
- [x] 基础命令（project, import, session）
- [x] JSON输出模式
- [x] REPL接口
- [x] 文档和测试

### ⏳ 需要实现（20%）

---

## Phase 1: 协议层实现（核心）

### 1.1 WebSocket协议分析器

**目标**: 完全理解GUI和后端的通信协议

**文件**: `cli_anything/msinsight/core/protocol_analyzer.py`

```python
"""WebSocket协议分析器"""

import json
import websocket
from typing import Dict, Any, List

class ProtocolAnalyzer:
    """分析GUI和后端的WebSocket通信"""

    def __init__(self, port: int = 9000):
        self.port = port
        self.captured_commands = []

    def capture_gui_session(self, duration_seconds: int = 60):
        """捕获GUI会话的所有命令"""
        # 启动代理服务器
        # GUI → Proxy → Backend
        # 记录所有命令

    def analyze_command_patterns(self) -> Dict[str, Any]:
        """分析命令模式"""
        # 按模块分组
        # 提取参数模式
        # 生成API文档

    def generate_api_reference(self) -> str:
        """生成API参考文档"""
```

**实现步骤**:
1. 创建WebSocket代理
2. 捕获GUI操作
3. 分析命令格式
4. 生成API文档

**工作量**: 2-3天

---

### 1.2 完整的WebSocket客户端

**目标**: 实现与后端的完整通信

**文件**: `cli_anything/msinsight/core/websocket_client.py`

```python
"""WebSocket客户端"""

import websocket
import json
from typing import Dict, Any, Optional

class MindStudioWebSocketClient:
    """MindStudio Insight WebSocket客户端"""

    def __init__(self, host: str = "127.0.0.1", port: int = 9000):
        self.host = host
        self.port = port
        self.ws = None
        self.msg_id = 0

    def connect(self):
        """连接到后端服务器"""
        pass

    def send_command(
        self,
        module: str,
        command: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """发送命令到后端"""
        self.msg_id += 1

        request = {
            "id": self.msg_id,
            "type": "request",
            "moduleName": module,
            "command": command,
            "params": params or {}
        }

        self.ws.send(json.dumps(request))
        response = json.loads(self.ws.recv())

        return response

    # 状态管理
    def subscribe_event(self, event_type: str, callback):
        """订阅事件"""
        pass

    def unsubscribe_event(self, event_type: str):
        """取消订阅"""
        pass
```

**实现步骤**:
1. 完善连接管理
2. 实现消息队列
3. 添加事件订阅
4. 错误处理

**工作量**: 1-2天

---

## Phase 2: 控制层实现

### 2.1 Timeline控制模块

**目标**: 完整的Timeline控制能力

**文件**: `cli_anything/msinsight/core/timeline_control.py`

```python
"""Timeline控制"""

from typing import List, Dict, Any, Optional

class TimelineController:
    """Timeline控制器"""

    def __init__(self, client):
        self.client = client

    # 缩放控制
    def zoom_to_time(self, start: float, end: float):
        """缩放到时间范围"""
        return self.client.send_command(
            "timeline",
            "zoomToRange",
            {"start": start, "end": end}
        )

    def zoom_to_event(self, event_id: str, padding: float = 500):
        """缩放到事件（带上下文）"""
        # 1. 获取事件详情
        event = self.get_event_details(event_id)
        # 2. 计算范围
        start = max(0, event["start_time"] - padding)
        end = event["end_time"] + padding
        # 3. 缩放
        return self.zoom_to_time(start, end)

    def zoom_in(self, factor: float = 2.0):
        """放大"""
        pass

    def zoom_out(self, factor: float = 2.0):
        """缩小"""
        pass

    def zoom_fit(self):
        """适应窗口"""
        pass

    # 泳道管理
    def set_swimlane_order(
        self,
        lanes: List[Dict[str, Any]]
    ):
        """设置泳道顺序（支持置顶）"""
        return self.client.send_command(
            "timeline",
            "setSwimlaneOrder",
            {"lanes": lanes}
        )

    def pin_swimlanes(self, lane_ids: List[str]):
        """置顶泳道"""
        lanes = [
            {"id": lid, "pinned": True}
            for lid in lane_ids
        ]
        return self.set_swimlane_order(lanes)

    def unpin_swimlanes(self, lane_ids: List[str]):
        """取消置顶"""
        pass

    def hide_swimlanes(self, lane_ids: List[str]):
        """隐藏泳道"""
        pass

    def show_swimlanes(self, lane_ids: List[str]):
        """显示泳道"""
        pass

    # 对比模式
    def enable_compare_mode(
        self,
        lane_ids: List[str],
        sync_zoom: bool = True,
        highlight_diff: bool = True
    ):
        """启用对比模式"""
        return self.client.send_command(
            "timeline",
            "enableCompareMode",
            {
                "lanes": lane_ids,
                "syncZoom": sync_zoom,
                "highlightDiff": highlight_diff
            }
        )

    def disable_compare_mode(self):
        """禁用对比模式"""
        pass

    # 事件操作
    def highlight_event(self, event_id: str):
        """高亮事件"""
        return self.client.send_command(
            "timeline",
            "highlight",
            {"eventId": event_id}
        )

    def select_events(self, event_ids: List[str]):
        """选择多个事件"""
        pass

    def clear_selection(self):
        """清除选择"""
        pass

    # 过滤
    def filter_events(
        self,
        event_type: Optional[str] = None,
        duration_min: Optional[float] = None,
        duration_max: Optional[float] = None,
        keyword: Optional[str] = None
    ):
        """过滤事件"""
        params = {}
        if event_type:
            params["type"] = event_type
        if duration_min is not None:
            params["durationMin"] = duration_min
        if duration_max is not None:
            params["durationMax"] = duration_max
        if keyword:
            params["keyword"] = keyword

        return self.client.send_command(
            "timeline",
            "filter",
            params
        )

    # 搜索
    def search_events(
        self,
        pattern: str,
        search_scope: str = "all"
    ):
        """搜索事件"""
        return self.client.send_command(
            "timeline",
            "search",
            {
                "pattern": pattern,
                "scope": search_scope
            }
        )

    # 导航
    def goto_time(self, time: float):
        """跳转到时间点"""
        pass

    def goto_event(self, event_id: str):
        """跳转到事件"""
        event = self.get_event_details(event_id)
        return self.zoom_to_event(event_id)

    def goto_next_event(self):
        """跳转到下一个事件"""
        pass

    def goto_previous_event(self):
        """跳转到上一个事件"""
        pass
```

**工作量**: 2-3天

---

### 2.2 数据分析模块

**目标**: 完整的数据查询能力

**文件**: `cli_anything/msinsight/core/data_query.py`

```python
"""数据查询"""

from typing import List, Dict, Any, Optional

class DataQuery:
    """数据查询接口"""

    def __init__(self, client):
        self.client = client

    # 算子查询
    def query_operators(
        self,
        filter_expr: Optional[str] = None,
        sort_by: str = "duration",
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """查询算子"""
        params = {"sort": sort_by}
        if filter_expr:
            params["filter"] = filter_expr
        if limit:
            params["limit"] = limit

        response = self.client.send_command(
            "operator",
            "query",
            params
        )

        return response.get("body", {}).get("operators", [])

    def get_operator_details(self, operator_id: str) -> Dict[str, Any]:
        """获取算子详情"""
        response = self.client.send_command(
            "operator",
            "getDetails",
            {"operatorId": operator_id}
        )
        return response.get("body", {})

    def get_operator_source(self, operator_id: str) -> str:
        """获取算子源码"""
        response = self.client.send_command(
            "operator",
            "getSource",
            {"operatorId": operator_id}
        )
        return response.get("body", {}).get("source", "")

    # 内存查询
    def query_memory(
        self,
        operation_type: Optional[str] = None,
        size_min: Optional[int] = None,
        size_max: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """查询内存操作"""
        params = {}
        if operation_type:
            params["operationType"] = operation_type
        if size_min is not None:
            params["sizeMin"] = size_min
        if size_max is not None:
            params["sizeMax"] = size_max

        response = self.client.send_command(
            "memory",
            "query",
            params
        )

        return response.get("body", {}).get("operations", [])

    def get_memory_summary(self) -> Dict[str, Any]:
        """获取内存摘要"""
        response = self.client.send_command(
            "memory",
            "getSummary",
            {}
        )
        return response.get("body", {})

    # 通信查询
    def query_communication(
        self,
        src_rank: Optional[int] = None,
        dst_rank: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """查询通信操作"""
        params = {}
        if src_rank is not None:
            params["srcRank"] = src_rank
        if dst_rank is not None:
            params["dstRank"] = dst_rank

        response = self.client.send_command(
            "communication",
            "query",
            params
        )

        return response.get("body", {}).get("operations", [])

    def get_communication_matrix(self) -> Dict[str, Any]:
        """获取通信矩阵"""
        response = self.client.send_command(
            "communication",
            "getMatrix",
            {}
        )
        return response.get("body", {})
```

**工作量**: 1-2天

---

## Phase 3: 自然语言层

### 3.1 意图识别器

**目标**: 理解自然语言命令

**文件**: `cli_anything/msinsight/core/nlp/intent_recognizer.py`

```python
"""自然语言意图识别"""

import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class Intent:
    """用户意图"""
    action: str  # 操作类型
    target: str  # 目标对象
    params: Dict[str, Any]  # 参数
    confidence: float  # 置信度

class IntentRecognizer:
    """意图识别器"""

    def __init__(self):
        self.patterns = self._load_patterns()

    def _load_patterns(self) -> List[Dict[str, Any]]:
        """加载意图模式"""
        return [
            # 定位类
            {
                "pattern": r"定位.*?(慢|慢算子|性能差|耗时)",
                "intent": {
                    "action": "locate",
                    "target": "slow_operator",
                }
            },
            {
                "pattern": r"定位.*?(通信|通信瓶颈|通信慢)",
                "intent": {
                    "action": "locate",
                    "target": "comm_bottleneck",
                }
            },
            {
                "pattern": r"定位.*?(内存|内存泄漏|内存问题)",
                "intent": {
                    "action": "locate",
                    "target": "memory_issue",
                }
            },

            # 对比类
            {
                "pattern": r"对比.*?rank\s*(\d+).*?(?:和|与).*?rank\s*(\d+)",
                "intent": {
                    "action": "compare",
                    "target": "ranks",
                    "params": {"ranks": [1, 2]}  # 从正则提取
                }
            },
            {
                "pattern": r"对比.*?GPU\s*(\d+).*?(?:和|与).*?GPU\s*(\d+)",
                "intent": {
                    "action": "compare",
                    "target": "gpus",
                }
            },

            # 置顶类
            {
                "pattern": r"置顶.*?rank\s*(\d+)",
                "intent": {
                    "action": "pin",
                    "target": "rank",
                }
            },
            {
                "pattern": r"置顶.*?(通信|内存|算子)",
                "intent": {
                    "action": "pin",
                    "target": "type",
                }
            },

            # 跳转类
            {
                "pattern": r"跳转到?\s*(\d+)\s*(ms|毫秒)",
                "intent": {
                    "action": "goto",
                    "target": "time",
                }
            },
            {
                "pattern": r"跳转到?.*?(开始|起始|起点)",
                "intent": {
                    "action": "goto",
                    "target": "start",
                }
            },
            {
                "pattern": r"跳转到?.*?(结束|终点|末尾)",
                "intent": {
                    "action": "goto",
                    "target": "end",
                }
            },

            # 查询类
            {
                "pattern": r"显示.*?(最慢|慢).*?(算子|op|operator)",
                "intent": {
                    "action": "query",
                    "target": "slow_operators",
                }
            },
            {
                "pattern": r"显示.*?(内存|memory).*?(摘要|概览)",
                "intent": {
                    "action": "query",
                    "target": "memory_summary",
                }
            },

            # 过滤类
            {
                "pattern": r"只显示.*?(\w+).*?(算子|事件)",
                "intent": {
                    "action": "filter",
                    "target": "event_type",
                }
            },
            {
                "pattern": r"隐藏.*?(\w+)",
                "intent": {
                    "action": "hide",
                    "target": "type",
                }
            },
        ]

    def recognize(self, text: str) -> Optional[Intent]:
        """识别用户意图"""
        text = text.lower().strip()

        for rule in self.patterns:
            match = re.search(rule["pattern"], text, re.IGNORECASE)
            if match:
                intent_data = rule["intent"].copy()

                # 提取参数
                params = self._extract_params(match, intent_data)

                return Intent(
                    action=intent_data["action"],
                    target=intent_data["target"],
                    params=params,
                    confidence=0.9  # 简单的置信度
                )

        return None

    def _extract_params(
        self,
        match,
        intent_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """从匹配中提取参数"""
        params = intent_data.get("params", {})

        # 根据不同意图提取不同参数
        if intent_data["action"] == "compare":
            if "ranks" in intent_data.get("target", ""):
                # 提取rank编号
                ranks = [int(g) for g in match.groups() if g.isdigit()]
                params["ranks"] = ranks

        elif intent_data["action"] == "goto":
            if intent_data["target"] == "time":
                # 提取时间值
                time_val = int(match.group(1))
                params["time"] = time_val

        elif intent_data["action"] == "pin":
            if intent_data["target"] == "rank":
                rank = int(match.group(1))
                params["rank"] = rank

        return params
```

**工作量**: 2-3天

---

### 3.2 命令执行器

**目标**: 将意图转换为实际命令

**文件**: `cli_anything/msinsight/core/nlp/command_executor.py`

```python
"""命令执行器"""

from typing import Dict, Any, Optional
from .intent_recognizer import Intent
from ..timeline_control import TimelineController
from ..data_query import DataQuery

class CommandExecutor:
    """命令执行器"""

    def __init__(
        self,
        timeline: TimelineController,
        query: DataQuery
    ):
        self.timeline = timeline
        self.query = query
        self._setup_handlers()

    def _setup_handlers(self):
        """设置意图处理器"""
        self.handlers = {
            ("locate", "slow_operator"): self._locate_slow_operator,
            ("locate", "comm_bottleneck"): self._locate_comm_bottleneck,
            ("locate", "memory_issue"): self._locate_memory_issue,
            ("compare", "ranks"): self._compare_ranks,
            ("compare", "gpus"): self._compare_gpus,
            ("pin", "rank"): self._pin_rank,
            ("pin", "type"): self._pin_type,
            ("goto", "time"): self._goto_time,
            ("goto", "start"): self._goto_start,
            ("goto", "end"): self._goto_end,
            ("query", "slow_operators"): self._query_slow_operators,
            ("query", "memory_summary"): self._query_memory_summary,
            ("filter", "event_type"): self._filter_event_type,
            ("hide", "type"): self._hide_type,
        }

    def execute(self, intent: Intent) -> Dict[str, Any]:
        """执行意图"""
        key = (intent.action, intent.target)
        handler = self.handlers.get(key)

        if handler:
            return handler(intent.params)
        else:
            return {
                "success": False,
                "error": f"未实现的意图: {intent.action} {intent.target}"
            }

    # 定位操作
    def _locate_slow_operator(
        self,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """定位慢算子"""
        # 1. 查询最慢的算子
        operators = self.query.query_operators(
            filter_expr="duration > 100",
            sort_by="duration",
            limit=1
        )

        if not operators:
            return {"success": False, "error": "未找到慢算子"}

        slowest = operators[0]

        # 2. 跳转到该算子
        self.timeline.zoom_to_event(slowest["id"], padding=500)

        # 3. 高亮显示
        self.timeline.highlight_event(slowest["id"])

        return {
            "success": True,
            "message": f"已定位到最慢算子: {slowest['name']} ({slowest['duration']}ms)",
            "operator": slowest
        }

    def _locate_comm_bottleneck(
        self,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """定位通信瓶颈"""
        # 1. 查询通信矩阵
        matrix = self.query.get_communication_matrix()

        # 2. 找出最慢的通信
        # ... 分析逻辑

        # 3. 跳转并高亮
        # ...

        return {
            "success": True,
            "message": "已定位到通信瓶颈"
        }

    def _locate_memory_issue(
        self,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """定位内存问题"""
        # 实现内存问题定位
        pass

    # 对比操作
    def _compare_ranks(
        self,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """对比ranks"""
        ranks = params.get("ranks", [0, 1])
        lane_ids = [f"rank_{r}" for r in ranks]

        # 1. 置顶泳道
        self.timeline.pin_swimlanes(lane_ids)

        # 2. 启用对比模式
        self.timeline.enable_compare_mode(lane_ids)

        return {
            "success": True,
            "message": f"已对比rank {ranks[0]}和rank {ranks[1]}，并置顶显示"
        }

    def _compare_gpus(
        self,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """对比GPUs"""
        # 实现GPU对比
        pass

    # 置顶操作
    def _pin_rank(
        self,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """置顶rank"""
        rank = params.get("rank", 0)
        lane_id = f"rank_{rank}"

        self.timeline.pin_swimlanes([lane_id])

        return {
            "success": True,
            "message": f"已置顶rank {rank}"
        }

    def _pin_type(
        self,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """置顶类型"""
        # 实现类型置顶
        pass

    # 跳转操作
    def _goto_time(
        self,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """跳转到时间"""
        time_ms = params.get("time", 0)

        # 设置时间窗口（前后各500ms）
        self.timeline.zoom_to_time(
            max(0, time_ms - 500),
            time_ms + 500
        )

        return {
            "success": True,
            "message": f"已跳转到 {time_ms}ms"
        }

    def _goto_start(
        self,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """跳转到开始"""
        self.timeline.zoom_to_time(0, 5000)
        return {"success": True, "message": "已跳转到开始"}

    def _goto_end(
        self,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """跳转到结束"""
        # 获取总时长，跳转到末尾
        pass

    # 查询操作
    def _query_slow_operators(
        self,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """查询慢算子"""
        operators = self.query.query_operators(
            sort_by="duration",
            limit=10
        )

        return {
            "success": True,
            "operators": operators,
            "message": f"找到{len(operators)}个慢算子"
        }

    def _query_memory_summary(
        self,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """查询内存摘要"""
        summary = self.query.get_memory_summary()

        return {
            "success": True,
            "summary": summary
        }

    # 过滤操作
    def _filter_event_type(
        self,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """过滤事件类型"""
        # 实现过滤
        pass

    def _hide_type(
        self,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """隐藏类型"""
        # 实现隐藏
        pass
```

**工作量**: 2-3天

---

### 3.3 自然语言接口

**目标**: 提供友好的自然语言入口

**文件**: `cli_anything/msinsight/core/nlp_interface.py`

```python
"""自然语言接口"""

from typing import Dict, Any, Optional
from .intent_recognizer import IntentRecognizer
from .command_executor import CommandExecutor
from ..websocket_client import MindStudioWebSocketClient
from ..timeline_control import TimelineController
from ..data_query import DataQuery

class NaturalLanguageInterface:
    """自然语言接口"""

    def __init__(self, port: int = 9000):
        # 初始化WebSocket客户端
        self.client = MindStudioWebSocketClient(port=port)
        self.client.connect()

        # 初始化控制器
        self.timeline = TimelineController(self.client)
        self.query = DataQuery(self.client)

        # 初始化NLP组件
        self.recognizer = IntentRecognizer()
        self.executor = CommandExecutor(self.timeline, self.query)

    def execute(self, text: str) -> Dict[str, Any]:
        """执行自然语言命令"""
        # 1. 识别意图
        intent = self.recognizer.recognize(text)

        if not intent:
            return {
                "success": False,
                "error": f"无法识别命令: {text}",
                "suggestions": [
                    "定位到最慢的算子",
                    "对比rank 0和rank 1",
                    "跳转到1500ms",
                    "显示内存摘要"
                ]
            }

        # 2. 执行命令
        result = self.executor.execute(intent)

        # 3. 返回结果
        return result

    def chat(self, text: str) -> str:
        """对话式接口（返回友好消息）"""
        result = self.execute(text)

        if result["success"]:
            return result["message"]
        else:
            return f"❌ {result['error']}"

    def interactive_session(self):
        """交互式会话"""
        print("🤖 MindStudio Insight 自然语言控制")
        print("输入命令（例如：'定位到最慢的算子'）")
        print("输入 'quit' 退出\n")

        while True:
            try:
                text = input(">>> ").strip()

                if text.lower() in ['quit', 'exit', 'q']:
                    print("再见！")
                    break

                if not text:
                    continue

                response = self.chat(text)
                print(response)
                print()

            except KeyboardInterrupt:
                print("\n再见！")
                break
            except Exception as e:
                print(f"❌ 错误: {e}\n")
```

**工作量**: 1天

---

## Phase 4: CLI集成

### 4.1 添加remote命令组

**文件**: 更新 `cli_anything/msinsight/msinsight_cli.py`

```python
@cli.group()
@click.option('--port', type=int, default=9000, help='Backend server port')
@click.pass_context
def remote(ctx, port):
    """Remote control MindStudio Insight GUI"""
    from cli_anything.msinsight.core.nlp_interface import NaturalLanguageInterface

    interface = NaturalLanguageInterface(port=port)
    ctx.obj['nlp_interface'] = interface

@remote.command()
@click.argument('command')
@click.pass_context
def exec(ctx, command):
    """Execute natural language command"""
    interface = ctx.obj['nlp_interface']
    result = interface.execute(command)

    if ctx.obj['json']:
        print_json(result)
    else:
        if result['success']:
            print_success(result['message'])
        else:
            print_error(result['error'])

@remote.command()
def chat():
    """Start interactive chat session"""
    interface = ctx.obj['nlp_interface']
    interface.interactive_session()
```

**工作量**: 1天

---

## Phase 5: 测试和文档

### 5.1 集成测试

**文件**: `cli_anything/msinsight/tests/test_nlp_control.py`

```python
"""自然语言控制测试"""

def test_locate_slow_operator():
    """测试定位慢算子"""
    pass

def test_compare_ranks():
    """测试对比ranks"""
    pass

def test_goto_time():
    """测试跳转时间"""
    pass
```

**工作量**: 1-2天

### 5.2 使用文档

**文件**: `NATURAL_LANGUAGE_CONTROL_GUIDE.md`

```markdown
# 自然语言控制指南

## 快速开始

### 启动交互式会话
\`\`\`bash
cli-anything-msinsight remote chat --port 9000
\`\`\`

### 支持的命令

#### 定位类
- "定位到最慢的算子"
- "定位到通信瓶颈"
- "定位到内存问题"

#### 对比类
- "对比rank 0和rank 1"
- "对比GPU 0和GPU 1"

#### 置顶类
- "置顶rank 0"
- "置顶通信泳道"

#### 跳转类
- "跳转到1500ms"
- "跳转到开始"
- "跳转到结束"

#### 查询类
- "显示最慢的算子"
- "显示内存摘要"
- "显示通信矩阵"

#### 过滤类
- "只显示MatMul算子"
- "隐藏通信事件"
\`\`\`
```

**工作量**: 1天

---

## 总工作量估算

| Phase | 模块 | 工作量 |
|-------|------|--------|
| **Phase 1** | 协议层 | 3-5天 |
| **Phase 2** | 控制层 | 3-5天 |
| **Phase 3** | 自然语言层 | 5-7天 |
| **Phase 4** | CLI集成 | 1天 |
| **Phase 5** | 测试文档 | 2-3天 |
| **总计** | | **14-21天** |

---

## MVP版本（5-7天）

如果想要快速验证，可以先实现MVP：

### Week 1:
1. **Day 1-2**: WebSocket协议分析 + 客户端实现
2. **Day 3-4**: Timeline控制（基础命令）
3. **Day 5**: 3-5个自然语言命令
4. **Day 6-7**: 测试和文档

### MVP功能:
- ✅ "定位到慢算子"
- ✅ "对比rank 0和rank 1"
- ✅ "跳转到时间点"
- ✅ "置顶rank"
- ✅ "显示摘要"

---

## 下一步行动

需要我帮你：

1. **开始协议分析**？（创建监控脚本）
2. **实现WebSocket客户端**？（基础通信）
3. **实现第一个控制命令**？（zoom_to_time）
4. **创建项目计划**？（详细任务分解）

选择一个，我们立即开始！🚀
