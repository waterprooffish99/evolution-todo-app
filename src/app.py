#!/usr/bin/env python3
"""Entry point for the in-memory Todo application.

This module serves as the single entry point for the application.
Run with: python3 src/app.py

Architecture:
    src/app.py → src/cli/todo_menu.py → src/skills/task_skills.py → src/models/task.py

See /specs/001-in-memory-todo/quickstart.md for usage instructions.
"""


def main() -> None:
    """Main entry point for the application.

    Initializes the application and starts the menu loop.
    All state is kept in-memory for the duration of the session.
    """
    # Import here to enable cleaner imports elsewhere
    from src.cli.todo_menu import run_menu_loop

    # Start the menu-driven interface
    run_menu_loop()


if __name__ == "__main__":
    main()
