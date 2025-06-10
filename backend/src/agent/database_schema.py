# 数据库Schema配置
# 这里定义了数据库的表结构，便于维护和查询生成

DATABASE_SCHEMA = {
    "departments": {
        "description": "部门信息表", 
        "columns": [
            {"name": "id", "type": "INTEGER", "description": "部门ID，主键"},
            {"name": "name", "type": "VARCHAR(100)", "description": "部门名称"},
            {"name": "budget", "type": "DECIMAL(12,2)", "description": "部门预算"},
            {"name": "head_id", "type": "INTEGER", "description": "部门负责人ID，外键"},
            {"name": "location", "type": "VARCHAR(100)", "description": "部门所在地"}
        ]
    },
    "employees": {
        "description": "员工信息表",
        "columns": [
            {"name": "id", "type": "INTEGER", "description": "员工ID，主键"},
            {"name": "name", "type": "VARCHAR(100)", "description": "员工姓名"},
            {"name": "email", "type": "VARCHAR(200)", "description": "员工邮箱，唯一"},
            {"name": "department_id", "type": "INTEGER", "description": "部门ID，外键"},
            {"name": "position", "type": "VARCHAR(100)", "description": "职位"},
            {"name": "hire_date", "type": "DATE", "description": "入职日期"},
            {"name": "salary", "type": "DECIMAL(10,2)", "description": "薪资"},
            {"name": "manager_id", "type": "INTEGER", "description": "直属经理ID，外键"},
            {"name": "status", "type": "VARCHAR(20)", "description": "员工状态：active, inactive, terminated"},
            {"name": "phone", "type": "VARCHAR(20)", "description": "电话号码"},
            {"name": "address", "type": "VARCHAR(200)", "description": "地址"},
            {"name": "birth_date", "type": "DATE", "description": "出生日期"}
        ]
    },
    "projects": {
        "description": "项目信息表",
        "columns": [
            {"name": "id", "type": "INTEGER", "description": "项目ID，主键"},
            {"name": "name", "type": "VARCHAR(200)", "description": "项目名称"},
            {"name": "description", "type": "TEXT", "description": "项目描述"},
            {"name": "start_date", "type": "DATE", "description": "项目开始日期"},
            {"name": "end_date", "type": "DATE", "description": "项目结束日期"},
            {"name": "budget", "type": "DECIMAL(12,2)", "description": "项目预算"},
            {"name": "status", "type": "VARCHAR(20)", "description": "项目状态：planning, active, completed, on_hold, cancelled"},
            {"name": "manager_id", "type": "INTEGER", "description": "项目经理ID，外键"},
            {"name": "priority", "type": "VARCHAR(10)", "description": "项目优先级：high, medium, low"},
            {"name": "client", "type": "VARCHAR(100)", "description": "客户信息"}
        ]
    },
    "project_assignments": {
        "description": "项目分配表，记录员工参与项目的情况",
        "columns": [
            {"name": "id", "type": "INTEGER", "description": "分配ID，主键"},
            {"name": "project_id", "type": "INTEGER", "description": "项目ID，外键"},
            {"name": "employee_id", "type": "INTEGER", "description": "员工ID，外键"},
            {"name": "role", "type": "VARCHAR(100)", "description": "在项目中的角色"},
            {"name": "start_date", "type": "DATE", "description": "参与开始日期"},
            {"name": "end_date", "type": "DATE", "description": "参与结束日期"},
            {"name": "workload_percentage", "type": "INTEGER", "description": "工作负载百分比"},
            {"name": "hourly_rate", "type": "DECIMAL(8,2)", "description": "小时费率"}
        ]
    },
    "salaries": {
        "description": "薪资记录表，按月记录员工薪资详情",
        "columns": [
            {"name": "id", "type": "INTEGER", "description": "薪资记录ID，主键"},
            {"name": "employee_id", "type": "INTEGER", "description": "员工ID，外键"},
            {"name": "year", "type": "INTEGER", "description": "年份"},
            {"name": "month", "type": "INTEGER", "description": "月份"},
            {"name": "base_salary", "type": "DECIMAL(10,2)", "description": "基本工资"},
            {"name": "bonus", "type": "DECIMAL(10,2)", "description": "奖金"},
            {"name": "overtime_pay", "type": "DECIMAL(10,2)", "description": "加班费"},
            {"name": "total_amount", "type": "DECIMAL(10,2)", "description": "总金额"},
            {"name": "deductions", "type": "DECIMAL(8,2)", "description": "扣除金额"}
        ]
    },
    "clients": {
        "description": "客户信息表",
        "columns": [
            {"name": "id", "type": "INTEGER", "description": "客户ID，主键"},
            {"name": "name", "type": "VARCHAR(200)", "description": "客户公司名称"},
            {"name": "contact_person", "type": "VARCHAR(100)", "description": "联系人姓名"},
            {"name": "email", "type": "VARCHAR(200)", "description": "联系邮箱"},
            {"name": "phone", "type": "VARCHAR(20)", "description": "联系电话"},
            {"name": "address", "type": "VARCHAR(300)", "description": "客户地址"},
            {"name": "industry", "type": "VARCHAR(100)", "description": "所属行业"},
            {"name": "status", "type": "VARCHAR(20)", "description": "客户状态：active, inactive, potential"}
        ]
    },
    "equipment": {
        "description": "设备信息表，记录公司设备分配情况",
        "columns": [
            {"name": "id", "type": "INTEGER", "description": "设备ID，主键"},
            {"name": "name", "type": "VARCHAR(200)", "description": "设备名称"},
            {"name": "type", "type": "VARCHAR(100)", "description": "设备类型"},
            {"name": "model", "type": "VARCHAR(100)", "description": "设备型号"},
            {"name": "serial_number", "type": "VARCHAR(100)", "description": "序列号，唯一"},
            {"name": "purchase_date", "type": "DATE", "description": "购买日期"},
            {"name": "price", "type": "DECIMAL(10,2)", "description": "购买价格"},
            {"name": "employee_id", "type": "INTEGER", "description": "分配给的员工ID，外键"},
            {"name": "status", "type": "VARCHAR(20)", "description": "设备状态：active, maintenance, retired"}
        ]
    }
}

