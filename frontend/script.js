// 全局变量
const API_BASE_URL = 'http://localhost:8000';
let isStreaming = false;
let currentEventSource = null;

// DOM 元素
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const messagesContainer = document.getElementById('messagesContainer');
const statusElement = document.getElementById('status');
const loadingOverlay = document.getElementById('loadingOverlay');

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    messageInput.addEventListener('input', handleInputChange);
    messageInput.addEventListener('paste', handleInputChange);
    
    // 自动调整输入框高度
    messageInput.addEventListener('input', autoResizeTextarea);
    
    // 检查后端连接
    checkBackendConnection();
});

// 处理输入变化
function handleInputChange() {
    const hasContent = messageInput.value.trim().length > 0;
    sendButton.disabled = !hasContent || isStreaming;
    
    if (hasContent) {
        sendButton.style.background = 'linear-gradient(135deg, #667eea, #764ba2)';
    } else {
        sendButton.style.background = '#e2e8f0';
    }
}

// 自动调整文本框高度
function autoResizeTextarea() {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
}

// 处理键盘事件
function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        if (!sendButton.disabled) {
            sendMessage();
        }
    }
}

// 检查后端连接
async function checkBackendConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            updateStatus('已连接', 'success');
        } else {
            updateStatus('连接失败', 'error');
        }
    } catch (error) {
        updateStatus('后端未启动', 'error');
        console.error('Backend connection failed:', error);
    }
}

// 更新状态
function updateStatus(message, type = 'info') {
    statusElement.textContent = message;
    statusElement.className = `status ${type}`;
    
    const colors = {
        success: { bg: '#f0f9ff', color: '#0369a1' },
        error: { bg: '#fef2f2', color: '#dc2626' },
        warning: { bg: '#fffbeb', color: '#d97706' },
        info: { bg: '#f0f9ff', color: '#0369a1' }
    };
    
    const style = colors[type] || colors.info;
    statusElement.style.backgroundColor = style.bg;
    statusElement.style.color = style.color;
}

// 发送建议消息
function sendSuggestion(message) {
    messageInput.value = message;
    handleInputChange();
    sendMessage();
}

// 开始新对话
function startNewChat() {
    // 停止当前流
    if (currentEventSource) {
        currentEventSource.close();
        currentEventSource = null;
    }
    
    // 清空消息容器
    messagesContainer.innerHTML = `
        <div class="welcome-message">
            <div class="welcome-icon">
                <i class="fas fa-sparkles"></i>
            </div>
            <h2>欢迎使用 AutoGen Chat</h2>
            <p>我是您的智能助手，可以帮助您解答问题、提供建议和进行对话。</p>
            <div class="suggestion-chips">
                <button class="chip" onclick="sendSuggestion('帮我写一个Python函数')">
                    <i class="fas fa-code"></i>
                    编程帮助
                </button>
                <button class="chip" onclick="sendSuggestion('解释一下机器学习的基本概念')">
                    <i class="fas fa-graduation-cap"></i>
                    学习指导
                </button>
                <button class="chip" onclick="sendSuggestion('帮我规划一下今天的工作')">
                    <i class="fas fa-calendar"></i>
                    日程规划
                </button>
            </div>
        </div>
    `;
    
    isStreaming = false;
    handleInputChange();
    updateStatus('就绪', 'success');
}

// 添加消息到聊天界面
function addMessage(content, isUser = false, isStreaming = false) {
    // 移除欢迎消息
    const welcomeMessage = messagesContainer.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (isStreaming) {
        contentDiv.id = 'streaming-message';
        contentDiv.innerHTML = content + '<span class="cursor">|</span>';
    } else {
        contentDiv.innerHTML = formatMessage(content);
    }
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    
    // 滚动到底部
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return contentDiv;
}

// 格式化消息内容
function formatMessage(content) {
    // 简单的 Markdown 支持
    return content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
}

// 发送消息
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || isStreaming) return;

    // 添加用户消息
    addMessage(message, true);

    // 清空输入框
    messageInput.value = '';
    messageInput.style.height = 'auto';
    handleInputChange();

    // 设置流式状态
    isStreaming = true;
    updateStatus('AI 正在思考...', 'warning');

    try {
        await sendStreamMessage(message);
    } catch (error) {
        console.error('Send message error:', error);
        addMessage('抱歉，发生了错误。请稍后重试。', false);
        updateStatus('发送失败', 'error');
    } finally {
        isStreaming = false;
        handleInputChange();
    }
}

// 发送流式消息
async function sendStreamMessage(message) {
    return new Promise((resolve, reject) => {
        const requestData = {
            message: message,
            system_message: "你是一个智能助手，能够帮助用户解答各种问题。请用中文回答，回答要详细且有帮助。"
        };

        // 创建 EventSource 用于 SSE
        const eventSource = new EventSource(`${API_BASE_URL}/chat/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });

        // 由于 EventSource 不支持 POST，我们使用 fetch 来模拟 SSE
        fetch(`${API_BASE_URL}/chat/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'text/event-stream',
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let streamingContent = '';
            let streamingElement = null;

            function readStream() {
                reader.read().then(({ done, value }) => {
                    if (done) {
                        // 流结束，移除光标
                        if (streamingElement) {
                            const cursor = streamingElement.querySelector('.cursor');
                            if (cursor) cursor.remove();
                        }
                        updateStatus('就绪', 'success');
                        resolve();
                        return;
                    }

                    const chunk = decoder.decode(value, { stream: true });
                    const lines = chunk.split('\n');

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.slice(6));

                                if (data.type === 'content' && data.content) {
                                    streamingContent += data.content;

                                    // 如果还没有流式元素，创建一个
                                    if (!streamingElement) {
                                        streamingElement = addMessage('', false, true);
                                    }

                                    // 更新内容
                                    streamingElement.innerHTML = formatMessage(streamingContent) + '<span class="cursor">|</span>';

                                    // 滚动到底部
                                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                                } else if (data.type === 'end') {
                                    // 流结束
                                    if (streamingElement) {
                                        const cursor = streamingElement.querySelector('.cursor');
                                        if (cursor) cursor.remove();
                                    }
                                    updateStatus('就绪', 'success');
                                    resolve();
                                    return;
                                } else if (data.type === 'error') {
                                    throw new Error(data.content);
                                }
                            } catch (parseError) {
                                console.error('Parse error:', parseError);
                            }
                        }
                    }

                    readStream();
                }).catch(error => {
                    console.error('Stream read error:', error);
                    reject(error);
                });
            }

            readStream();
        })
        .catch(error => {
            console.error('Fetch error:', error);
            reject(error);
        });
    });
}

// 添加光标闪烁动画的CSS
const style = document.createElement('style');
style.textContent = `
    .cursor {
        animation: blink 1s infinite;
        color: #667eea;
        font-weight: bold;
    }

    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0; }
    }

    .status.success {
        background-color: #f0f9ff !important;
        color: #0369a1 !important;
    }

    .status.error {
        background-color: #fef2f2 !important;
        color: #dc2626 !important;
    }

    .status.warning {
        background-color: #fffbeb !important;
        color: #d97706 !important;
    }
`;
document.head.appendChild(style);
