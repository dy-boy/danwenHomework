# AutoGen Chat Application

基于AutoGen 0.5.7的智能对话应用，具有炫酷的前端界面和FastAPI后端。

## 项目结构

```
├── frontend/          # 前端界面（类似Gemini风格）
├── backend/           # FastAPI后端服务
├── study_env/         # Python虚拟环境
└── study_env_projectFile/  # 示例文件
```

## 功能特性

- 🤖 基于AutoGen 0.5.7的智能对话
- 🎨 炫酷的Gemini风格前端界面
- ⚡ FastAPI后端，支持SSE流式输出
- 🔄 实时对话体验

## 技术栈

### 后端
- FastAPI
- AutoGen 0.5.7
- SSE (Server-Sent Events)
- Python 3.x

### 前端
- HTML5/CSS3/JavaScript
- 现代化UI设计
- 响应式布局

## 配置信息

- API密钥: sk-dc3c24db09fe4fd383c0a198dda84e0e
- Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
- 模型: deepseek-r1

## 快速开始

### 方式一：一键启动（推荐）
```bash
python start_project.py
```

### 方式二：手动启动

#### 1. 安装依赖
```bash
pip install -r backend/requirements.txt
```

#### 2. 启动后端
```bash
cd backend
python start.py
```

#### 3. 访问前端
- 主界面：打开 `frontend/index.html`
- 测试页面：打开 `frontend/test.html`

## 项目特色

### 🎨 前端特性
- **Gemini风格设计**：现代化、炫酷的用户界面
- **实时流式输出**：支持SSE协议，实时显示AI回复
- **响应式布局**：适配各种屏幕尺寸
- **智能建议**：预设常用对话场景
- **状态指示**：实时显示连接和处理状态

### ⚡ 后端特性
- **FastAPI框架**：高性能异步API服务
- **AutoGen集成**：基于最新0.5.7版本
- **流式输出**：SSE协议支持实时响应
- **配置管理**：灵活的配置系统
- **错误处理**：完善的异常处理机制
- **日志系统**：详细的运行日志

### 🤖 AI能力
- **智能对话**：基于DeepSeek-R1模型
- **多场景支持**：编程、学习、规划等
- **中文优化**：专门优化的中文对话体验
- **上下文理解**：保持对话连贯性

## API接口

### 健康检查
```http
GET /health
```

### 非流式聊天
```http
POST /chat
Content-Type: application/json

{
  "message": "你好",
  "system_message": "你是一个友好的助手"
}
```

### 流式聊天
```http
POST /chat/stream
Content-Type: application/json

{
  "message": "请写一个Python函数",
  "system_message": "你是一个编程助手"
}
```

### 统计信息
```http
GET /stats
```

## 测试

### 运行API测试
```bash
cd backend
python test_api.py
```

### 前端测试
打开 `frontend/test.html` 进行交互式测试

## 配置说明

### 环境变量（可选）
```bash
export AUTOGEN_API_KEY="your-api-key"
export AUTOGEN_BASE_URL="your-base-url"
export AUTOGEN_MODEL_NAME="your-model"
export SERVER_HOST="0.0.0.0"
export SERVER_PORT="8000"
```

### 配置文件
编辑 `backend/config.py` 修改默认配置

## 故障排除

### 常见问题

1. **后端启动失败**
   - 检查Python版本（需要3.8+）
   - 确认依赖包已安装
   - 检查端口8000是否被占用

2. **前端无法连接后端**
   - 确认后端服务已启动
   - 检查防火墙设置
   - 验证API地址配置

3. **AI回复异常**
   - 检查API密钥是否正确
   - 验证网络连接
   - 查看后端日志

### 日志查看
后端日志会显示详细的运行信息，包括请求处理、错误信息等。

## 开发说明

### 项目架构
```
├── frontend/           # 前端文件
│   ├── index.html     # 主界面
│   ├── styles.css     # 样式文件
│   ├── script.js      # 交互逻辑
│   └── test.html      # 测试页面
├── backend/           # 后端文件
│   ├── main.py        # 主应用
│   ├── config.py      # 配置管理
│   ├── autogen_manager.py  # AutoGen管理器
│   ├── start.py       # 启动脚本
│   ├── test_api.py    # API测试
│   └── requirements.txt    # 依赖列表
├── start_project.py   # 项目启动脚本
└── README.md         # 项目说明
```

### 技术栈
- **前端**：HTML5, CSS3, JavaScript (ES6+)
- **后端**：Python 3.8+, FastAPI, AutoGen 0.5.7
- **通信**：RESTful API, Server-Sent Events (SSE)
- **AI模型**：DeepSeek-R1 (通过阿里云DashScope)

项目使用AutoGen进行智能对话，通过SSE协议实现流式输出，为用户提供流畅的对话体验。
