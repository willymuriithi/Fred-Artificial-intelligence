"""Core Fred AI Agent implementation."""

import re
from typing import Optional

from .config import Config
from .memory import ConversationMemory
from .tools import ToolRegistry


class FredAgent:
    """Fred AI - A modular AI agent with tools and memory."""

    SYSTEM_PROMPT = """You are Fred AI, a helpful and capable AI assistant.

You have access to the following tools:
{tools}

When a user request matches a tool's purpose, use the tool by responding with:
[TOOL: tool_name] parameters

For example:
- User: "What's 25 * 4?"
- You: [TOOL: calculator] 25 * 4

- User: "What time is it?"
- You: [TOOL: datetime] %Y-%m-%d %H:%M:%S

If no tool is needed, respond normally and helpfully.
"""

    def __init__(self, config: Optional[Config] = None):
        """Initialize Fred AI agent.
        
        Args:
            config: Configuration object. Creates default if None.
        """
        self.config = config or Config()
        self.memory = ConversationMemory(max_history=self.config.get("max_history", 50))
        self.tool_registry = ToolRegistry()
        self._client = None

    def _get_client(self):
        """Get or create the LLM client."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.config.api_key or "not-set",
                    base_url=self.config.get("api_base_url")
                )
            except ImportError:
                raise ImportError(
                    "OpenAI library not installed. Install with: pip install openai"
                )
        return self._client

    def _parse_tool_call(self, response: str) -> Optional[tuple[str, str]]:
        """Parse tool call from response.
        
        Args:
            response: The LLM response text
            
        Returns:
            Tuple of (tool_name, parameters) or None if no tool call
        """
        pattern = r'\[TOOL:\s*(\w+)\]\s*(.*)'
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            return match.group(1), match.group(2).strip()
        return None

    def _execute_tool(self, tool_name: str, params: str) -> str:
        """Execute a tool with given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            params: Parameters string for the tool
            
        Returns:
            Tool execution result
        """
        tool = self.tool_registry.get(tool_name)
        if not tool:
            return f"Error: Unknown tool '{tool_name}'"
        
        try:
            # Parse params based on tool
            if tool_name == "calculator":
                return tool.execute(expression=params)
            elif tool_name == "datetime":
                return tool.execute(format=params or "%Y-%m-%d %H:%M:%S")
            elif tool_name == "echo":
                return tool.execute(message=params)
            else:
                return tool.execute()
        except Exception as e:
            return f"Tool error: {str(e)}"

    def chat(self, message: str) -> str:
        """Send a message and get a response.
        
        Args:
            message: User's message
            
        Returns:
            Agent's response
        """
        # Add user message to memory
        self.memory.add_message("user", message)

        # Build messages for LLM
        tools_desc = self.tool_registry.get_tool_descriptions()
        system_prompt = self.SYSTEM_PROMPT.format(tools=tools_desc)
        
        messages = [
            {"role": "system", "content": system_prompt},
            *self.memory.get_context_messages(n=self.config.get("max_history", 50) - 2)
        ]

        # Get LLM response
        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.get("temperature", 0.7),
                max_tokens=self.config.get("max_tokens", 2048)
            )
            assistant_message = response.choices[0].message.content or ""
        except Exception as e:
            assistant_messages = f"Error: Could not get LLM response - {str(e)}"

        # Check for tool call
        tool_call = self._parse_tool_call(assistant_messages)
        if tool_call:
            tool_name, params = tool_call
            if self.config.verbose:
                print(f"[Fred] Executing tool: {tool_name} with params: {params}")
            
            tool_result = self._execute_tool(tool_name, params)
            
            # Add tool result to conversation
            self.memory.add_message("assistant", f"Using {tool_name}...")
            self.memory.add_message("user", f"[Tool result: {tool_result}]")
            
            # Get final response with tool result
            messages = [
                {"role": "system", "content": system_prompt},
                *self.memory.get_context_messages()
            ]
            
            try:
                client = self._get_client()
                response = client.chat.completions.create(
                    model=self.config.model,
                    messages=messages,
                    temperature=self.config.get("temperature", 0.7),
                    max_tokens=self.config.get("max_tokens", 2048)
                )
                assistant_messages = response.choices[0].message.content or ""
            except Exception as e:
                assistant_messages = f"Tool result: {tool_result}"

        # Add assistant response to memory
        self.memory.add_message("assistant", assistant_messages)

        if self.config.verbose:
            print(f"[Fred] {assistant_messages}")

        return assistant_messages

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.memory.clear()

    def save_conversation(self, name: Optional[str] = None) -> str:
        """Save current conversation.
        
        Args:
            name: Optional name for the conversation
            
        Returns:
            Path to saved file
        """
        return self.memory.save_conversation(name)

    def set_verbose(self, verbose: bool) -> None:
        """Enable/disable verbose mode.
        
        Args:
            verbose: Whether to enable verbose output
        """
        self.config.verbose = verbose
