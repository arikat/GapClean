# gapclean/setup.py
from setuptools import setup, find_packages

setup(
    name="gapclean",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "tqdm",
        "numpy",
    ],
    entry_points={
        "console_scripts": [
            "gapclean=gapclean.gapclean:main"
        ]
    },
    author="Aarya Venkat, PhD",
    description="GapClean: Clean up large gappy multiple sequence alignments.",
    long_description="GapClean is a tool for removing columns with too many gaps from large sequence alignments to improve visual clarity and comprehension.",
    url="https://github.com/arikat/GapClean",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
