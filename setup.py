"""Setup configuration for PyRust Image Processor.

A demonstration of accelerating Python applications with Rust extensions,
showcasing high-performance image processing in a GUI application.
"""

from setuptools import setup, find_packages
from setuptools_rust import Binding, RustExtension

setup(
    name="pyrust_image_processor",
    version="0.1.0",
    description="Image Processing Tool demonstrating Python-Rust integration",
    long_description="""
    An image processing application that demonstrates how to accelerate
    Python applications using Rust. Features include:
    - High-performance image processing with Rust
    - Python GUI with PySide6
    - Seamless Python-Rust integration via PyO3
    - Batch processing capabilities
    """,
    author="Abbey Mugisha",
    packages=find_packages(),
    rust_extensions=[
        RustExtension(
            "image_processor_rust",
            binding=Binding.PyO3,
            debug=False
        )
    ],
    install_requires=[
        "PySide6>=6.0.0",
        "setuptools-rust>=1.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "isort>=5.0",
            "flake8>=4.0",
            "pre-commit>=2.0",
        ]
    },
    python_requires=">=3.8",
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Rust",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries :: Rust Extensions",
        "Topic :: Multimedia :: Graphics :: Graphics Processing",
        "Framework :: PyO3",
    ],
    keywords="rust, python, extension, image processing, performance, pyo3",
) 