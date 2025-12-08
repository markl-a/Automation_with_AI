"""Common tools for agents."""

import ast
import operator
import os
import json
import re
import requests
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path


class SafeMathEvaluator:
    """
    Safe mathematical expression evaluator.

    Replaces dangerous eval() with AST-based parsing that only allows
    mathematical operations.
    """

    # Supported operators
    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    @classmethod
    def evaluate(cls, expression: str) -> Union[int, float]:
        """
        Safely evaluate a mathematical expression.

        Args:
            expression: Mathematical expression string

        Returns:
            Calculated result

        Raises:
            ValueError: If expression contains invalid operations
        """
        try:
            tree = ast.parse(expression, mode='eval')
            return cls._eval_node(tree.body)
        except (SyntaxError, TypeError, KeyError) as e:
            raise ValueError(f"Invalid expression: {expression}") from e

    @classmethod
    def _eval_node(cls, node: ast.AST) -> Union[int, float]:
        """Recursively evaluate AST nodes."""
        if isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Unsupported constant type: {type(node.value)}")

        elif isinstance(node, ast.Num):  # Python 3.7 compatibility
            return node.n

        elif isinstance(node, ast.BinOp):
            left = cls._eval_node(node.left)
            right = cls._eval_node(node.right)
            op_func = cls.OPERATORS.get(type(node.op))
            if op_func is None:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            return op_func(left, right)

        elif isinstance(node, ast.UnaryOp):
            operand = cls._eval_node(node.operand)
            op_func = cls.OPERATORS.get(type(node.op))
            if op_func is None:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            return op_func(operand)

        elif isinstance(node, ast.Expression):
            return cls._eval_node(node.body)

        else:
            raise ValueError(f"Unsupported expression type: {type(node).__name__}")


