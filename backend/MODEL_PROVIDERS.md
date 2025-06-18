# 模型提供商配置

本项目支持四种 AI 模型提供商：Gemini、DeepSeek、Ollama 和 OpenAI。

## 环境变量配置

在 `backend` 目录下创建 `.env` 文件，并根据需要配置以下环境变量：

### Gemini 配置
```bash
# 必需：Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here
```

### DeepSeek 配置
```bash
# 必需：DeepSeek API Key
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### Ollama 配置
```bash
# 可选：Ollama 服务地址（默认为 http://localhost:11434）
OLLAMA_BASE_URL=http://localhost:11434
```

### OpenAI 配置
```bash
# 必需：OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# 可选：OpenAI 自定义端点（用于 Azure OpenAI 或其他兼容服务）
OPENAI_BASE_URL=https://your-custom-endpoint.com/v1
```

## 支持的模型

### Gemini 模型
- `gemini-2.0-flash` - Gemini 2.0 Flash
- `gemini-2.5-flash-preview-04-17` - Gemini 2.5 Flash
- `gemini-2.5-pro-preview-05-06` - Gemini 2.5 Pro

### DeepSeek 模型
- `deepseek-chat` - DeepSeek Chat
- `deepseek-coder` - DeepSeek Coder

### Ollama 模型
- `qwen3:8b` - Qwen 3 8B

### OpenAI 模型
- `gpt-4.1` - GPT-4.1
- `gpt-4.1-mini` - GPT-4.1 Mini

## 注意事项

1. **网络搜索功能**：目前只有 Gemini 模型支持 Google Search API 功能
2. **API 密钥**：使用 DeepSeek 和 OpenAI 时需要有效的 API 密钥
3. **Ollama 本地部署**：使用 Ollama 时需要确保本地 Ollama 服务正在运行
4. **OpenAI 兼容性**：支持 Azure OpenAI 和其他兼容 OpenAI API 的服务

## 使用方法

1. 配置相应的环境变量
2. 启动后端服务：`langgraph dev`
3. 在前端界面选择模型提供商和具体模型
4. 开始使用！ 