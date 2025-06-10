# 豆包API替换设置指南

## 📋 替换完成状态

✅ **已完成的替换步骤：**

1. **依赖替换** - `langchain-google-genai` → `volcengine-python-sdk[ark]`
2. **配置更新** - 使用豆包模型名称和超时配置
3. **代码重构** - 完全替换为豆包API调用
4. **前端适配** - 更新模型选择器
5. **智能混合策略** - 快速模型 + 深度思考模型

## 🔧 智能模型分配策略

### 🚀 **快速响应节点** (使用 `doubao-pro-256k-241115`)
- **generate_query**: 查询生成 - 注重速度
- **web_research**: 网络搜索和信息提取 - 注重效率

### 🧠 **深度思考节点** (使用 `doubao-1.5-thinking-pro-250415`)
- **reflection**: 反思分析和知识空缺识别 - 注重推理质量
- **finalize_answer**: 最终答案生成 - 注重答案质量

## ⚙️ 环境配置

### 1. 设置豆包API密钥

在 `backend/.env` 文件中添加：

```bash
# 豆包API Key - 必需
ARK_API_KEY=your_ark_api_key_here

# 可选：自定义模型配置
# QUERY_GENERATOR_MODEL=doubao-pro-256k-241115
# REFLECTION_MODEL=doubao-1.5-thinking-pro-250415
# ANSWER_MODEL=doubao-1.5-thinking-pro-250415
# WEB_RESEARCH_MODEL=doubao-pro-256k-241115

# 可选：超时时间配置（秒）
# THINKING_MODEL_TIMEOUT=1800  # 深度思考模型30分钟
# REGULAR_MODEL_TIMEOUT=300    # 常规模型5分钟
```

### 2. 测试API连接

```bash
cd backend
python3 test_doubao.py
```

## 🚀 启动服务

### 后端服务
```bash
cd backend
langgraph dev
```

### 前端服务
```bash
cd frontend
npm run dev
```

## 🎯 核心优势

### 1. **智能混合策略**
- 简单任务用快速模型，复杂推理用深度思考模型
- 平衡响应速度与答案质量
- 优化成本效率

### 2. **深度思考能力**
- `doubao-1.5-thinking-pro-250415` 提供详细思维链
- 在关键决策点使用最强推理能力
- 支持复杂问题的深度分析

### 3. **灵活配置**
- 支持环境变量自定义模型
- 可调整超时时间
- 前端支持模型切换

## 🔍 模型对比

| 节点 | 原Gemini模型 | 新豆包模型 | 选择理由 |
|------|-------------|-----------|----------|
| generate_query | gemini-2.0-flash | doubao-pro-256k | 速度优先，快速生成查询 |
| web_research | gemini-2.0-flash | doubao-pro-256k | 效率优先，快速处理搜索 |
| reflection | gemini-2.5-flash | doubao-thinking-pro | 推理质量，深度分析 |
| finalize_answer | gemini-2.5-pro | doubao-thinking-pro | 最终质量，完整答案 |

## ⚠️ 注意事项

### 1. **网络搜索功能**
当前 `web_research` 函数使用模拟数据。如需实际搜索功能，请：
- 集成Google Search API
- 或使用其他搜索服务
- 或实现自定义搜索逻辑

### 2. **深度思考模型特性**
- 响应时间较长（可能需要几分钟）
- 提供详细的思维过程
- 适合复杂推理任务

### 3. **错误处理**
- 完善的异常处理机制
- API调用失败时优雅降级
- 详细的错误日志输出

## 🎨 前端更新

前端现在支持两种豆包模型选择：
- **Doubao Pro 256K** ⚡ - 快速响应
- **Doubao Thinking Pro** 🧠 - 深度思考

用户可以根据需求选择合适的模型。

## 📊 性能优化

### 超时时间设置
- **深度思考模型**: 30分钟（1800秒）
- **常规模型**: 5分钟（300秒）

### 温度参数
- **查询生成**: 1.0（创造性）
- **反思分析**: 1.0（多样性）
- **最终答案**: 0.0（一致性）
- **网络搜索**: 0.0（准确性）

## 🔧 故障排除

### 常见问题

1. **API密钥错误**
   ```
   ValueError: ARK_API_KEY is not set
   ```
   解决：检查 `.env` 文件中的 `ARK_API_KEY` 设置

2. **模型调用失败**
   ```
   Error calling Doubao model: ...
   ```
   解决：检查网络连接和API密钥权限

3. **JSON解析错误**
   ```
   Invalid JSON response: ...
   ```
   解决：这通常是模型输出格式问题，系统会自动重试

## 🎉 替换完成

恭喜！您已成功将项目从Gemini API替换为豆包API。现在可以：

1. 享受豆包的深度思考能力
2. 体验智能混合模型策略
3. 获得更好的中文支持
4. 实现成本优化的AI研究助手

如有任何问题，请检查日志输出或参考本文档的故障排除部分。 