"""
Project Management Tool

Provides project management capabilities including task tracking,
milestone management, and project analysis.
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from .base import BaseTool, ToolResult, ToolCapability, ToolError
import logging

logger = logging.getLogger(__name__)


class ProjectManagementTool(BaseTool):
    """
    Tool for project management operations.

    Provides task management, milestone tracking, and project analysis capabilities.
    """

    def __init__(self):
        super().__init__(
            name="project_management",
            description="Comprehensive project management including task tracking, milestone management, and project analysis",
            category="project_management"
        )
        # In-memory storage for demo (would use database in production)
        self.tasks = {}
        self.milestones = {}
        self.projects = {}

    def get_capabilities(self) -> List[ToolCapability]:
        return [
            ToolCapability(
                name="create_task",
                description="Create a new task",
                parameters={
                    "required": ["title", "description"],
                    "optional": ["priority", "due_date", "assignee", "project_id", "tags"],
                    "title": "Task title",
                    "description": "Task description",
                    "priority": "Task priority (low, medium, high, critical)",
                    "due_date": "Due date in ISO format",
                    "assignee": "Person assigned to the task",
                    "project_id": "ID of the project this task belongs to",
                    "tags": "List of tags for the task"
                },
                examples=["create_task('Fix login bug', 'User cannot login with valid credentials')"],
                category="task"
            ),
            ToolCapability(
                name="update_task",
                description="Update an existing task",
                parameters={
                    "required": ["task_id"],
                    "optional": ["title", "description", "status", "priority", "due_date", "assignee", "tags"],
                    "task_id": "ID of the task to update",
                    "status": "Task status (todo, in_progress, review, done, cancelled)"
                },
                examples=["update_task('task_123', status='in_progress')"],
                category="task"
            ),
            ToolCapability(
                name="get_task",
                description="Get details of a specific task",
                parameters={
                    "required": ["task_id"],
                    "task_id": "ID of the task to retrieve"
                },
                examples=["get_task('task_123')"],
                category="task"
            ),
            ToolCapability(
                name="list_tasks",
                description="List tasks with optional filtering",
                parameters={
                    "optional": ["project_id", "status", "assignee", "priority", "tags"],
                    "project_id": "Filter by project ID",
                    "status": "Filter by task status",
                    "assignee": "Filter by assignee",
                    "priority": "Filter by priority",
                    "tags": "Filter by tags"
                },
                examples=["list_tasks(status='in_progress')", "list_tasks(assignee='john')"],
                category="task"
            ),
            ToolCapability(
                name="create_milestone",
                description="Create a project milestone",
                parameters={
                    "required": ["title", "target_date"],
                    "optional": ["description", "project_id", "tasks"],
                    "title": "Milestone title",
                    "target_date": "Target completion date in ISO format",
                    "description": "Milestone description",
                    "project_id": "ID of the project this milestone belongs to",
                    "tasks": "List of task IDs associated with this milestone"
                },
                examples=["create_milestone('Beta Release', '2024-12-31')"],
                category="milestone"
            ),
            ToolCapability(
                name="analyze_project",
                description="Analyze project progress and metrics",
                parameters={
                    "required": ["project_id"],
                    "optional": ["include_tasks", "include_milestones"],
                    "project_id": "ID of the project to analyze",
                    "include_tasks": "Include detailed task analysis",
                    "include_milestones": "Include milestone analysis"
                },
                examples=["analyze_project('proj_123')"],
                category="analysis"
            ),
            ToolCapability(
                name="generate_report",
                description="Generate project status report",
                parameters={
                    "required": ["report_type"],
                    "optional": ["project_id", "date_range", "format"],
                    "report_type": "Type of report (summary, detailed, timeline)",
                    "project_id": "Specific project to report on",
                    "date_range": "Date range for the report",
                    "format": "Report format (json, markdown, html)"
                },
                examples=["generate_report('summary')", "generate_report('detailed', project_id='proj_123')"],
                category="reporting"
            )
        ]

    async def execute(self, action: str, parameters: Dict[str, Any]) -> ToolResult:
        """Execute project management action"""
        try:
            if action == "create_task":
                return await self._create_task(parameters)
            elif action == "update_task":
                return await self._update_task(parameters)
            elif action == "get_task":
                return await self._get_task(parameters)
            elif action == "list_tasks":
                return await self._list_tasks(parameters)
            elif action == "create_milestone":
                return await self._create_milestone(parameters)
            elif action == "analyze_project":
                return await self._analyze_project(parameters)
            elif action == "generate_report":
                return await self._generate_report(parameters)
            else:
                raise ToolError(f"Unknown action: {action}", tool_name=self.name)

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Project management operation failed: {str(e)}", tool_name=self.name)

    async def _create_task(self, parameters: Dict[str, Any]) -> ToolResult:
        """Create a new task"""
        task_id = f"task_{len(self.tasks) + 1}"

        task = {
            "id": task_id,
            "title": parameters["title"],
            "description": parameters["description"],
            "status": "todo",
            "priority": parameters.get("priority", "medium"),
            "due_date": parameters.get("due_date"),
            "assignee": parameters.get("assignee"),
            "project_id": parameters.get("project_id"),
            "tags": parameters.get("tags", []),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        self.tasks[task_id] = task

        return ToolResult(
            success=True,
            data={"task": task},
            message=f"Successfully created task {task_id}: {task['title']}"
        )

    async def _update_task(self, parameters: Dict[str, Any]) -> ToolResult:
        """Update an existing task"""
        task_id = parameters["task_id"]

        if task_id not in self.tasks:
            raise ToolError(f"Task {task_id} not found", tool_name=self.name)

        task = self.tasks[task_id]

        # Update fields if provided
        updatable_fields = ["title", "description", "status", "priority", "due_date", "assignee", "tags"]
        for field in updatable_fields:
            if field in parameters:
                task[field] = parameters[field]

        task["updated_at"] = datetime.now().isoformat()

        return ToolResult(
            success=True,
            data={"task": task},
            message=f"Successfully updated task {task_id}"
        )

    async def _get_task(self, parameters: Dict[str, Any]) -> ToolResult:
        """Get task details"""
        task_id = parameters["task_id"]

        if task_id not in self.tasks:
            raise ToolError(f"Task {task_id} not found", tool_name=self.name)

        task = self.tasks[task_id]

        return ToolResult(
            success=True,
            data={"task": task},
            message=f"Successfully retrieved task {task_id}"
        )

    async def _list_tasks(self, parameters: Dict[str, Any]) -> ToolResult:
        """List tasks with filtering"""
        filtered_tasks = []

        for task in self.tasks.values():
            # Apply filters
            if parameters.get("project_id") and task.get("project_id") != parameters["project_id"]:
                continue
            if parameters.get("status") and task.get("status") != parameters["status"]:
                continue
            if parameters.get("assignee") and task.get("assignee") != parameters["assignee"]:
                continue
            if parameters.get("priority") and task.get("priority") != parameters["priority"]:
                continue
            if parameters.get("tags"):
                task_tags = task.get("tags", [])
                if not any(tag in task_tags for tag in parameters["tags"]):
                    continue

            filtered_tasks.append(task)

        return ToolResult(
            success=True,
            data={
                "tasks": filtered_tasks,
                "total_count": len(filtered_tasks),
                "filters_applied": {k: v for k, v in parameters.items() if v is not None}
            },
            message=f"Successfully retrieved {len(filtered_tasks)} tasks"
        )
