// AutoGen Chat Frontend JavaScript

class AutoGenChat {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000';
        this.currentConversationId = null;
        this.isStreaming = false;
        this.chatHistory = [];
        
        this.initializeElements();
        this.bindEvents();
        this.loadChatHistory();
        
        // 配置marked.js
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                highlight: function(code, lang) {
                    if (typeof hljs !== 'undefined' && lang && hljs.getLanguage(lang)) {
                        try {
                            return hljs.highlight(code, { language: lang }).value;
                        } catch (err) {}
                    }
                    return code;
                },
                breaks: true,
                gfm: true
            });
        }
    }
    
    initializeElements() {
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.messagesContainer = document.getElementById('messagesContainer');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.chatHistoryList = document.getElementById('chatHistoryList');
    }
    
    bindEvents() {
        // 输入框事件
        this.messageInput.addEventListener('input', () => {
            this.updateSendButton();
            this.adjustTextareaHeight(this.messageInput);
        });
        
        // 发送按钮事件
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // 键盘事件
        this.messageInput.addEventListener('keydown', (e) => this.handleKeyDown(e));
        
        // 状态更新
        this.updateStatus('就绪', 'ready');
    }
    
    handleKeyDown(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            this.sendMessage();
        }
    }
    
    adjustTextareaHeight(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
    
    updateSendButton() {
        const hasText = this.messageInput.value.trim().length > 0;
        this.sendButton.disabled = !hasText || this.isStreaming;
    }
    
    updateStatus(text, type = 'ready') {
        const statusText = this.statusIndicator.querySelector('.status-text');
        const statusDot = this.statusIndicator.querySelector('.status-dot');
        
        statusText.textContent = text;
        
        // 更新状态点颜色
        statusDot.className = 'status-dot';
        switch (type) {
            case 'thinking':
                statusDot.style.background = '#ea4335';
                break;
            case 'typing':
                statusDot.style.background = '#fbbc04';
                break;
            case 'ready':
            default:
                statusDot.style.background = '#34a853';
                break;
        }
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isStreaming) return;
        
        // 清空输入框
        this.messageInput.value = '';
        this.adjustTextareaHeight(this.messageInput);
        this.updateSendButton();
        
        // 隐藏欢迎消息
        const welcomeMessage = document.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.style.display = 'none';
        }
        
        // 添加用户消息
        this.addMessage(message, 'user');
        
        // 开始流式对话
        await this.streamChat(message);
    }
    
    async streamChat(message) {
        this.isStreaming = true;
        this.updateSendButton();
        this.updateStatus('AI正在思考...', 'thinking');
        
        // 添加打字指示器
        const typingIndicator = this.addTypingIndicator();
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/chat/stream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    conversation_id: this.currentConversationId
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            // 移除打字指示器
            typingIndicator.remove();
            
            // 创建AI消息容器
            const aiMessageElement = this.addMessage('', 'ai');
            const contentElement = aiMessageElement.querySelector('.message-content');
            
            this.updateStatus('AI正在回复...', 'typing');
            
            // 处理流式响应
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            let fullResponse = '';
            
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop(); // 保留不完整的行
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        if (data === '[DONE]') {
                            this.updateStatus('就绪', 'ready');
                            break;
                        }
                        
                        try {
                            const parsed = JSON.parse(data);
                            if (parsed.type === 'message' && parsed.content) {
                                fullResponse = parsed.content;
                                // 使用marked.js渲染Markdown
                                if (typeof marked !== 'undefined') {
                                    contentElement.innerHTML = marked.parse(fullResponse);
                                } else {
                                    contentElement.textContent = fullResponse;
                                }
                                
                                // 高亮代码块
                                if (typeof hljs !== 'undefined') {
                                    contentElement.querySelectorAll('pre code').forEach((block) => {
                                        hljs.highlightElement(block);
                                    });
                                }
                                
                                // 滚动到底部
                                this.scrollToBottom();
                            } else if (parsed.type === 'error') {
                                this.showError(parsed.message);
                            }
                        } catch (e) {
                            console.warn('Failed to parse SSE data:', data);
                        }
                    }
                }
            }
            
            // 保存对话到历史
            this.saveChatToHistory(message, fullResponse);
            
        } catch (error) {
            console.error('Stream chat error:', error);
            typingIndicator.remove();
            this.showError(`连接错误: ${error.message}`);
        } finally {
            this.isStreaming = false;
            this.updateSendButton();
            this.updateStatus('就绪', 'ready');
        }
    }
    
    addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const now = new Date();
        const timeString = now.toLocaleTimeString('zh-CN', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        const avatar = sender === 'user' ? '👤' : '🤖';
        const senderName = sender === 'user' ? '您' : 'AutoGen AI';
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <div class="message-avatar ${sender}-avatar">${avatar}</div>
                <span class="message-sender">${senderName}</span>
                <span class="message-time">${timeString}</span>
            </div>
            <div class="message-content">${content}</div>
        `;
        
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
        
        return messageDiv;
    }
    
    addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.innerHTML = `
            <span>AI正在思考</span>
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        
        this.messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
        
        return typingDiv;
    }
    
    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `
            <span class="material-icons">error</span>
            <span>${message}</span>
        `;
        
        this.messagesContainer.appendChild(errorDiv);
        this.scrollToBottom();
        
        // 3秒后自动移除错误消息
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 3000);
    }
    
    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    saveChatToHistory(userMessage, aiResponse) {
        const chatItem = {
            id: Date.now(),
            title: userMessage.substring(0, 30) + (userMessage.length > 30 ? '...' : ''),
            timestamp: new Date().toISOString(),
            messages: [
                { sender: 'user', content: userMessage },
                { sender: 'ai', content: aiResponse }
            ]
        };
        
        this.chatHistory.unshift(chatItem);
        this.updateChatHistoryUI();
        this.saveChatHistoryToStorage();
    }
    
    loadChatHistory() {
        const saved = localStorage.getItem('autogen-chat-history');
        if (saved) {
            try {
                this.chatHistory = JSON.parse(saved);
                this.updateChatHistoryUI();
            } catch (e) {
                console.warn('Failed to load chat history:', e);
            }
        }
    }
    
    saveChatHistoryToStorage() {
        try {
            localStorage.setItem('autogen-chat-history', JSON.stringify(this.chatHistory));
        } catch (e) {
            console.warn('Failed to save chat history:', e);
        }
    }
    
    updateChatHistoryUI() {
        this.chatHistoryList.innerHTML = '';
        
        this.chatHistory.slice(0, 10).forEach(chat => {
            const chatItem = document.createElement('div');
            chatItem.className = 'chat-history-item';
            chatItem.innerHTML = `
                <div class="chat-title">${chat.title}</div>
                <div class="chat-time">${new Date(chat.timestamp).toLocaleDateString('zh-CN')}</div>
            `;
            
            chatItem.addEventListener('click', () => this.loadChat(chat));
            this.chatHistoryList.appendChild(chatItem);
        });
    }
    
    loadChat(chat) {
        // 清空当前对话
        this.clearChat();

        // 加载历史消息
        chat.messages.forEach(msg => {
            this.addMessage(msg.content, msg.sender);
        });
    }

    clearChat() {
        // 清空消息容器，但保留欢迎消息
        const messages = this.messagesContainer.querySelectorAll('.message, .typing-indicator, .error-message');
        messages.forEach(msg => msg.remove());

        // 显示欢迎消息
        const welcomeMessage = document.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.style.display = 'block';
        }

        this.currentConversationId = null;
    }
}