# 表之间的关系
TABLE_RELATIONSHIPS = {
    "employees.department_id": "departments.id",
    "employees.manager_id": "employees.id",
    "departments.head_id": "employees.id", 
    "projects.manager_id": "employees.id",
    "project_assignments.project_id": "projects.id",
    "project_assignments.employee_id": "employees.id",
    "salaries.employee_id": "employees.id",
    "equipment.employee_id": "employees.id"
}

def get_schema_description():
    """获取数据库schema的文本描述，用于AI理解"""
    description = "🏢 公司数据库包含以下表：\n\n"
    
    for table_name, table_info in DATABASE_SCHEMA.items():
        description += f"**{table_name}** - {table_info['description']}\n"
        description += "列：\n"
        for col in table_info['columns']:
            description += f"  - {col['name']} ({col['type']}): {col['description']}\n"
        description += "\n"
    
    description += "🔗 表关系：\n"
    for fk, pk in TABLE_RELATIONSHIPS.items():
        description += f"  - {fk} → {pk}\n"
    
    return description

def get_table_names():
    """获取所有表名"""
    return list(DATABASE_SCHEMA.keys())

def get_table_schema(table_name):
    """获取指定表的schema"""
    return DATABASE_SCHEMA.get(table_name)

def get_full_schema_for_ai():
    """获取完整的schema信息，专门用于AI查询生成"""
    schema_text = get_schema_description()
    
    schema_text += "\n💡 查询建议：\n"
    schema_text += "- 使用JOIN连接相关表获取完整信息\n"
    schema_text += "- 统计查询使用COUNT、AVG、SUM等聚合函数\n"
    schema_text += "- 时间范围查询注意日期格式\n"
    schema_text += "- 薪资相关查询可结合年月维度分析\n"
    schema_text += "- 项目查询可按状态、优先级等筛选\n"
    
    return schema_text 