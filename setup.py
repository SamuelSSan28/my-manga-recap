from setuptools import setup, find_packages

setup(
    name="my-manga-recap",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pytesseract",
        "Pillow",
        "transformers",
        "torch",
        "moviepy",
        "pyttsx3",
        "python-dotenv",
        "numpy",
        "requests",
        "beautifulsoup4",
        "selenium",
        "webdriver-manager",
        "openai",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ]
    },
    entry_points={
        "console_scripts": [
            "manga-recap=src.main:main",
            "manga-recap-cli=src.interactive_cli:main",
        ]
    },
    author="Samuel",
    description="Sistema para converter mangás em vídeos narrados com IA",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
) 