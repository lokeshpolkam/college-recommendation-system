from setuptools import setup, find_packages

setup(
    name="college-recommendation-system",
    version="1.0.0",
    author="Lokesh Polkam",
    description="AI-powered college recommendation system for JEE Main students",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "fuzzywuzzy>=0.18.0",
        "python-Levenshtein>=0.12.0",
        "openpyxl>=3.0.0",
    ],
)
