# 模型配置总结

## 当前支持的模型提供商和模型

### 1. Gemini (Google)
- **模型**: 
  - `gemini-2.0-flash` - Gemini 2.0 Flash
  - `gemini-2.5-flash-preview-04-17` - Gemini 2.5 Flash  
  - `gemini-2.5-pro-preview-05-06` - Gemini 2.5 Pro
- **环境变量**: `GEMINI_API_KEY`
- **特殊功能**: 支持 Google Search API

### 2. DeepSeek
- **模型**:
  - `deepseek-chat` - DeepSeek Chat
  - `deepseek-coder` - DeepSeek Coder
- **环境变量**: `DEEPSEEK_API_KEY`

### 3. Ollama (本地部署)
- **模型**:
  - `qwen3:8b` - Qwen 3 8B
- **环境变量**: `OLLAMA_BASE_URL` (默认: http://localhost:11434)

### 4. OpenAI
- **模型**:
  - `gpt-4.1` - GPT-4.1
  - `gpt-4.1-mini` - GPT-4.1 Mini
- **环境变量**: 
  - `OPENAI_API_KEY` (必需)
  - `OPENAI_BASE_URL` (可选，用于自定义端点)

## 配置检查清单

- [ ] 前端模型选项与后端 LLM 工厂配置一致
- [ ] 文档中的模型列表与实际支持的模型一致
- [ ] 环境变量配置说明完整
- [ ] 默认模型配置正确

## 注意事项

1. **网络搜索**: 仅 Gemini 支持 Google Search API
2. **API 密钥**: DeepSeek 和 OpenAI 需要有效的 API 密钥
3. **本地服务**: Ollama 需要本地服务运行
4. **兼容性**: OpenAI 支持 Azure OpenAI 等兼容服务 