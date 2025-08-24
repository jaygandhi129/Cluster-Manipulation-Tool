# Contributing to Cluster Manipulation Tool

Thank you for your interest in contributing to the Cluster Manipulation Tool! We welcome contributions from everyone.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

### Our Standards

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment
4. Create a branch for your changes
5. Make your changes
6. Test your changes
7. Submit a pull request

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** to demonstrate the steps
- **Describe the behavior you observed** and what behavior you expected
- **Include screenshots** if they help explain the problem
- **Include your environment details** (OS, Python version, browser, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description** of the suggested enhancement
- **Provide specific examples** to demonstrate the steps
- **Describe the current behavior** and explain what behavior you expected
- **Explain why this enhancement would be useful**

### Your First Code Contribution

Unsure where to begin contributing? You can start by looking through these issues:

- `good first issue` - issues that should only require a few lines of code
- `help wanted` - issues that should be a bit more involved than beginner issues

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- Virtual environment tool (venv, conda, etc.)

### Setup Steps

1. **Clone your fork:**
```bash
git clone https://github.com/jaygandhi129/Cluster-Manipulation-Tool.git
cd Cluster-Manipulation-Tool
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Install development dependencies:**
```bash
pip install pytest black flake8 mypy
```

5. **Run the application:**
```bash
streamlit run app/main.py
```

### Project Structure

```
Cluster-Manipulation-Tool/
├── app/
│   ├── main.py              # Main Streamlit application
│   ├── cluster_manager.py   # Core logic
│   ├── messages.py          # UI messages
│   └── styles.py            # CSS styles
├── data/
│   └── sample_data.json     # Sample data
├── tests/
│   └── test_*.py            # Test files
└── docs/
    └── *.md                 # Documentation
```

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 88 characters (Black default)
- **Imports**: Use absolute imports where possible
- **Docstrings**: Use Google style docstrings
- **Type hints**: Use type hints for function parameters and return values

### Code Formatting

We use [Black](https://black.readthedocs.io/) for code formatting:

```bash
black app/ tests/
```

### Linting

We use [flake8](https://flake8.pycqa.org/) for linting:

```bash
flake8 app/ tests/
```

### Type Checking

We use [mypy](https://mypy.readthedocs.io/) for type checking:

```bash
mypy app/
```

### Example Code Style

```python
from typing import Dict, List, Optional


class ExampleClass:
    """Example class demonstrating code style.
    
    Args:
        data: Input data dictionary
        options: Optional configuration options
    """
    
    def __init__(self, data: Dict[str, any], options: Optional[Dict] = None):
        self.data = data
        self.options = options or {}
    
    def process_data(self, filter_term: str = "") -> List[Dict]:
        """Process the input data with optional filtering.
        
        Args:
            filter_term: Optional string to filter results
            
        Returns:
            List of processed data dictionaries
            
        Raises:
            ValueError: If data is invalid
        """
        if not self.data:
            raise ValueError("No data provided")
            
        # Implementation here
        return []
```

## Testing

### Running Tests

Run the test suite:

```bash
python -m pytest tests/
```

Run tests with coverage:

```bash
python -m pytest tests/ --cov=app/ --cov-report=html
```

### Writing Tests

- Write tests for all new functionality
- Follow the naming convention: `test_<function_name>`
- Use descriptive test names that explain what is being tested
- Include both positive and negative test cases
- Mock external dependencies

Example test:

```python
import pytest
from app.cluster_manager import ClusterManager


class TestClusterManager:
    def test_load_valid_data_success(self):
        """Test loading valid cluster data succeeds."""
        manager = ClusterManager()
        valid_data = {
            "clusters": [
                {
                    "id": "1",
                    "name": "Test Cluster",
                    "members": [{"id": "m1", "name": "Member 1"}],
                    "relationships": []
                }
            ]
        }
        
        success, message = manager.load_data(valid_data)
        
        assert success is True
        assert message == "data_loaded"
        assert len(manager.data["clusters"]) == 1
```

## Pull Request Process

1. **Create a branch** from `main` for your work:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards

3. **Add or update tests** for your changes

4. **Run the test suite** and ensure all tests pass

5. **Run linting and formatting**:
   ```bash
   black app/ tests/
   flake8 app/ tests/
   mypy app/
   ```

6. **Update documentation** if needed

7. **Commit your changes** with a clear commit message:
   ```bash
   git commit -m "Add feature: brief description of changes"
   ```

8. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

9. **Create a Pull Request** on GitHub

### Pull Request Guidelines

- **Use a clear title** that describes what the PR does
- **Fill out the PR template** completely
- **Reference any related issues** using keywords like "Fixes #123"
- **Include screenshots** for UI changes
- **Keep PRs focused** - one feature or fix per PR
- **Update the changelog** if your change affects users

### PR Review Process

1. All PRs must be reviewed by at least one maintainer
2. All tests must pass
3. Code coverage should not decrease significantly
4. Documentation must be updated for new features
5. Breaking changes require discussion and migration guide

## Issue Guidelines

### Issue Templates

Please use the appropriate issue template:

- **Bug Report**: For reporting bugs
- **Feature Request**: For suggesting new features
- **Documentation**: For documentation improvements
- **Question**: For asking questions about the project

### Issue Labels

We use the following labels to categorize issues:

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `question`: Further information is requested
- `wontfix`: This will not be worked on

## Recognition

Contributors will be recognized in:

- The project's README
- Release notes for significant contributions
- A dedicated CONTRIBUTORS.md file

## Getting Help

If you need help with contributing:

- Check the [README](README.md) for basic information
- Look through existing [Issues](https://github.com/jaygandhi129/Cluster-Manipulation-Tool/issues)
- Join our [Discussions](https://github.com/jaygandhi129/Cluster-Manipulation-Tool/discussions)
- Contact the maintainers

Thank you for contributing to the Cluster Manipulation Tool! 🎉
