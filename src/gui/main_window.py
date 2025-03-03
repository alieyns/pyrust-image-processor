"""Main window implementation for the VFX Image Processor.

This module contains the main application window and core UI logic.
"""

from PySide6 import QtCore as Core
from PySide6 import QtGui as Gui
from PySide6 import QtWidgets as Widgets
from typing import Optional, List
from pathlib import Path
import logging
import image_processor_rust

from ..processing.batch_processor import BatchProcessor
from ..processing.commands import ImageProcessCommand, ImageState

__all__ = ['MainWindow', 'ProcessingThread']

# Constants
Qt = Core.Qt
SUPPORTED_FORMATS = "Images (*.png *.jpg *.jpeg *.tiff *.bmp)"
MIN_WINDOW_SIZE = Core.QSize(1024, 768)
IMAGE_PREVIEW_SIZE = Core.QSize(640, 480)

# Configure logging
logging.basicConfig(level=logging.INFO)



class ProcessingThread(Core.QThread):
    """Thread for handling image processing operations.
    
    Attributes:
        progress: Signal emitting processing progress (0-100)
        finished: Signal emitting path to processed image
    """
    progress = Core.Signal(int)
    finished = Core.Signal(str)
    
    def __init__(self, input_path: str, effect_type: str, output_path: str) -> None:
        """Initialize the processing thread.
        
        Args:
            input_path: Path to input image
            effect_type: Type of effect to apply
            output_path: Path for output image
        """
        super().__init__()
        self.input_path = input_path
        self.effect_type = effect_type
        self.output_path = output_path
        
    def run(self) -> None:
        """Execute the image processing operation."""
        try:
            result_path = image_processor_rust.process_image(
                self.input_path,
                self.effect_type,
                self.output_path,
                lambda x: self.progress.emit(x)
            )
            self.finished.emit(result_path)
        except Exception as e:
            logging.error(f"Processing error: {e}")

