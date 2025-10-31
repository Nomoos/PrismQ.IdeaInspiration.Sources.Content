"""Plugin modules for SpotifyPodcasts source.

All plugins inherit from SourcePlugin base class and implement the scrape() method.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class SourcePlugin(ABC):
    """Base class for all source plugins."""
    
    def __init__(self, config):
        """Initialize plugin with configuration.
        
        Args:
            config: Configuration object
        """
        self.config = config
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name as string
        """
        pass
    
    @abstractmethod
    def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        """Scrape ideas from the source.
        
        Args:
            **kwargs: Source-specific parameters
            
        Returns:
            List of idea dictionaries
        """
        pass
