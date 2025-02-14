# Contributing to Maverick

First off, thank you for considering contributing to Maverick! It's people like you that make Maverick such a great tool.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct:

- Use welcoming and inclusive language
- Be respectful of different viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps which reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include screenshots if relevant

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Provide specific examples to demonstrate the steps
* Describe the current behavior and explain which behavior you expected to see instead
* Explain why this enhancement would be useful

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code lints
6. Issue that pull request!

## Development Process

1. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and commit them:
```bash
git commit -m 'Add some feature'
```

3. Push to the branch:
```bash
git push origin feature/your-feature-name
```

4. Submit a pull request

### Python Style Guide

* Follow PEP 8 guidelines
* Use type hints for function arguments and return values
* Write docstrings for all public methods and functions
* Keep functions focused and under 50 lines where possible
* Use meaningful variable names

### Testing

* Write unit tests for all new code
* Ensure all tests pass before submitting PR
* Aim for at least 80% code coverage
* Include both positive and negative test cases

```bash
# Run tests
python -m pytest tests/

# Run tests with coverage
python -m pytest --cov=maverick tests/
```

### Documentation

* Update README.md with any new features
* Add docstrings to all new functions and classes
* Keep documentation up to date with code changes
* Include examples for new features

## Project Structure

When adding new features, please maintain the existing project structure:

```
maverick/
├── core/              # Core engine components
├── ai/               # AI and ML components
├── api/              # API interfaces
├── ui/               # User interface components
└── tests/            # Test suite
```

## Version Control Guidelines

* Keep commits atomic and focused
* Write clear commit messages
* Reference issues and pull requests in commits
* Rebase your branch before submitting PR

## Questions?

Feel free to open an issue with your question or contact the maintainers directly.

Thank you for your contributions! 🎉 