class MainWindow(Widgets.QMainWindow):
    """Main application window for the VFX Image Processor.
    
    Handles the main UI layout, image processing operations, and batch processing.
    
    Attributes:
        current_image: Path to the currently loaded image
        current_processed_image: Path to the current processed image
        batch_files: List of files queued for batch processing
    """

    def __init__(self) -> None:
        """Initialize the main window and setup UI components."""
        super().__init__()
        
        self.current_image: Optional[str] = None
        self.current_processed_image: Optional[str] = None
        self.batch_files: List[str] = []
        
        self.undo_stack = Gui.QUndoStack(self)
        self.batch_processor = BatchProcessor()
        
        self.setWindowTitle("VFX Image Processor")
        self.setMinimumSize(MIN_WINDOW_SIZE)
        
        self._setup_shortcuts()
        self._setup_menu()
        self._setup_ui()

    def _setup_shortcuts(self) -> None:
        """Configure keyboard shortcuts for the application."""
        self.undo_action = self.undo_stack.createUndoAction(self)
        self.undo_action.setShortcut(Gui.QKeySequence.Undo)
        
        self.redo_action = self.undo_stack.createRedoAction(self)
        self.redo_action.setShortcut(Gui.QKeySequence.Redo)
        
        self.addAction(self.undo_action)
        self.addAction(self.redo_action)

    def _setup_menu(self) -> None:
        """Setup the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        actions = [
            ("Open Image", self.load_image, Gui.QKeySequence.Open),
            ("Open Multiple Images", self.load_batch_images, None),
            ("Save Current Image", self.save_current_image, Gui.QKeySequence.Save),
            ("Save All Processed Images", self.save_processed_images, "Ctrl+Shift+S")
        ]
        
        for label, slot, shortcut in actions:
            action = Gui.QAction(label, self)
            action.triggered.connect(slot)
            if shortcut:
                action.setShortcut(shortcut)
            file_menu.addAction(action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)

    def _setup_ui(self) -> None:
        """Setup the main UI components."""
        main_widget = Widgets.QWidget()
        self.setCentralWidget(main_widget)
        main_layout = Widgets.QHBoxLayout(main_widget)
        
        # Left panel for batch processing
        left_panel = Widgets.QWidget()
        left_layout = Widgets.QVBoxLayout(left_panel)
        
        self.batch_list = Widgets.QListWidget()
        self.batch_list.setSelectionMode(Widgets.QListWidget.ExtendedSelection)
        self.batch_list.itemClicked.connect(self.preview_batch_image)
        left_layout.addWidget(self.batch_list)
        
        self.process_batch_button = Widgets.QPushButton("Process Selected")
        self.process_batch_button.clicked.connect(self.process_batch)
        self.process_batch_button.setEnabled(False)
        left_layout.addWidget(self.process_batch_button)
        
        main_layout.addWidget(left_panel)
        
        # Center panel for image display
        center_panel = Widgets.QWidget()
        center_layout = Widgets.QVBoxLayout(center_panel)
        
        self.image_label = Widgets.QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(IMAGE_PREVIEW_SIZE)
        self.image_label.setStyleSheet("QLabel { background-color: #2a2a2a; }")
        center_layout.addWidget(self.image_label)
        
        self.progress_bar = Widgets.QProgressBar()
        self.progress_bar.setVisible(False)
        center_layout.addWidget(self.progress_bar)
        
        # Effects buttons
        effects_layout = Widgets.QHBoxLayout()
        effects = [
            ("Edge Detect", "edge_detect"),
            ("Blur", "blur"),
            ("Sharpen", "sharpen"),
            ("Grayscale", "grayscale"),
            ("Sepia", "sepia"),
            ("Invert", "invert")
        ]
        
        for label, effect in effects:
            btn = Widgets.QPushButton(label)
            btn.clicked.connect(lambda checked, e=effect: self.process_image(e))
            btn.setEnabled(False)
            effects_layout.addWidget(btn)
        
        self.save_button = Widgets.QPushButton("Save All")
        self.save_button.clicked.connect(self.save_processed_images)
        self.save_button.setEnabled(False)
        effects_layout.addWidget(self.save_button)
        
        center_layout.addLayout(effects_layout)
        main_layout.addWidget(center_panel)

    def load_image(self) -> None:
        """Open file dialog to load a single image."""
        file_names, _ = Widgets.QFileDialog.getOpenFileNames(
            self,
            "Select Images",
            "",
            SUPPORTED_FORMATS
        )
        
        if file_names:
            self.load_specific_image(file_names[0])
            
            # Add to batch list if multiple files selected
            if len(file_names) > 1:
                self.batch_files.extend(file_names[1:])
                self.update_batch_list()

    def load_specific_image(self, file_name: str, is_preview: bool = False) -> None:
        """Load and display a specific image.
        
        Args:
            file_name: Path to the image file
            is_preview: Whether this is a preview load
        """
        self.current_image = file_name
        pixmap = Gui.QPixmap(file_name)
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        
        # Enable all effect buttons
        for button in self.findChildren(Widgets.QPushButton):
            if button not in (self.process_batch_button, self.save_button):
                button.setEnabled(True)

    def load_batch_images(self) -> None:
        """Open file dialog to load multiple images."""
        file_names, _ = Widgets.QFileDialog.getOpenFileNames(
            self,
            "Select Images",
            "",
            SUPPORTED_FORMATS
        )
        
        if file_names:
            self.batch_files.extend(file_names)
            self.update_batch_list()

    def update_batch_list(self) -> None:
        """Update the batch list widget with current files."""
        self.batch_list.clear()
        for file in self.batch_files:
            self.batch_list.addItem(Path(file).name)
        
        self.process_batch_button.setEnabled(bool(self.batch_files))

    def preview_batch_image(self, item: Widgets.QListWidgetItem) -> None:
        """Preview the selected image from batch list.
        
        Args:
            item: Selected list widget item
        """
        selected_items = self.batch_list.selectedItems()
        if selected_items and item == selected_items[-1]:
            file_path = next(
                path for path in self.batch_files 
                if Path(path).name == item.text()
            )
            self.load_specific_image(file_path, is_preview=True)

    def process_image(self, effect_type: str) -> None:
        """Process the current image with the specified effect.
        
        Args:
            effect_type: Type of effect to apply
        """
        command = ImageProcessCommand(self, effect_type)
        self.undo_stack.push(command)
        self.batch_processor.add_effect(effect_type)
        self.save_button.setEnabled(True)
        self.process_batch_button.setEnabled(True)

    def process_image_internal(self, effect_type: str, command: Optional[ImageProcessCommand] = None) -> None:
        """Internal method to handle image processing.
        
        Args:
            effect_type: Type of effect to apply
            command: Associated undo command if any
        """
        if not self.current_image:
            return
            
        self.progress_bar.setVisible(True)
        
        temp_output = self.batch_processor.get_temp_path(self.current_image)
        
        self.processing_thread = ProcessingThread(self.current_image, effect_type, temp_output)
        self.processing_thread.progress.connect(self.update_progress)
        self.processing_thread.finished.connect(
            lambda path: self.processing_complete(path, command)
        )
        self.processing_thread.start()

    def process_batch(self) -> None:
        """Process all images in the batch with queued effects."""
        if not self.batch_files or not self.batch_processor.effects_queue:
            logging.info("No files or effects to process")
            return
            
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        total_operations = len(self.batch_files) * len(self.batch_processor.effects_queue)
        completed_operations = 0
        
        try:
            for file in self.batch_files:
                current_input = file
                
                for effect in self.batch_processor.effects_queue:
                    temp_output = self.batch_processor.get_temp_path(file)
                    thread = ProcessingThread(current_input, effect, temp_output)
                    thread.run()  # Run synchronously for batch processing
                    current_input = temp_output
                    
                    completed_operations += 1
                    progress = int((completed_operations / total_operations) * 100)
                    self.progress_bar.setValue(progress)
                    Widgets.QApplication.processEvents()
                
                self.batch_processor.processed_images[file] = current_input
            
            self.save_button.setEnabled(True)
            logging.info("Batch processing complete!")
            
        except Exception as e:
            logging.error(f"Error during batch processing: {e}")
        
        finally:
            self.progress_bar.setVisible(False)

    def save_current_image(self) -> None:
        """Save the currently processed image."""
        if not self.current_processed_image:
            return
            
        file_name, _ = Widgets.QFileDialog.getSaveFileName(
            self,
            "Save Image",
            str(Path(self.current_processed_image).name),
            SUPPORTED_FORMATS
        )
        
        if file_name:
            try:
                import shutil
                shutil.copy2(self.current_processed_image, file_name)
                logging.info(f"Saved current image to: {file_name}")
            except Exception as e:
                logging.error(f"Error saving file: {e}")

    def save_processed_images(self) -> None:
        """Save all processed images."""
        if not self.batch_processor.processed_images and not self.current_processed_image:
            logging.info("No processed images to save")
            return
            
        save_dir = Widgets.QFileDialog.getExistingDirectory(
            self,
            "Select Directory to Save Processed Images"
        )
        
        if save_dir:
            try:
                if self.current_processed_image:
                    output_name = f"processed_{Path(self.current_image).name}"
                    output_path = str(Path(save_dir) / output_name)
                    import shutil
                    shutil.copy2(self.current_processed_image, output_path)
                
                for original, processed in self.batch_processor.processed_images.items():
                    output_name = f"processed_{Path(original).name}"
                    output_path = str(Path(save_dir) / output_name)
                    shutil.copy2(processed, output_path)
                
                logging.info(f"Saved all processed images to: {save_dir}")
                
            except Exception as e:
                logging.error(f"Error saving files: {e}")

    def update_progress(self, value: int) -> None:
        """Update the progress bar.
        
        Args:
            value: Progress value (0-100)
        """
        self.progress_bar.setValue(value)

    def processing_complete(self, result_path: str, command: Optional[ImageProcessCommand] = None) -> None:
        """Handle completion of image processing.
        
        Args:
            result_path: Path to the processed image
            command: Associated undo command if any
        """
        logging.info(f"Processing complete. Result saved to: {result_path}")
        
        self.progress_bar.setVisible(False)
        
        if not Path(result_path).exists():
            logging.error(f"Error: Result file does not exist: {result_path}")
            return
        
        pixmap = Gui.QPixmap(result_path)
        if pixmap.isNull():
            logging.error(f"Error: Failed to load result image: {result_path}")
            return
        
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        
        self.current_processed_image = result_path
        
        if command:
            command.new_state = ImageState(result_path, command.effect_type)
            
        self.save_button.setEnabled(True)

    # ... (rest of the implementation) 