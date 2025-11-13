"""
Setup script for GRCM - Grounded Resonant Consciousness Module
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README
readme_path = Path(__file__).parent / "README_GRCM.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

setup(
    name="grcm",
    version="0.1.0",
    author="GRCM Research Team",
    author_email="grcm-team@example.com",
    description="Grounded Resonant Consciousness Module - Production PyTorch implementation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/newdew",
    packages=find_packages(include=['grcm', 'grcm.*']),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "torch>=2.0.0",
        "numpy>=1.24.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-benchmark>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.4.0",
        ],
        "optimization": [
            "onnx>=1.14.0",
            "onnxruntime>=1.15.0",
        ],
        "training": [
            "mlflow>=2.7.0",
            "tensorboard>=2.13.0",
        ],
        "ui": [
            "gradio>=3.40.0",
            "matplotlib>=3.7.0",
            "plotly>=5.15.0",
        ],
        "deployment": [
            "bentoml>=1.1.0",
            "fastapi>=0.100.0",
            "uvicorn>=0.23.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
            "myst-parser>=2.0.0",
        ],
        "full": [
            "transformers>=4.30.0",
            "Pillow>=10.0.0",
            "librosa>=0.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "grcm-demo=examples.basic_usage:main",
        ],
    },
    include_package_data=True,
    package_data={
        "grcm": ["py.typed"],
    },
    zip_safe=False,
    keywords="consciousness ai machine-learning pytorch resonance integrated-information",
    project_urls={
        "Bug Reports": "https://github.com/your-org/newdew/issues",
        "Source": "https://github.com/your-org/newdew",
        "Documentation": "https://github.com/your-org/newdew/docs",
    },
)
