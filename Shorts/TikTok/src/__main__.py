"""Main entry point for TikTok source module.

This allows running the module as a script:
    python -m src.cli [command]
"""

from .cli import main

if __name__ == '__main__':
    main()
