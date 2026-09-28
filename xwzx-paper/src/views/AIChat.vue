<template>
  <div class="ai-chat-container">
    <van-nav-bar title="AI问答" fixed />

    <div class="chat-content">
      <div class="messages-container" ref="messagesContainer">
        <div
            v-for="(message, index) in messages"
            :key="index"
            :class="['message', message.role === 'user' ? 'user-message' : 'ai-message']"
        >
          <div class="message-content">
            <div v-if="message.role === 'assistant' && message.content === ''" class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <div v-else v-html="formatMessage(message.content)"></div>
          </div>
        </div>
      </div>

      <div class="chat-options">
        <label class="option-label" style="display: flex; align-items: center; cursor: pointer; color: #666; font-size: 13px;">
          <input
              type="checkbox"
              v-model="isStreaming"
              style="margin-right: 6px; width: 16px; height: 16px; cursor: pointer;"
          />
          开启流式响应 (打字机效果)
        </label>
      </div>

      <div class="input-container">
        <van-field
            v-model="userInput"
            rows="1"
            autosize
            type="textarea"
            placeholder="请输入问题..."
            class="chat-input"
            @keypress.enter.prevent="sendMessage"
        />
        <van-button
            type="primary"
            class="send-button"
            :disabled="isLoading || !userInput.trim()"
            @click="sendMessage"
        >
          发送
        </van-button>
      </div>
    </div>

    <tab-bar />
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue';
import TabBar from '../components/TabBar.vue';
import { showToast } from 'vant';
import * as marked from 'marked';
import DOMPurify from 'dompurify';
import { aiChatConfig } from '../config/api';

// 聊天消息
const messages = ref([
  { role: 'assistant', content: '你好！我是AI助手，有什么可以帮助你的吗？' }
]);
const userInput = ref('');
const messagesContainer = ref(null);
const isLoading = ref(false);

// 控制是否开启流式响应的变量，默认开启(true)
const isStreaming = ref(true);

// 从配置文件获取API设置
const chatEndpoint = ref(aiChatConfig.chatEndpoint);

// 格式化消息内容（支持Markdown）
const formatMessage = (content) => {
  if (!content) return '';
  return DOMPurify.sanitize(marked.parse(content));
};

// 发送消息
const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return;

  const userMessage = userInput.value.trim();
  messages.value.push({ role: 'user', content: userMessage });
  userInput.value = '';

  messages.value.push({ role: 'assistant', content: '' });

  await nextTick();
  scrollToBottom();

  isLoading.value = true;
  try {
    await fetchAIResponse(userMessage);
  } catch (error) {
    console.error('Error fetching AI response:', error);
    messages.value[messages.value.length - 1].content = `发生错误: ${error.message || '请检查网络连接和后端服务'}`;
  } finally {
    isLoading.value = false;
    await nextTick();
    scrollToBottom();
  }
};

// 获取AI响应
const fetchAIResponse = async (userMessage) => {
  const historyMessages = messages.value
      .slice(0, -1)
      .map(msg => ({ role: msg.role, content: msg.content }));

  try {
    const response = await fetch(chatEndpoint.value, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: userMessage,
        history: historyMessages,
        stream: isStreaming.value // 动态读取上方开关的状态
      })
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || `HTTP error! status: ${response.status}`);
    }

    const contentType = response.headers.get('content-type');

    // 如果响应头是事件流，则走流式处理
    if (contentType && contentType.includes('text/event-stream')) {
      await handleStreamResponse(response);
    } else {
      // 否则走非流式一次性返回处理
      const data = await response.json();

      if (data.code === 200 && data.data?.reply) {
        messages.value[messages.value.length - 1].content = data.data.reply;
      } else {
        messages.value[messages.value.length - 1].content = data.message || 'AI 回复失败';
      }
    }
  } catch (error) {
    console.error('Fetch error:', error);
    throw error;
  }
};

// 处理流式响应(SSE)
const handleStreamResponse = async (response) => {
  console.log('>>> 开始处理流式响应');
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let aiResponse = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        console.log('>>> 流式响应结束');
        break;
      }

      const chunk = decoder.decode(value, { stream: true });
      console.log('>>> 收到原始chunk:', chunk.substring(0, 100));
      
      buffer += chunk;
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        console.log('>>> 处理行:', line);
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          console.log('>>> SSE数据:', data);
          if (data === '[DONE]') {
            console.log('>>> 收到[DONE]标记');
            continue;
          }

          try {
            const json = JSON.parse(data);
            console.log('>>> 解析JSON成功:', json);
            const content = json.choices?.[0]?.delta?.content || '';
            if (content) {
              aiResponse += content;
              messages.value[messages.value.length - 1].content = aiResponse;
              await nextTick();
              scrollToBottom();
            }
          } catch (e) {
            console.error('Error parsing SSE data:', e, '原始数据:', data);
          }
        }
      }
    }

    if (!aiResponse) {
      console.warn('>>> 没有收到任何AI回复内容');
      messages.value[messages.value.length - 1].content = '抱歉，我无法生成回复。请稍后再试。';
    } else {
      console.log('>>> AI回复完成，总长度:', aiResponse.length);
    }
  } finally {
    reader.releaseLock();
  }
};

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

watch(messages, () => {
  nextTick(scrollToBottom);
}, { deep: true });

onMounted(() => {
  scrollToBottom();
});
</script>

<style scoped>
.ai-chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding-top: 46px;
  padding-bottom: 50px;
  box-sizing: border-box;
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: #f7f8fa;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.message {
  margin-bottom: 10px;
  max-width: 80%;
}

.user-message {
  margin-left: auto;
}

.ai-message {
  margin-right: auto;
}

.message-content {
  padding: 10px;
  border-radius: 10px;
  word-break: break-word;
}

.user-message .message-content {
  background-color: #007aff;
  color: white;
  border-bottom-right-radius: 2px;
}

.ai-message .message-content {
  background-color: #fff;
  color: #333;
  border-bottom-left-radius: 2px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

/* 选项工具栏样式 */
.chat-options {
  display: flex;
  justify-content: flex-end;
  padding: 8px 12px;
  background-color: #fff;
  border-top: 1px solid #eee;
}

.input-container {
  display: flex;
  padding: 10px;
  background-color: #fff;
}

.chat-input {
  flex: 1;
  margin-right: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
}

.send-button {
  align-self: flex-end;
}

/* Markdown 样式 */
.message-content pre {
  background-color: #f8f8f8;
  padding: 10px;
  border-radius: 5px;
  overflow-x: auto;
}

.message-content code {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 2px 4px;
  border-radius: 3px;
}

.message-content img {
  max-width: 100%;
}

/* 打字指示器 */
.typing-indicator {
  display: flex;
  padding: 5px;
}

.typing-indicator span {
  height: 8px;
  width: 8px;
  background-color: #999;
  border-radius: 50%;
  margin: 0 2px;
  display: inline-block;
  animation: bounce 1.5s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-5px);
  }
}

/* Markdown样式覆盖 */
:deep(pre) {
  background-color: #f0f0f0;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}

:deep(code) {
  font-family: monospace;
  background-color: #f0f0f0;
  padding: 2px 4px;
  border-radius: 4px;
}

:deep(p) {
  margin: 8px 0;
}

:deep(ul), :deep(ol) {
  padding-left: 20px;
}

:deep(a) {
  color: #1989fa;
  text-decoration: none;
}
</style>