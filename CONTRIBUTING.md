# Contributing to FastAPI ML Application

Thank you for your interest in contributing! This guide will help you get started.

## Getting Started

### 1. Fork and Clone
```bash
git clone https://github.com/your-username/project-name.git
cd project-name
```

### 2. Set Up Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Start Services
```bash
docker-compose up -d
uvicorn app.main:app --reload
```

## Making Changes

### Branch Naming
- `feature/add-new-endpoint` - New features
- `bugfix/fix-auth-issue` - Bug fixes
- `docs/update-readme` - Documentation

### Development Process
1. Create a new branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Write tests for your changes
4. Run tests: `pytest tests/`
5. Commit: `git commit -m "feat: add new feature"`
6. Push: `git push origin feature/your-feature`
7. Open a Pull Request

## Code Style

### Format Your Code
```bash
black app/ tests/
isort app/ tests/
```

### Check Code Quality
```bash
flake8 app/ tests/
```

## Writing Tests

Place tests in the `tests/` directory:
```python
def test_your_feature(test_client):
    response = test_client.get("/your-endpoint")
    assert response.status_code == 200
```

Run tests:
```bash
pytest tests/ -v
```

## Commit Messages

Use clear, descriptive commit messages:
- `feat: add user registration endpoint`
- `fix: resolve token expiration bug`
- `docs: update API documentation`
- `test: add tests for auth service`

## Pull Request Guidelines

### Before Submitting
- [ ] Tests pass locally
- [ ] Code is formatted (black, isort)
- [ ] Added tests for new features
- [ ] Updated documentation if needed

### PR Description Should Include
- What changes were made
- Why these changes are needed
- Related issue numbers (if any)
- Screenshots (for UI changes)

## Need Help?

- Open an issue for questions
- Check existing issues and PRs
- Reach out to maintainers

## Code of Conduct

- Be respectful and constructive
- Welcome newcomers
- Focus on what's best for the project

Thank you for contributing! 🚀