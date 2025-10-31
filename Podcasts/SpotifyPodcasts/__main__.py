"""Entry point for running SpotifyPodcasts as a module.

Usage:
    python -m SpotifyPodcasts scrape-trending
    python -m SpotifyPodcasts scrape-category --category "business"
    python -m SpotifyPodcasts scrape-show --show-id "4rOoJ6Egrf8K2IrywzwOMk"
"""

from .src.cli import main

if __name__ == '__main__':
    main()
