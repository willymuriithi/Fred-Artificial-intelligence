#!/usr/bin/env python3
"""Fred AI - Command Line Interface."""

import argparse
import sys
from typing import Optional


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="fred",
        description="Fred AI - Your friendly AI assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  fred                    Start interactive chat
  fred -c "What is 25 * 4?"   Single command execution
  fred --verbose          Enable verbose output
  fred --config           Show current configuration
        """
    )

    parser.add_argument(
        "-c", "--command",
        type=str,
        help="Execute a single command and exit"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--config",
        action="store_true",
        help="Show or edit configuration"
    )

    parser.add_argument(
        "--set-api-key",
        type=str,
        help="Set the API key"
    )

    parser.add_argument(
        "--set-model",
        type=str,
        help="Set the model to use"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Fred AI v0.1.0"
    )

    return parser


def print_banner() -> None:
    """Print the Fred AI banner."""
    banner = """
╔═══════════════════════════════════════╗
║         🤖 Fred AI v0.1.0             ║
║    Your friendly AI assistant         ║
╚═══════════════════════════════════════╝

Type 'quit' or 'exit' to end the conversation.
Type 'clear' to clear conversation history.
Type 'save [name]' to save the conversation.
Type 'tools' to list available tools.
"""
    print(banner)


def interactive_mode(agent) -> None:
    """Run Fred AI in interactive mode.
    
    Args:
        agent: FredAgent instance
    """
    print_banner()
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ("quit", "exit"):
                print("\n🤖 Fred: Goodbye! Have a great day!")
                break
            
            if user_input.lower() == "clear":
                agent.clear_history()
                print("\n🤖 Fred: Conversation history cleared.")
                continue
            
            if user_input.lower() == "tools":
                tools = agent.tool_registry.list_tools()
                print(f"\n🤖 Fred: Available tools: {', '.join(tools)}")
                continue
            
            if user_input.lower().startswith("save"):
                parts = user_input.split(maxsplit=1)
                name = parts[1] if len(parts) > 1 else None
                filepath = agent.save_conversation(name)
                print(f"\n🤖 Fred: Conversation saved to: {filepath}")
                continue
            
            # Get response from agent
            print("\n🤖 Fred: ", end="", flush=True)
            response = agent.chat(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\n🤖 Fred: Interrupted. Type 'quit' to exit.")
        except EOFError:
            print("\n\n🤖 Fred: Goodbye!")
            break


def single_command_mode(agent, command: str) -> None:
    """Execute a single command.
    
    Args:
        agent: FredAgent instance
        command: Command to execute
    """
    response = agent.chat(command)
    print(response)


def config_mode(agent, set_api_key: Optional[str] = None, set_model: Optional[str] = None) -> None:
    """Handle configuration commands.
    
    Args:
        agent: FredAgent instance
        set_api_key: API key to set
        set_model: Model to set
    """
    from .config import Config
    
    config = agent.config
    
    if set_api_key:
        config.api_key = set_api_key
        config.save()
        print("✅ API key saved.")
    
    if set_model:
        config.model = set_model
        config.save()
        print(f"✅ Model set to: {set_model}")
    
    # Show current config
    print("\n📋 Current Configuration:")
    print(f"   Model: {config.model}")
    print(f"   API Key: {'*' * 8 + config.api_key[-4:] if config.api_key else 'Not set'}")
    print(f"   Verbose: {config.verbose}")
    print(f"   Max History: {config.get('max_history', 50)}")
    print(f"   Config File: {config.config_path}")


def main() -> int:
    """Main entry point.
    
    Returns:
        Exit code
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # Import here to avoid circular imports
    from .agent import FredAgent
    from .config import Config
    
    # Load configuration
    config = Config()
    
    # Handle command line args
    if args.verbose:
        config.verbose = True
    
    # Create agent
    agent = FredAgent(config=config)
    
    # Handle configuration commands
    if args.set_api_key or args.set_model or args.config:
        config_mode(agent, set_api_key=args.set_api_key, set_model=args.set_model)
        return 0
    
    # Execute single command or start interactive mode
    if args.command:
        single_command_mode(agent, args.command)
    else:
        interactive_mode(agent)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
