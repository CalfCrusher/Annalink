from setuptools import setup, find_packages

setup(
    name="annalink",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "ecdsa==0.18.0",
        "base58==2.1.1",
        "PyYAML==6.0.1",
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
    ],
    entry_points={
        "console_scripts": [
            "annalink-cli=annalink.api.cli:main",
        ],
    },
    author="Christopher",
    description="A custom blockchain implementation",
    python_requires=">=3.8",
)