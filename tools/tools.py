"""Tools system for Fred AI."""

from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """Base class for all Fred AI tools."""

    name: str = "base_tool"
    description: str = "Base tool description"

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            The result of the tool execution
        """
        pass

    def to_dict(self) -> dict:
        """Convert tool to dictionary for LLM function calling."""
        return {
            "name": self.name,
            "description": self.description,
        }


class CalculatorTool(BaseTool):
    """Simple calculator tool for basic math operations."""

    name = "calculator"
    description = "Perform basic arithmetic calculations. Supports +, -, *, / operations."

    def execute(self, expression: str) -> str:
        """Evaluate a mathematical expression.
        
        Args:
            expression: A mathematical expression string (e.g., "2 + 2")
            
        Returns:
            The result as a string
        """
        try:
            # Safe evaluation of basic math
            allowed_chars = set("0123456789+-*/.() ")
            if not all(c in allowed_chars for c in expression):
                return "Error: Invalid characters in expression"
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"Error: {str(e)}"


class DateTimeTool(BaseTool):
    """Tool for getting current date and time information."""

    name = "datetime"
    description = "Get the current date and time information."

    def execute(self, format: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Get current date/time.
        
        Args:
            format: strftime format string
            
        Returns:
            Formatted current date/time
        """
        from datetime import datetime
        return datetime.now().strftime(format)


class EchoTool(BaseTool):
    """Simple echo tool for testing."""

    name = "echo"
    description = "Echo back the input message. Useful for testing."

    def execute(self, message: str) -> str:
        """Echo the message back.
        
        Args:
            message: The message to echo
            
        Returns:
            The same message
        """
        return f"Echo: {message}"


class ToolRegistry:
    """Registry for managing available tools."""

    def __init__(self):
        """Initialize the tool registry."""
        self._tools: dict[str, BaseTool] = {}
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Register default tools."""
        self.register(CalculatorTool())
        self.register(DateTimeTool())
        self.register(EchoTool())

    def register(self, tool: BaseTool) -> None:
        """Register a tool.
        
        Args:
            tool: The tool to register
        """
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name.
        
        Args:
            name: The tool name
            
        Returns:
            The tool instance or None if not found
        """
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        """List all registered tool names.
        
        Returns:
            List of tool names
        """
        return list(self._tools.keys())

    def get_tool_descriptions(self) -> str:
        """Get descriptions of all tools.
        
        Returns:
            Formatted string of tool descriptions
        """
        descriptions = []
        for tool in self._tools.values():
            descriptions.append(f"- {tool.name}: {tool.description}")
        return "\n".join(descriptions)
