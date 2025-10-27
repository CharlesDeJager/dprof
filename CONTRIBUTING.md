# Contributing to DView

Thank you for your interest in contributing to DView! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- Git

### Setting up Development Environment

1. **Fork and Clone**

   ```bash
   git clone https://github.com/yourusername/dview.git
   cd dview
   ```

2. **Run Setup Script**

   ```bash
   ./setup.sh
   ```

3. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📋 Development Workflow

### Backend Development

1. **Activate Virtual Environment**

   ```bash
   cd backend
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run Development Server**

   ```bash
   python run_server.py
   ```

4. **Run Tests** (when available)
   ```bash
   pytest tests/
   ```

### Frontend Development

1. **Install Dependencies**

   ```bash
   cd frontend
   npm install
   ```

2. **Start Development Server**

   ```bash
   npm start
   ```

3. **Run Tests** (when available)

   ```bash
   npm test
   ```

4. **Build for Production**
   ```bash
   npm run build
   ```

## 🎯 Code Style Guidelines

### Python (Backend)

- Follow **PEP 8** style guide
- Use **Black** for code formatting: `black .`
- Use **flake8** for linting: `flake8 .`
- Add type hints where appropriate
- Write docstrings for all functions and classes

Example:

```python
def profile_column(series: pd.Series, column_name: str, total_records: int) -> Dict[str, Any]:
    """
    Profile a single column with comprehensive statistics.

    Args:
        series: Pandas series to analyze
        column_name: Name of the column
        total_records: Total number of records in the dataset

    Returns:
        Dictionary containing profiling results
    """
    # Implementation here
```

### JavaScript/React (Frontend)

- Use **Prettier** for formatting
- Follow **ESLint** rules
- Use functional components with hooks
- Use TypeScript-style JSDoc for complex functions

Example:

```javascript
/**
 * Handle data source selection and validation
 * @param {Object} sourceData - The selected data source information
 * @param {string} sourceData.type - Type of data source ('file' or 'database')
 * @param {string} sourceData.sessionId - Unique session identifier
 */
const handleDataSourceSelected = (sourceData) => {
  // Implementation here
};
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment Information**

   - Operating System
   - Python version
   - Node.js version
   - Browser (for frontend issues)

2. **Steps to Reproduce**

   - Detailed steps to reproduce the issue
   - Sample data if applicable
   - Expected vs actual behavior

3. **Error Messages**

   - Full error messages and stack traces
   - Console logs if applicable

4. **Screenshots** (if applicable)

## ✨ Feature Requests

For new features:

1. **Check Existing Issues** first
2. **Describe the Problem** the feature would solve
3. **Propose a Solution** with implementation details
4. **Consider Breaking Changes** and backward compatibility

## 🔄 Pull Request Process

### Before Submitting

1. **Test Your Changes**

   - Ensure all existing tests pass
   - Add tests for new functionality
   - Test manually in different browsers

2. **Update Documentation**

   - Update README.md if needed
   - Add/update code comments
   - Update CHANGELOG.md

3. **Code Quality**
   - Run linting tools
   - Format code consistently
   - Remove debugging code

### Pull Request Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Commit messages are descriptive
- [ ] Branch is up to date with main

### Commit Message Format

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:

```
feat(profiler): add pattern detection for email addresses
fix(frontend): resolve table selection issue on mobile devices
docs(readme): update installation instructions
```

## 🏗️ Architecture Guidelines

### Adding New Data Sources

1. **Create Connector**: Add new connector in `backend/app/connectors/`
2. **Update API**: Add endpoints in `main.py`
3. **Frontend Support**: Add UI components for new source type
4. **Documentation**: Update README with new capabilities

### Adding New Export Formats

1. **Backend Exporter**: Add to `backend/app/exporters/`
2. **API Endpoint**: Update export endpoint
3. **Frontend UI**: Add export button/option
4. **Tests**: Add tests for new format

### Performance Considerations

- **Memory Usage**: Consider memory footprint for large datasets
- **Parallelization**: Ensure thread safety
- **Database Connections**: Proper connection pooling
- **Progress Tracking**: Provide user feedback

## 🧪 Testing Guidelines

### Backend Tests

- Unit tests for individual functions
- Integration tests for API endpoints
- Mock external dependencies (databases, files)
- Test error conditions and edge cases

### Frontend Tests

- Component unit tests with React Testing Library
- Integration tests for user workflows
- Mock API calls
- Test responsive design

## 📚 Documentation

### Code Documentation

- Comprehensive docstrings/comments
- Type hints and JSDoc
- README updates for new features
- API documentation

### User Documentation

- Clear setup instructions
- Usage examples with screenshots
- Troubleshooting guides
- Configuration options

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Provide constructive feedback
- Focus on technical merit

### Getting Help

- Check existing documentation
- Search existing issues
- Ask questions in discussions
- Be specific about problems

## 🎉 Recognition

Contributors will be recognized in:

- README.md contributors section
- Release notes for significant contributions
- GitHub contributors page

## 📞 Contact

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Security**: security@dview.com

Thank you for contributing to DView! 🚀