// 全局函数
function sendSuggestion(text) {
    const chat = window.autoGenChat;
    if (chat) {
        chat.messageInput.value = text;
        chat.updateSendButton();
        chat.sendMessage();
    }
}

function startNewChat() {
    const chat = window.autoGenChat;
    if (chat) {
        chat.clearChat();
        chat.currentConversationId = null;

        // 显示欢迎消息
        const welcomeMessage = document.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.style.display = 'block';
        }
    }
}

function clearChat() {
    const chat = window.autoGenChat;
    if (chat) {
        // 清空消息容器，但保留欢迎消息
        const messages = chat.messagesContainer.querySelectorAll('.message, .typing-indicator, .error-message');
        messages.forEach(msg => msg.remove());

        // 显示欢迎消息
        const welcomeMessage = document.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.style.display = 'block';
        }

        chat.currentConversationId = null;
    }
}

function toggleTheme() {
    const body = document.body;
    const isDark = !body.classList.contains('light-theme');

    if (isDark) {
        body.classList.add('light-theme');
        localStorage.setItem('theme', 'light');
    } else {
        body.classList.remove('light-theme');
        localStorage.setItem('theme', 'dark');
    }

    // 更新主题切换按钮图标
    const themeButton = document.querySelector('.action-btn .material-icons');
    if (themeButton && themeButton.textContent === 'dark_mode') {
        themeButton.textContent = isDark ? 'light_mode' : 'dark_mode';
    }
}

function adjustTextareaHeight(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function sendMessage() {
    const chat = window.autoGenChat;
    if (chat) {
        chat.sendMessage();
    }
}

// 添加聊天历史样式
const historyStyles = `
.chat-history-item {
    padding: 12px 16px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all var(--transition-fast);
}

.chat-history-item:hover {
    background: var(--bg-hover);
    border-color: var(--primary-color);
    transform: translateX(4px);
}

.chat-history-item .chat-title {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 4px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.chat-history-item .chat-time {
    font-size: 12px;
    color: var(--text-muted);
}
`;

// 添加样式到页面
const styleSheet = document.createElement('style');
styleSheet.textContent = historyStyles;
document.head.appendChild(styleSheet);

// 初始化应用
document.addEventListener('DOMContentLoaded', function() {
    // 加载保存的主题
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.body.classList.add('light-theme');
        const themeButton = document.querySelector('.action-btn .material-icons');
        if (themeButton && themeButton.textContent === 'dark_mode') {
            themeButton.textContent = 'light_mode';
        }
    }

    // 初始化聊天应用
    window.autoGenChat = new AutoGenChat();

    console.log('🚀 AutoGen Chat Frontend initialized!');
});