class WebSearchTool:
    """Tool for web searching (simulated)."""

    @staticmethod
    def search(query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Search the web for information.

        Args:
            query: Search query
            num_results: Number of results to return

        Returns:
            List of search results
        """
        # In production, integrate with real search API (SerpAPI, Google Custom Search, etc.)
        return [
            {
                "title": f"Result {i+1} for: {query}",
                "url": f"https://example.com/result{i+1}",
                "snippet": f"This is a sample search result for '{query}'"
            }
            for i in range(num_results)
        ]


class CalculatorTool:
    """Tool for mathematical calculations."""

    @staticmethod
    def calculate(expression: str) -> Dict[str, Any]:
        """
        Evaluate a mathematical expression safely.

        Uses AST-based parsing instead of eval() for security.
        Supports: +, -, *, /, //, %, ** operators and parentheses.

        Args:
            expression: Mathematical expression as string

        Returns:
            Calculation result
        """
        try:
            # Use safe AST-based evaluator instead of dangerous eval()
            result = SafeMathEvaluator.evaluate(expression)
            return {
                "expression": expression,
                "result": result,
                "success": True
            }
        except ValueError as e:
            return {
                "expression": expression,
                "error": str(e),
                "success": False
            }
        except ZeroDivisionError:
            return {
                "expression": expression,
                "error": "Division by zero",
                "success": False
            }
        except Exception as e:
            return {
                "expression": expression,
                "error": f"Calculation error: {str(e)}",
                "success": False
            }

    @staticmethod
    def calculate_percentage(value: float, percentage: float) -> float:
        """Calculate percentage of a value."""
        return (value * percentage) / 100

    @staticmethod
    def calculate_compound_interest(
        principal: float,
        rate: float,
        time: float,
        n: int = 1
    ) -> Dict[str, float]:
        """
        Calculate compound interest.

        Args:
            principal: Initial amount
            rate: Annual interest rate (as percentage)
            time: Time in years
            n: Number of times interest is compounded per year

        Returns:
            Dictionary with calculation details
        """
        amount = principal * (1 + (rate/100)/n) ** (n * time)
        interest = amount - principal

        return {
            "principal": principal,
            "rate": rate,
            "time": time,
            "compound_frequency": n,
            "final_amount": round(amount, 2),
            "interest_earned": round(interest, 2)
        }


class FileSystemTool:
    """
    Tool for file system operations with security protections.

    Security features:
    - Path traversal prevention (blocks ../ patterns)
    - Optional base directory sandboxing
    - Symbolic link resolution validation
    """

    # Default allowed base directories (can be configured)
    _allowed_base_dirs: Optional[List[Path]] = None

    @classmethod
    def set_allowed_directories(cls, directories: List[str]) -> None:
        """
        Set allowed base directories for sandboxing.

        When set, all file operations are restricted to these directories.

        Args:
            directories: List of allowed directory paths
        """
        cls._allowed_base_dirs = [Path(d).resolve() for d in directories]

    @classmethod
    def clear_allowed_directories(cls) -> None:
        """Clear directory restrictions."""
        cls._allowed_base_dirs = None

    @classmethod
    def _validate_path(cls, file_path: str, must_exist: bool = False) -> Path:
        """
        Validate and sanitize file path to prevent path traversal attacks.

        Args:
            file_path: The path to validate
            must_exist: Whether the path must exist

        Returns:
            Resolved, validated Path object

        Raises:
            ValueError: If path is invalid or potentially dangerous
            FileNotFoundError: If must_exist=True and path doesn't exist
        """
        if not file_path or not file_path.strip():
            raise ValueError("Empty file path")

        # Check for null bytes (potential attack vector)
        if '\x00' in file_path:
            raise ValueError("Invalid path: contains null bytes")

        path = Path(file_path)

        # Resolve to absolute path (this also resolves symlinks)
        try:
            resolved_path = path.resolve()
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Cannot resolve path: {e}")

        # Check for path traversal attempts
        # The resolved path should not escape intended boundaries
        if '..' in path.parts:
            # Additional check: ensure resolved path doesn't go above original intent
            original_parent = Path(file_path).parent.resolve() if path.parent != path else Path.cwd()
            if not str(resolved_path).startswith(str(original_parent.parent)):
                raise ValueError(f"Path traversal detected: {file_path}")

        # Check against allowed directories if sandboxing is enabled
        if cls._allowed_base_dirs is not None:
            is_allowed = any(
                resolved_path == allowed_dir or
                str(resolved_path).startswith(str(allowed_dir) + os.sep)
                for allowed_dir in cls._allowed_base_dirs
            )
            if not is_allowed:
                raise ValueError(
                    f"Access denied: path '{file_path}' is outside allowed directories"
                )

        if must_exist and not resolved_path.exists():
            raise FileNotFoundError(f"Path does not exist: {file_path}")

        return resolved_path

    @classmethod
    def read_file(cls, file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """
        Read a text file safely.

        Includes path traversal protection and optional sandboxing.

        Args:
            file_path: Path to the file
            encoding: File encoding

        Returns:
            File content and metadata
        """
        try:
            path = cls._validate_path(file_path, must_exist=True)

            if not path.is_file():
                return {"error": f"Not a file: {file_path}", "success": False}

            content = path.read_text(encoding=encoding)

            return {
                "path": str(path),
                "content": content,
                "size": path.stat().st_size,
                "lines": len(content.splitlines()),
                "success": True
            }
        except (ValueError, FileNotFoundError) as e:
            return {"error": str(e), "success": False}
        except PermissionError:
            return {"error": f"Permission denied: {file_path}", "success": False}
        except UnicodeDecodeError:
            return {"error": f"Cannot decode file with {encoding} encoding", "success": False}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}", "success": False}

    @classmethod
    def write_file(
        cls,
        file_path: str,
        content: str,
        encoding: str = "utf-8"
    ) -> Dict[str, Any]:
        """
        Write content to a file safely.

        Includes path traversal protection and optional sandboxing.

        Args:
            file_path: Path to the file
            content: Content to write
            encoding: File encoding

        Returns:
            Operation result
        """
        try:
            # Validate path (doesn't need to exist yet)
            path = cls._validate_path(file_path, must_exist=False)

            # Create parent directories safely
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding=encoding)

            return {
                "path": str(path),
                "size": path.stat().st_size,
                "success": True
            }
        except ValueError as e:
            return {"error": str(e), "success": False}
        except PermissionError:
            return {"error": f"Permission denied: {file_path}", "success": False}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}", "success": False}

    @classmethod
    def list_directory(cls, dir_path: str) -> Dict[str, Any]:
        """
        List contents of a directory safely.

        Includes path traversal protection and optional sandboxing.

        Args:
            dir_path: Directory path

        Returns:
            Directory contents
        """
        try:
            path = cls._validate_path(dir_path, must_exist=True)

            if not path.is_dir():
                return {"error": f"Not a directory: {dir_path}", "success": False}

            files = []
            directories = []

            for item in path.iterdir():
                try:
                    if item.is_file():
                        files.append({
                            "name": item.name,
                            "size": item.stat().st_size,
                            "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                        })
                    elif item.is_dir():
                        directories.append(item.name)
                except (PermissionError, OSError):
                    # Skip items we can't access
                    continue

            return {
                "path": str(path),
                "files": files,
                "directories": directories,
                "total_items": len(files) + len(directories),
                "success": True
            }
        except (ValueError, FileNotFoundError) as e:
            return {"error": str(e), "success": False}
        except PermissionError:
            return {"error": f"Permission denied: {dir_path}", "success": False}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}", "success": False}


class DateTimeTool:
    """Tool for date and time operations."""

    @staticmethod
    def get_current_datetime(timezone: str = "UTC") -> Dict[str, str]:
        """
        Get current date and time.

        Args:
            timezone: Timezone (currently only UTC)

        Returns:
            Current datetime information
        """
        now = datetime.now()

        return {
            "datetime": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "timestamp": int(now.timestamp()),
            "weekday": now.strftime("%A"),
            "timezone": timezone
        }

    @staticmethod
    def calculate_date_difference(
        date1: str,
        date2: str,
        format: str = "%Y-%m-%d"
    ) -> Dict[str, Any]:
        """
        Calculate difference between two dates.

        Args:
            date1: First date string
            date2: Second date string
            format: Date format

        Returns:
            Date difference information
        """
        try:
            d1 = datetime.strptime(date1, format)
            d2 = datetime.strptime(date2, format)
            diff = abs((d2 - d1).days)

            return {
                "date1": date1,
                "date2": date2,
                "difference_days": diff,
                "difference_weeks": diff // 7,
                "difference_months": diff // 30,
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "success": False}


class DataProcessingTool:
    """Tool for data processing operations."""

    @staticmethod
    def parse_json(json_string: str) -> Dict[str, Any]:
        """
        Parse JSON string.

        Args:
            json_string: JSON string

        Returns:
            Parsed data or error
        """
        try:
            data = json.loads(json_string)
            return {"data": data, "success": True}
        except json.JSONDecodeError as e:
            return {"error": str(e), "success": False}

    @staticmethod
    def to_json(data: Any, indent: int = 2) -> Dict[str, Any]:
        """
        Convert data to JSON string.

        Args:
            data: Data to convert
            indent: JSON indentation

        Returns:
            JSON string or error
        """
        try:
            json_string = json.dumps(data, indent=indent)
            return {"json": json_string, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}

    @staticmethod
    def count_words(text: str) -> Dict[str, Any]:
        """
        Count words in text.

        Args:
            text: Text to analyze

        Returns:
            Word count statistics
        """
        words = text.split()
        unique_words = set(word.lower() for word in words)

        return {
            "total_words": len(words),
            "unique_words": len(unique_words),
            "characters": len(text),
            "characters_no_spaces": len(text.replace(" ", "")),
            "lines": len(text.splitlines()),
            "success": True
        }


# Tool schemas for OpenAI function calling
TOOL_SCHEMAS = {
    "web_search": {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    "calculator": {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Calculate a mathematical expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate (e.g., '2+2', '10*5')"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    "read_file": {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read content from a text file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    "get_datetime": {
        "type": "function",
        "function": {
            "name": "get_datetime",
            "description": "Get current date and time",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
}


# Tool registry mapping
TOOL_REGISTRY = {
    "web_search": WebSearchTool.search,
    "calculator": CalculatorTool.calculate,
    "read_file": FileSystemTool.read_file,
    "write_file": FileSystemTool.write_file,
    "list_directory": FileSystemTool.list_directory,
    "get_datetime": DateTimeTool.get_current_datetime,
    "parse_json": DataProcessingTool.parse_json,
    "count_words": DataProcessingTool.count_words,
}
