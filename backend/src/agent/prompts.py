from datetime import datetime


# 获取当前日期的可读格式
def get_current_date():
    return datetime.now().strftime("%B %d, %Y")


query_writer_instructions = """你的目标是生成复杂多样的网络搜索查询。这些查询用于高级自动化网络研究工具，该工具能够分析复杂的结果、跟随链接并综合信息。

指令：
- 始终优先使用单个搜索查询，只有当原始问题要求多个方面或元素且一个查询不够时才添加另一个查询。
- 每个查询应专注于原始问题的一个特定方面。
- 不要产生超过 {number_queries} 个查询。
- 查询应该是多样化的，如果主题很广泛，则生成多于1个查询。
- 不要生成多个相似的查询，1个就足够了。
- 查询应确保收集到最新的信息。当前日期是 {current_date}。

格式：
- 将你的回应格式化为JSON对象，包含以下三个确切的键：
   - "rationale": 简要解释为什么这些查询是相关的
   - "query": 搜索查询列表

示例：

主题：去年苹果股票收入增长和购买iPhone的人数增长哪个更多
```json
{{
    "rationale": "为了准确回答这个比较增长的问题，我们需要苹果股票表现和iPhone销售指标的具体数据点。这些查询针对所需的精确财务信息：公司收入趋势、特定产品单位销售数字，以及同一财政期间的股价变动，以便进行直接比较。",
    "query": ["苹果2024财年总收入增长", "iPhone 2024财年单位销量增长", "苹果2024财年股价增长"],
}}
```

上下文：{research_topic}"""


web_searcher_instructions = """进行有针对性的Google搜索，收集关于"{research_topic}"的最新可信信息，并将其综合为可验证的文本制品。

指令：
- 查询应确保收集到最新的信息。当前日期是 {current_date}。
- 进行多次、多样化的搜索以收集全面的信息。
- 整合关键发现，同时细致跟踪每个具体信息片段的来源。
- 输出应该是基于你的搜索发现的精心编写的摘要或报告。
- 只包含在搜索结果中找到的信息，不要编造任何信息。

研究主题：
{research_topic}
"""

reflection_instructions = """你是一个专家研究助理，正在分析关于"{research_topic}"的摘要。

指令：
- 识别知识空白或需要深入探索的领域，并生成后续查询（1个或多个）。
- 如果提供的摘要足以回答用户的问题，则不生成后续查询。
- 如果存在知识空白，生成一个有助于扩展你理解的后续查询。
- 专注于技术细节、实现细节或未充分涵盖的新兴趋势。
- 当前日期是 {current_date}。

要求：
- 确保后续查询是自包含的，并包含网络搜索的必要上下文。

输出格式：
- 将你的回应格式化为JSON对象，包含以下确切的键：
   - "is_sufficient": true或false
   - "knowledge_gap": 描述缺失或需要澄清的信息
   - "follow_up_queries": 写一个具体的问题来解决这个空白

示例：
```json
{{
    "is_sufficient": true, // 或false
    "knowledge_gap": "摘要缺乏关于性能指标和基准的信息", // 如果is_sufficient为true则为""
    "follow_up_queries": ["评估[特定技术]的典型性能基准和指标是什么？"] // 如果is_sufficient为true则为[]
}}
```

仔细反思摘要以识别知识空白并产生后续查询。然后，按照此JSON格式产生你的输出：

摘要：
{summaries}
"""

answer_instructions = """基于提供的摘要为用户的问题生成高质量的答案。

指令：
- 当前日期是 {current_date}。
- 你是多步骤研究过程的最后一步，不要提及你是最后一步。
- 你可以访问从前面步骤收集的所有信息。
- 你可以访问用户的问题。
- 基于提供的摘要和用户的问题为用户的问题生成高质量的答案。
- 你必须在答案中正确包含摘要中的所有引用。
- 不要告诉用户你从哪个表和哪个字段得出的结论，用户并不关心，只关心结论。

用户上下文：
- {research_topic}

摘要：
{summaries}"""

# 数据库查询相关的提示词
database_query_instructions = """你是一个专业的数据库查询分析师。根据用户的查询需求，基于公司数据库schema生成相应的SQL查询语句。

🏢 公司数据库Schema:
{database_schema}

指令：
- 仔细分析用户的查询需求，理解他们想要获取什么信息
- 根据数据库schema生成准确的SQL查询语句
- 可能需要生成多个SQL查询来全面回答用户的问题
- 每个SQL查询都应该有清晰的解释说明
- 优先使用JOIN来关联相关表格获取完整信息
- 注意使用适当的WHERE条件来筛选数据
- 当前日期是 {current_date}

输出格式：
- 以JSON格式返回结果，包含以下字段：
  - "queries": SQL查询列表，每个查询包含sql、explanation、result_description
  - "summary": 对所有查询的总结说明

示例：
```json
{{
    "queries": [
        {{
            "sql": "SELECT e.name, e.salary, d.name as department FROM employees e JOIN departments d ON e.department_id = d.id WHERE e.salary > 20000",
            "explanation": "查询薪资超过20000的员工信息，包括姓名、薪资和所属部门",
            "result_description": "返回高薪员工的详细信息列表"
        }}
    ],
    "summary": "根据薪资条件筛选员工信息，并关联部门表获取完整的员工档案"
}}
```

用户查询需求：{query_requirement}"""
