# Publishing Guide

This document explains how to publish the `wavemaker-agent-framework` to PyPI.

## Prerequisites

### 1. PyPI Account Setup

1. Create accounts on:
   - [Test PyPI](https://test.pypi.org/account/register/) (for testing)
   - [PyPI](https://pypi.org/account/register/) (for production)

2. Enable 2FA on both accounts (required for API tokens)

3. Create API tokens:
   - Go to Account Settings → API tokens
   - Create token with scope "Entire account" or specific to this project
   - Save tokens securely

### 2. GitHub Secrets Setup

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

- `TEST_PYPI_API_TOKEN` - Your Test PyPI API token
- `PYPI_API_TOKEN` - Your PyPI API token

## Publishing Methods

### Method 1: Automated Publishing (Recommended)

#### Via GitHub Release

1. Create and push a version tag:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

2. Create a GitHub Release:
   - Go to GitHub → Releases → "Create a new release"
   - Select the tag you just pushed
   - Add release notes
   - Click "Publish release"

3. The GitHub Action will automatically:
   - Build the package
   - Run tests
   - Publish to PyPI

#### Via Manual Workflow Dispatch

1. Go to GitHub → Actions → "Publish to PyPI"
2. Click "Run workflow"
3. Select:
   - Branch: `main`
   - PyPI repository: `pypi` or `testpypi`
4. Click "Run workflow"

### Method 2: Manual Publishing

#### Build the Package

```bash
# Install build tools
pip install build twine

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build the package
python -m build
```

This creates:
- `dist/wavemaker_agent_framework-0.1.0-py3-none-any.whl` (wheel)
- `dist/wavemaker_agent_framework-0.1.0.tar.gz` (source)

#### Check the Package

```bash
# Verify package structure
twine check dist/*

# Install locally to test
pip install dist/wavemaker_agent_framework-0.1.0-py3-none-any.whl
```

#### Publish to Test PyPI (Testing)

```bash
# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ wavemaker-agent-framework
```

#### Publish to PyPI (Production)

```bash
# Upload to PyPI
twine upload dist/*

# Verify installation
pip install wavemaker-agent-framework
```

## Version Management

### Semantic Versioning

We use [Semantic Versioning](https://semver.org/):

- **MAJOR** version (1.0.0): Incompatible API changes
- **MINOR** version (0.1.0): Backwards-compatible new features
- **PATCH** version (0.0.1): Backwards-compatible bug fixes

### Updating Version

1. Edit `pyproject.toml`:
   ```toml
   [project]
   version = "0.2.0"  # Update this
   ```

2. Commit the change:
   ```bash
   git add pyproject.toml
   git commit -m "chore: Bump version to 0.2.0"
   git push
   ```

3. Create and push tag:
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

4. Create GitHub Release (triggers auto-publish)

## Private PyPI Setup (Alternative)

If you want to use a private PyPI server instead of public PyPI:

### Option 1: PyPI Cloud (Paid)

1. Sign up at [PyPI Cloud](https://pypi.org/help/#pypiocloud)
2. Configure repository:
   ```bash
   # In ~/.pypirc
   [distutils]
   index-servers =
       private-pypi

   [private-pypi]
   repository = https://your-private-pypi.com/simple/
   username = __token__
   password = your-token-here
   ```

3. Publish:
   ```bash
   twine upload --repository private-pypi dist/*
   ```

### Option 2: Self-Hosted PyPI Server

Using [pypiserver](https://github.com/pypiserver/pypiserver):

1. Install and run:
   ```bash
   pip install pypiserver
   pypi-server -p 8080 ./packages
   ```

2. Configure clients:
   ```bash
   # Install from private server
   pip install --index-url http://localhost:8080/simple/ wavemaker-agent-framework
   ```

### Option 3: Artifact Repository (JFrog, Nexus, AWS CodeArtifact)

Contact DevOps for setup instructions.

## Installation from Private PyPI

### For Developers

```bash
# Add to pip.conf or pip.ini
[global]
index-url = https://your-private-pypi.com/simple/
extra-index-url = https://pypi.org/simple/
```

### In requirements.txt

```txt
# Private package
--index-url https://your-private-pypi.com/simple/
--extra-index-url https://pypi.org/simple/

wavemaker-agent-framework==0.1.0
```

### In pyproject.toml

```toml
[[tool.uv.index]]
name = "private"
url = "https://your-private-pypi.com/simple/"
```

## Troubleshooting

### Build Fails

```bash
# Check for syntax errors
python -m py_compile src/**/*.py

# Verify pyproject.toml
python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"
```

### Upload Fails

```bash
# Check package
twine check dist/*

# Verify credentials
twine upload --repository testpypi --verbose dist/*
```

### Version Already Exists

PyPI doesn't allow re-uploading the same version. You must:
1. Increment the version number
2. Build and upload again

### Import Fails After Install

```bash
# Check package structure
pip show wavemaker-agent-framework

# Verify installation
python -c "from wavemaker_agent_framework.core import AgentConfig; print('Success')"
```

## Release Checklist

Before publishing a new version:

- [ ] All tests passing (`pytest`)
- [ ] Coverage ≥ 85% (`pytest --cov`)
- [ ] Code formatted (`black src tests`)
- [ ] Linting clean (`ruff check src tests`)
- [ ] Version updated in `pyproject.toml`
- [ ] CHANGELOG.md updated
- [ ] README.md updated (if needed)
- [ ] Git tag created
- [ ] GitHub Release created
- [ ] Verify installation from PyPI

## Support

For publishing issues:
- Email: bobby@nolimitz.com
- GitHub Issues: https://github.com/NoLimitzLab/wavemaker-agent-framework/issues

---

**Last Updated:** 2026-01-23
