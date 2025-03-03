"""Command pattern implementation for image processing operations."""

from PySide6 import QtGui as Gui
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from ..gui.main_window import MainWindow

__all__ = ['ImageProcessCommand', 'ImageState']


@dataclass
class ImageState:
    """Represents the state of an image for undo/redo operations.
    
    Attributes:
        path: Path to the image file
        effect: Name of the effect applied, if any
    """
    path: str
    effect: Optional[str] = None


class ImageProcessCommand(Gui.QUndoCommand):
    """Command for applying image processing effects.
    
    Handles the undo/redo functionality for image processing operations.
    
    Attributes:
        window: Reference to the main window
        effect_type: Type of effect being applied
        old_state: Previous state of the image
        new_state: New state after applying the effect
    """
    
    def __init__(self, window: 'MainWindow', effect_type: str) -> None:
        """Initialize the command.
        
        Args:
            window: Reference to the main window
            effect_type: Type of effect to apply
        """
        super().__init__(f"Apply {effect_type}")
        self.window = window
        self.effect_type = effect_type
        self.old_state = ImageState(window.current_image)
        self.new_state: Optional[ImageState] = None

    def redo(self) -> None:
        """Apply the effect or restore the processed state."""
        if self.new_state:
            self.window.load_specific_image(self.new_state.path)
        else:
            self.window.process_image_internal(self.effect_type, self)

    def undo(self) -> None:
        """Restore the previous image state."""
        self.window.load_specific_image(self.old_state.path) 
    