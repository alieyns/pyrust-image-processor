# PyRust Image Processor

A high-performance image processing application that demonstrates Python-Rust integration, combining the ease of Python's GUI capabilities with Rust's processing speed.

## Features

- 🚀 High-performance image processing powered by Rust
- 🖼️ User-friendly Python GUI built with PySide6
- 🔄 Seamless Python-Rust integration via PyO3
- 📦 Batch processing capabilities

## Prerequisites

- Python 3.8 or higher
- Rust (latest stable version)
- Cargo (comes with Rust)
- A C compiler (for Windows: MSVC, for Unix: gcc)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/alieyns/pyrust-image-processor.git
   cd pyrust-image-processor
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On Unix or MacOS
   source venv/bin/activate
   ```

3. Install the package:
   ```bash
   pip install -e .
   ```

## Usage

- Add simple filters to an image.
- Batch process images.
- Save the processed images.
- Study the code to learn how to integrate Rust and Python.
- Build a simple GUI using PySide6.
- Benchmark the performance of the image processing.

## Development

To set up the development environment:

1. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

2. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- PyO3 team for making Python-Rust integration possible
- PySide6 for the GUI framework

## Author

**Abbey Mugisha**
- GitHub: [@alieyns](https://github.com/alieyns)
