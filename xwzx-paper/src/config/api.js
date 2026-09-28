/**
 * API配置文件
 */

// API基础URL配置
export const apiConfig = {
  baseURL: 'http://127.0.0.1:8000',
}

// AI 问答功能配置
export const aiChatConfig = {
  chatEndpoint: `${apiConfig.baseURL}/api/ai/chat`,
  nonStreamEndpoint: `${apiConfig.baseURL}/api/ai/chat/non-stream`,
  useStream: true,
}