"""Batch processing functionality for image operations."""

from dataclasses import dataclass
from typing import List, Dict, Optional
from pathlib import Path
import tempfile

__all__ = ['BatchProcessor', 'ImageState']

@dataclass
class ImageState:
    """Represents the state of an image during processing.
    
    Attributes:
        path: Path to the image file
        effect: Name of the effect applied, if any
        is_temp: Whether this is a temporary file
    """
    path: str
    effect: Optional[str] = None
    is_temp: bool = False



class BatchProcessor:
    """Handles batch processing operations for multiple images.
    
    Manages effect queues and temporary files for batch image processing.
    
    Attributes:
        effects_queue: List of effects to apply to images
        processed_images: Dictionary mapping original paths to processed paths
    """
    
    def __init__(self) -> None:
        """Initialize the batch processor."""
        self.effects_queue: List[str] = []
        self.temp_dir = tempfile.mkdtemp()
        self.processed_images: Dict[str, str] = {}
    
    def add_effect(self, effect: str) -> None:
        """Add an effect to the processing queue.
        
        Args:
            effect: Name of the effect to add
        """
        self.effects_queue.append(effect)
    
    def clear_effects(self) -> None:
        """Clear all queued effects."""
        self.effects_queue.clear()
    
    def get_temp_path(self, original_path: str) -> str:
        """Generate a temporary path for processed images.
        
        Args:
            original_path: Original image path
            
        Returns:
            Path for the temporary processed file
        """
        return str(Path(self.temp_dir) / f"temp_{Path(original_path).name}") 