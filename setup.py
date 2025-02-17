from setuptools import setup, find_packages

setup(
    name="maverick",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.26.0",
        "pandas>=2.2.0",
        "pytest>=7.4.0",
        "pytest-cov>=4.1.0",
        "tqdm>=4.66.0",
        "treys>=0.1.8",
        "pokerkit>=0.1.0",
        "scikit-learn>=1.4.0",
        "torch>=2.2.0",
        "matplotlib>=3.8.0"
    ],
    python_requires=">=3.8",
) 