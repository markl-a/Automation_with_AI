## 工作流自動化集成指南
# Workflow Automation Integration Guide

本指南詳細介紹如何使用 AI Automation Framework 集成各種工作流自動化平台。

---

## 📋 目錄

- [支持的平台](#支持的平台)
- [快速開始](#快速開始)
- [平台集成詳解](#平台集成詳解)
  - [n8n](#n8n-集成)
  - [Make (Integromat)](#make-integromat-集成)
  - [Zapier](#zapier-集成)
  - [Apache Airflow](#apache-airflow-集成)
- [統一接口使用](#統一接口使用)
- [高級用法](#高級用法)
- [最佳實踐](#最佳實踐)
- [故障排除](#故障排除)

---

## 支持的平台

| 平台 | 類型 | 開源 | 自託管 | 支持功能 |
|------|------|------|--------|---------|
| **n8n** | 工作流自動化 | ✅ | ✅ | Webhook、API、工作流管理 |
| **Make** | 工作流自動化 | ❌ | ❌ | Webhook、場景管理 |
| **Zapier** | 工作流自動化 | ❌ | ❌ | Webhook、Zap 觸發 |
| **Apache Airflow** | 數據管道 | ✅ | ✅ | DAG 管理、執行監控 |

---

## 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 設置環境變量

創建 `.env` 文件：

```bash
# n8n
N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=your_n8n_api_key

# Make
MAKE_API_TOKEN=your_make_api_token
MAKE_ORGANIZATION_ID=your_org_id
MAKE_TEAM_ID=your_team_id

# Zapier
ZAPIER_WEBHOOK_URL=https://hooks.zapier.com/hooks/catch/xxx/yyy/
ZAPIER_API_KEY=your_zapier_api_key

# Airflow
AIRFLOW_BASE_URL=http://localhost:8080
AIRFLOW_USERNAME=admin
AIRFLOW_PASSWORD=admin
```

### 3. 基本使用

```python
from ai_automation_framework.integrations.workflow_automation_unified import (
    UnifiedWorkflowManager,
    WorkflowPlatform
)

# 創建管理器
manager = UnifiedWorkflowManager()

# 註冊 n8n
manager.register_n8n(
    base_url="http://localhost:5678",
    api_key="your_api_key"
)

# 觸發工作流
result = manager.trigger_workflow(
    platform=WorkflowPlatform.N8N,
    workflow_id="workflow_123",
    data={"key": "value"}
)

print(result)
```

---

## 平台集成詳解

### n8n 集成

#### 基本功能

```python
from ai_automation_framework.integrations.n8n_integration_enhanced import N8NEnhanced

# 初始化
n8n = N8NEnhanced(
    base_url="http://localhost:5678",
    api_key="your_api_key"
)

# 1. 工作流管理
workflows = n8n.get_workflows(active=True)
workflow = n8n.get_workflow("workflow_id")

# 2. 執行工作流
result = n8n.execute_workflow(
    workflow_id="workflow_123",
    data={"input": "data"}
)

# 3. 監控執行
execution = n8n.get_execution(result['data']['id'])
print(f"狀態: {execution['data']['status']}")

# 4. Webhook 觸發
webhook_result = n8n.trigger_webhook(
    webhook_id="webhook_path",
    data={"event": "new_order"}
)
```

#### 創建 AI 工作流模板

```python
# 創建 AI 處理工作流
template = n8n.create_ai_workflow_template(
    name="AI Content Generator",
    webhook_path="ai-content",
    ai_prompt="You are a helpful content writer..."
)

# 創建工作流
result = n8n.create_workflow(
    name=template['name'],
    nodes=template['nodes'],
    connections=template['connections'],
    active=True
)
```

#### 批量執行

```python
# 批量執行工作流
data_list = [
    {"customer": "John", "order": 1},
    {"customer": "Jane", "order": 2},
    {"customer": "Bob", "order": 3}
]

results = n8n.bulk_execute("workflow_id", data_list)

for result in results:
    print(f"執行: {result.get('success')}")
```

#### 等待執行完成

```python
# 觸發工作流
execution = n8n.execute_workflow("workflow_id", {"data": "test"})
execution_id = execution['data']['id']

# 等待完成（最多 5 分鐘）
final_result = n8n.wait_for_execution(
    execution_id=execution_id,
    max_wait=300,
    poll_interval=2
)

if final_result.get('success'):
    print(f"執行狀態: {final_result['data']['status']}")
```

---

### Make (Integromat) 集成

#### 基本功能

```python
from ai_automation_framework.integrations.make_integration import MakeIntegration

# 初始化
make = MakeIntegration(
    api_token="your_token",
    organization_id="org_id",
    team_id="team_id"
)

# 1. 場景管理
scenarios = make.get_scenarios()
scenario = make.get_scenario("scenario_id")

# 2. 執行場景
result = make.run_scenario(
    scenario_id="scenario_123",
    data={"input": "data"}
)

# 3. 激活/停用場景
make.activate_scenario("scenario_id")
make.deactivate_scenario("scenario_id")
```

#### Webhook 觸發

```python
# 方式 1: 直接 URL
result = make.trigger_webhook(
    webhook_url="https://hook.eu1.make.com/xxx",
    data={"event": "order_created"}
)

# 方式 2: 使用 webhook key
result = make.trigger_custom_webhook(
    webhook_key="your_webhook_key",
    data={"event": "order_created"}
)
```

#### 數據存儲

```python
# 獲取數據存儲
datastores = make.get_data_stores()

# 讀取記錄
records = make.get_data_store_records(
    datastore_id="ds_123",
    limit=100
)

# 添加記錄
result = make.add_data_store_record(
    datastore_id="ds_123",
    data={"name": "John", "email": "john@example.com"}
)
```

---

### Zapier 集成

#### 基本功能

```python
from ai_automation_framework.integrations.zapier_integration_enhanced import ZapierEnhanced

# 初始化
zapier = ZapierEnhanced(
    default_webhook_url="https://hooks.zapier.com/hooks/catch/xxx/yyy/",
    api_key="your_api_key"
)

# 1. 觸發 Webhook
result = zapier.trigger_webhook({
    "event": "new_user",
    "name": "John Doe",
    "email": "john@example.com"
})

# 2. 批量觸發
results = zapier.batch_trigger(
    data_list=[
        {"user": "John"},
        {"user": "Jane"},
        {"user": "Bob"}
    ],
    delay_between=0.5  # 500ms 延遲
)
```

#### 預定義動作

```python
# 發送郵件
zapier.send_email(
    to="recipient@example.com",
    subject="Test Email",
    body="This is a test email from AI Framework",
    cc=["cc@example.com"],
    attachments=["https://example.com/file.pdf"]
)

# 發送 Slack 消息
zapier.send_slack_message(
    channel="#general",
    message="New order received!",
    username="Order Bot",
    icon_emoji=":package:"
)

# 創建 Google Sheets 行
zapier.create_google_sheet_row(
    spreadsheet_id="sheet_123",
    row_data={
        "Name": "John Doe",
        "Email": "john@example.com",
        "Date": "2025-01-XX"
    }
)

# 創建任務
zapier.create_task(
    task_name="Follow up with customer",
    description="Contact John about the order",
    due_date="2025-02-01",
    priority="high",
    assignee="sales@example.com"
)

# 發送短信
zapier.send_sms(
    to="+1234567890",
    message="Your order has been shipped!"
)
```

---

### Apache Airflow 集成

#### 基本功能

```python
from ai_automation_framework.integrations.airflow_integration import AirflowIntegration

# 初始化
airflow = AirflowIntegration(
    base_url="http://localhost:8080",
    username="admin",
    password="admin"
)

# 1. DAG 管理
dags = airflow.list_dags()
dag = airflow.get_dag("dag_id")

# 2. 觸發 DAG
result = airflow.trigger_dag(
    dag_id="example_dag",
    conf={"param1": "value1"}
)

# 3. 查詢執行狀態
dag_run = airflow.get_dag_run("dag_id", "run_id")
print(f"狀態: {dag_run['state']}")

# 4. 暫停/恢復 DAG
airflow.pause_dag("dag_id")
airflow.unpause_dag("dag_id")
```

---

## 統一接口使用

### 單平台使用

```python
from ai_automation_framework.integrations.workflow_automation_unified import (
    UnifiedWorkflowManager,
    WorkflowPlatform
)

manager = UnifiedWorkflowManager()

# 註冊平台
manager.register_n8n("http://localhost:5678", "api_key")

# 觸發工作流
result = manager.trigger_workflow(
    platform=WorkflowPlatform.N8N,
    workflow_id="workflow_123",
    data={"key": "value"}
)
```

### 多平台集成

```python
manager = UnifiedWorkflowManager()

# 註冊多個平台
manager.register_n8n("http://localhost:5678", "n8n_key")
manager.register_zapier(webhook_url="https://hooks.zapier.com/...")
manager.register_make(api_token="make_token")
manager.register_airflow("http://localhost:8080", "admin", "password")

# 廣播觸發
results = manager.broadcast_trigger(
    platforms=[
        WorkflowPlatform.N8N,
        WorkflowPlatform.ZAPIER,
        WorkflowPlatform.MAKE
    ],
    workflow_configs={
        "n8n": "notification_workflow",
        "zapier": "https://hooks.zapier.com/...",
        "make": "scenario_notify"
    },
    data={"event": "order_completed", "order_id": "ORD-123"}
)

# 檢查結果
for platform, result in results.items():
    print(f"{platform}: {result.get('success')}")
```

---

## 高級用法

### 1. 順序工作流編排

```python
from ai_automation_framework.integrations.workflow_automation_unified import (
    WorkflowOrchestrator
)

orchestrator = WorkflowOrchestrator(manager)

# 定義順序步驟
steps = [
    {
        "platform": WorkflowPlatform.N8N,
        "workflow_id": "extract_data",
        "data": {"source": "database"}
    },
    {
        "platform": WorkflowPlatform.MAKE,
        "workflow_id": "transform_data",
        "use_previous_output": True  # 使用前一步的輸出
    },
    {
        "platform": WorkflowPlatform.ZAPIER,
        "workflow_id": "notify_users",
        "use_previous_output": True
    }
]

result = orchestrator.execute_sequential(steps)
```

### 2. 並行工作流執行

```python
# 定義並行任務
workflows = [
    {
        "platform": WorkflowPlatform.N8N,
        "workflow_id": "send_email",
        "data": {"to": "admin@example.com"}
    },
    {
        "platform": WorkflowPlatform.ZAPIER,
        "workflow_id": "log_event",
        "data": {"event_type": "notification_sent"}
    },
    {
        "platform": WorkflowPlatform.MAKE,
        "workflow_id": "update_crm",
        "data": {"customer_id": "CUST-123"}
    }
]

# 並行執行
result = orchestrator.execute_parallel(workflows)
```

### 3. 錯誤處理和重試

```python
import time

def trigger_with_retry(manager, platform, workflow_id, data, max_retries=3):
    """帶重試的工作流觸發"""
    for attempt in range(max_retries):
        result = manager.trigger_workflow(platform, workflow_id, data)

        if result.get('success'):
            return result

        print(f"嘗試 {attempt + 1} 失敗，重試中...")
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # 指數退避

    return result

# 使用
result = trigger_with_retry(
    manager,
    WorkflowPlatform.N8N,
    "critical_workflow",
    {"data": "important"}
)
```

### 4. 條件執行

```python
def conditional_workflow(manager, condition, workflow_a_id, workflow_b_id):
    """根據條件執行不同的工作流"""

    if condition:
        workflow_id = workflow_a_id
        platform = WorkflowPlatform.N8N
    else:
        workflow_id = workflow_b_id
        platform = WorkflowPlatform.ZAPIER

    return manager.trigger_workflow(
        platform=platform,
        workflow_id=workflow_id,
        data={"condition": condition}
    )

# 使用
is_premium_customer = True
result = conditional_workflow(
    manager,
    is_premium_customer,
    "premium_workflow",
    "standard_workflow"
)
```

---

## 最佳實踐

### 1. 環境變量管理

```python
import os
from dotenv import load_dotenv

# 加載環境變量
load_dotenv()

manager = UnifiedWorkflowManager()

# 使用環境變量
manager.register_n8n(
    base_url=os.getenv("N8N_BASE_URL"),
    api_key=os.getenv("N8N_API_KEY")
)
```

### 2. 日誌記錄

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def trigger_with_logging(manager, platform, workflow_id, data):
    """帶日誌的工作流觸發"""
    logger.info(f"觸發工作流: {platform.value}/{workflow_id}")

    result = manager.trigger_workflow(platform, workflow_id, data)

    if result.get('success'):
        logger.info(f"執行成功: {result.get('data', {}).get('id')}")
    else:
        logger.error(f"執行失敗: {result.get('error')}")

    return result
```

### 3. 配置管理

```python
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class WorkflowConfig:
    platform: WorkflowPlatform
    workflow_id: str
    default_data: Dict[str, Any]
    retry_count: int = 3
    timeout: int = 300

# 定義配置
WORKFLOWS = {
    "order_notification": WorkflowConfig(
        platform=WorkflowPlatform.N8N,
        workflow_id="notify_order",
        default_data={"channel": "email"},
        retry_count=3
    ),
    "data_sync": WorkflowConfig(
        platform=WorkflowPlatform.AIRFLOW,
        workflow_id="sync_dag",
        default_data={},
        timeout=600
    )
}

# 使用配置
config = WORKFLOWS["order_notification"]
result = manager.trigger_workflow(
    platform=config.platform,
    workflow_id=config.workflow_id,
    data={**config.default_data, "order_id": "ORD-123"}
)
```

### 4. 監控和告警

```python
def monitor_workflow_execution(manager, platform, execution_id, alert_func=None):
    """監控工作流執行並在失敗時告警"""
    result = manager.get_workflow_status(platform, execution_id)

    if not result.get('success'):
        error_msg = f"工作流執行失敗: {result.get('error')}"

        if alert_func:
            alert_func(error_msg)
        else:
            print(f"❌ {error_msg}")

        return False

    return True

# 使用
def send_alert(message):
    # 發送告警到 Slack/Email 等
    print(f"🚨 告警: {message}")

monitor_workflow_execution(
    manager,
    WorkflowPlatform.N8N,
    "exec_123",
    alert_func=send_alert
)
```

---

## 故障排除

### 常見問題

#### 1. 連接超時

```python
# 增加超時時間
from ai_automation_framework.integrations.n8n_integration_enhanced import N8NEnhanced

n8n = N8NEnhanced(
    base_url="http://localhost:5678",
    api_key="key",
    timeout=60  # 60 秒超時
)
```

#### 2. API 密鑰無效

```bash
# 驗證環境變量
echo $N8N_API_KEY
echo $ZAPIER_API_KEY
echo $MAKE_API_TOKEN

# 重新加載環境變量
source .env  # Bash
# 或
dotenv load  # Python-dotenv
```

#### 3. Webhook URL 錯誤

```python
# 驗證 Webhook URL
webhook_url = "https://hooks.zapier.com/hooks/catch/xxx/yyy/"

# 測試連接
import requests
response = requests.post(webhook_url, json={"test": "data"})
print(response.status_code)  # 應該返回 200
```

#### 4. 數據格式錯誤

```python
# 確保數據是 JSON 可序列化的
import json

data = {
    "string": "text",
    "number": 123,
    "boolean": True,
    "list": [1, 2, 3],
    "dict": {"key": "value"}
}

# 驗證
try:
    json.dumps(data)
    print("✅ 數據格式正確")
except TypeError as e:
    print(f"❌ 數據格式錯誤: {e}")
```

### 調試技巧

```python
# 啟用詳細日誌
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 打印請求和響應
result = manager.trigger_workflow(
    platform=WorkflowPlatform.N8N,
    workflow_id="workflow_id",
    data={"debug": True}
)

print(json.dumps(result, indent=2))
```

---

## 總結

通過本指南，您已經學會了：

- ✅ 集成多個工作流自動化平台
- ✅ 使用統一接口管理工作流
- ✅ 實現順序和並行工作流編排
- ✅ 處理錯誤和實現重試邏輯
- ✅ 應用最佳實踐和監控策略

## 更多資源

- [n8n 文檔](https://docs.n8n.io/)
- [Make 文檔](https://www.make.com/en/help)
- [Zapier 文檔](https://platform.zapier.com/docs/)
- [Airflow 文檔](https://airflow.apache.org/docs/)

---

**最後更新**: 2025-01-XX
**版本**: 2.0.0
