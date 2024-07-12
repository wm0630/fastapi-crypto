from setuptools import find_packages, setup

setup(
    name="cryptogpt",
    version="0.1.0",
    description="A FastAPI project",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "databases",
        "pydantic",
        "alembic",
        "python-dotenv",
        "requests",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-asyncio",
            "httpx",
            "black",
            "flake8",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Framework :: FastAPI",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'cryptogpt=app.main:app',
        ],
    },
)
