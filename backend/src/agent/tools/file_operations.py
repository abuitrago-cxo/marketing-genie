"""
File Operations Tool

Provides comprehensive file system operations for the AI agent.
Inspired by II-Agent's file handling capabilities but designed for our system.
"""

import os
import shutil
import pathlib
from typing import Dict, Any, List, Optional
import aiofiles
import json
import yaml
from .base import BaseTool, ToolResult, ToolCapability, ToolError
import logging

logger = logging.getLogger(__name__)


class FileOperationsTool(BaseTool):
    """
    Tool for file system operations.

    Provides safe file operations with proper error handling and validation.
    """

    def __init__(self, base_path: str = ".", allowed_extensions: Optional[List[str]] = None):
        super().__init__(
            name="file_operations",
            description="Comprehensive file system operations including read, write, create, delete, and directory management",
            category="file_system"
        )
        self.base_path = pathlib.Path(base_path).resolve()
        self.allowed_extensions = allowed_extensions or [
            '.txt', '.md', '.json', '.yaml', '.yml', '.py', '.js', '.ts',
            '.html', '.css', '.xml', '.csv', '.log'
        ]

    def get_capabilities(self) -> List[ToolCapability]:
        return [
            ToolCapability(
                name="read_file",
                description="Read contents of a file",
                parameters={
                    "required": ["file_path"],
                    "optional": ["encoding"],
                    "file_path": "Path to the file to read",
                    "encoding": "File encoding (default: utf-8)"
                },
                examples=["read_file('/path/to/file.txt')", "read_file('config.json')"],
                category="read"
            ),
            ToolCapability(
                name="write_file",
                description="Write content to a file",
                parameters={
                    "required": ["file_path", "content"],
                    "optional": ["encoding", "create_dirs"],
                    "file_path": "Path to the file to write",
                    "content": "Content to write to the file",
                    "encoding": "File encoding (default: utf-8)",
                    "create_dirs": "Create parent directories if they don't exist"
                },
                examples=["write_file('/path/to/file.txt', 'Hello World')"],
                category="write"
            ),
            ToolCapability(
                name="list_directory",
                description="List contents of a directory",
                parameters={
                    "required": ["directory_path"],
                    "optional": ["recursive", "include_hidden"],
                    "directory_path": "Path to the directory to list",
                    "recursive": "List subdirectories recursively",
                    "include_hidden": "Include hidden files and directories"
                },
                examples=["list_directory('/path/to/dir')", "list_directory('.', recursive=True)"],
                category="directory"
            ),
            ToolCapability(
                name="create_directory",
                description="Create a new directory",
                parameters={
                    "required": ["directory_path"],
                    "optional": ["parents"],
                    "directory_path": "Path to the directory to create",
                    "parents": "Create parent directories if they don't exist"
                },
                examples=["create_directory('/path/to/new/dir')"],
                category="directory"
            ),
            ToolCapability(
                name="delete_file",
                description="Delete a file",
                parameters={
                    "required": ["file_path"],
                    "file_path": "Path to the file to delete"
                },
                examples=["delete_file('/path/to/file.txt')"],
                category="delete"
            ),
            ToolCapability(
                name="copy_file",
                description="Copy a file to another location",
                parameters={
                    "required": ["source_path", "destination_path"],
                    "optional": ["overwrite"],
                    "source_path": "Path to the source file",
                    "destination_path": "Path to the destination",
                    "overwrite": "Overwrite destination if it exists"
                },
                examples=["copy_file('/source/file.txt', '/dest/file.txt')"],
                category="copy"
            ),
            ToolCapability(
                name="move_file",
                description="Move a file to another location",
                parameters={
                    "required": ["source_path", "destination_path"],
                    "optional": ["overwrite"],
                    "source_path": "Path to the source file",
                    "destination_path": "Path to the destination",
                    "overwrite": "Overwrite destination if it exists"
                },
                examples=["move_file('/source/file.txt', '/dest/file.txt')"],
                category="move"
            ),
            ToolCapability(
                name="get_file_info",
                description="Get information about a file or directory",
                parameters={
                    "required": ["path"],
                    "path": "Path to the file or directory"
                },
                examples=["get_file_info('/path/to/file.txt')"],
                category="info"
            )
        ]

    def _validate_path(self, path: str) -> pathlib.Path:
        """Validate and resolve a file path"""
        try:
            resolved_path = pathlib.Path(path).resolve()

            # Security check: ensure path is within base_path
            if not str(resolved_path).startswith(str(self.base_path)):
                raise ToolError(
                    f"Path {path} is outside allowed base path {self.base_path}",
                    tool_name=self.name
                )

            return resolved_path
        except Exception as e:
            raise ToolError(f"Invalid path {path}: {str(e)}", tool_name=self.name)

    def _validate_file_extension(self, path: pathlib.Path):
        """Validate file extension"""
        if self.allowed_extensions and path.suffix.lower() not in self.allowed_extensions:
            raise ToolError(
                f"File extension {path.suffix} not allowed. Allowed: {self.allowed_extensions}",
                tool_name=self.name
            )

    async def execute(self, action: str, parameters: Dict[str, Any]) -> ToolResult:
        """Execute file operation"""
        try:
            if action == "read_file":
                return await self._read_file(parameters)
            elif action == "write_file":
                return await self._write_file(parameters)
            elif action == "list_directory":
                return await self._list_directory(parameters)
            elif action == "create_directory":
                return await self._create_directory(parameters)
            elif action == "delete_file":
                return await self._delete_file(parameters)
            elif action == "copy_file":
                return await self._copy_file(parameters)
            elif action == "move_file":
                return await self._move_file(parameters)
            elif action == "get_file_info":
                return await self._get_file_info(parameters)
            else:
                raise ToolError(f"Unknown action: {action}", tool_name=self.name)

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"File operation failed: {str(e)}", tool_name=self.name)

    async def _read_file(self, parameters: Dict[str, Any]) -> ToolResult:
        """Read file contents"""
        file_path = self._validate_path(parameters["file_path"])
        encoding = parameters.get("encoding", "utf-8")

        if not file_path.exists():
            raise ToolError(f"File {file_path} does not exist", tool_name=self.name)

        if not file_path.is_file():
            raise ToolError(f"Path {file_path} is not a file", tool_name=self.name)

        self._validate_file_extension(file_path)

        async with aiofiles.open(file_path, 'r', encoding=encoding) as f:
            content = await f.read()

        return ToolResult(
            success=True,
            data={
                "content": content,
                "file_path": str(file_path),
                "size": file_path.stat().st_size,
                "encoding": encoding
            },
            message=f"Successfully read file {file_path}"
        )

    async def _write_file(self, parameters: Dict[str, Any]) -> ToolResult:
        """Write content to file"""
        file_path = self._validate_path(parameters["file_path"])
        content = parameters["content"]
        encoding = parameters.get("encoding", "utf-8")
        create_dirs = parameters.get("create_dirs", True)

        self._validate_file_extension(file_path)

        # Create parent directories if needed
        if create_dirs and not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(file_path, 'w', encoding=encoding) as f:
            await f.write(content)

        return ToolResult(
            success=True,
            data={
                "file_path": str(file_path),
                "size": len(content.encode(encoding)),
                "encoding": encoding
            },
            message=f"Successfully wrote to file {file_path}"
        )

    async def _list_directory(self, parameters: Dict[str, Any]) -> ToolResult:
        """List directory contents"""
        dir_path = self._validate_path(parameters["directory_path"])
        recursive = parameters.get("recursive", False)
        include_hidden = parameters.get("include_hidden", False)

        if not dir_path.exists():
            raise ToolError(f"Directory {dir_path} does not exist", tool_name=self.name)

        if not dir_path.is_dir():
            raise ToolError(f"Path {dir_path} is not a directory", tool_name=self.name)

        items = []

        def scan_directory(path: pathlib.Path, level: int = 0):
            try:
                for item in path.iterdir():
                    if not include_hidden and item.name.startswith('.'):
                        continue

                    item_info = {
                        "name": item.name,
                        "path": str(item),
                        "type": "directory" if item.is_dir() else "file",
                        "size": item.stat().st_size if item.is_file() else None,
                        "level": level
                    }
                    items.append(item_info)

                    if recursive and item.is_dir() and level < 10:  # Limit recursion depth
                        scan_directory(item, level + 1)
            except PermissionError:
                logger.warning(f"Permission denied accessing {path}")

        scan_directory(dir_path)

        return ToolResult(
            success=True,
            data={
                "directory": str(dir_path),
                "items": items,
                "total_items": len(items)
            },
            message=f"Successfully listed directory {dir_path}"
        )

    async def _create_directory(self, parameters: Dict[str, Any]) -> ToolResult:
        """Create directory"""
        dir_path = self._validate_path(parameters["directory_path"])
        parents = parameters.get("parents", True)

        if dir_path.exists():
            return ToolResult(
                success=True,
                data={"directory": str(dir_path)},
                message=f"Directory {dir_path} already exists"
            )

        dir_path.mkdir(parents=parents, exist_ok=True)

        return ToolResult(
            success=True,
            data={"directory": str(dir_path)},
            message=f"Successfully created directory {dir_path}"
        )

    async def _delete_file(self, parameters: Dict[str, Any]) -> ToolResult:
        """Delete file"""
        file_path = self._validate_path(parameters["file_path"])

        if not file_path.exists():
            raise ToolError(f"File {file_path} does not exist", tool_name=self.name)

        if file_path.is_file():
            file_path.unlink()
        elif file_path.is_dir():
            shutil.rmtree(file_path)

        return ToolResult(
            success=True,
            data={"deleted_path": str(file_path)},
            message=f"Successfully deleted {file_path}"
        )

    async def _copy_file(self, parameters: Dict[str, Any]) -> ToolResult:
        """Copy file"""
        source_path = self._validate_path(parameters["source_path"])
        dest_path = self._validate_path(parameters["destination_path"])
        overwrite = parameters.get("overwrite", False)

        if not source_path.exists():
            raise ToolError(f"Source file {source_path} does not exist", tool_name=self.name)

        if dest_path.exists() and not overwrite:
            raise ToolError(f"Destination {dest_path} exists and overwrite is False", tool_name=self.name)

        if source_path.is_file():
            shutil.copy2(source_path, dest_path)
        elif source_path.is_dir():
            shutil.copytree(source_path, dest_path, dirs_exist_ok=overwrite)

        return ToolResult(
            success=True,
            data={
                "source": str(source_path),
                "destination": str(dest_path)
            },
            message=f"Successfully copied {source_path} to {dest_path}"
        )

    async def _move_file(self, parameters: Dict[str, Any]) -> ToolResult:
        """Move file"""
        source_path = self._validate_path(parameters["source_path"])
        dest_path = self._validate_path(parameters["destination_path"])
        overwrite = parameters.get("overwrite", False)

        if not source_path.exists():
            raise ToolError(f"Source file {source_path} does not exist", tool_name=self.name)

        if dest_path.exists() and not overwrite:
            raise ToolError(f"Destination {dest_path} exists and overwrite is False", tool_name=self.name)

        shutil.move(str(source_path), str(dest_path))

        return ToolResult(
            success=True,
            data={
                "source": str(source_path),
                "destination": str(dest_path)
            },
            message=f"Successfully moved {source_path} to {dest_path}"
        )

    async def _get_file_info(self, parameters: Dict[str, Any]) -> ToolResult:
        """Get file information"""
        path = self._validate_path(parameters["path"])

        if not path.exists():
            raise ToolError(f"Path {path} does not exist", tool_name=self.name)

        stat = path.stat()
        info = {
            "path": str(path),
            "name": path.name,
            "type": "directory" if path.is_dir() else "file",
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "accessed": stat.st_atime,
            "permissions": oct(stat.st_mode)[-3:]
        }

        if path.is_file():
            info["extension"] = path.suffix

        return ToolResult(
            success=True,
            data=info,
            message=f"Successfully retrieved info for {path}"
        )
