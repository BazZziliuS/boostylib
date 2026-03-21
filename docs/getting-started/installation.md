# Installation

## Requirements

- Python 3.14 or later
- Works on Linux, macOS, and Windows

## Install with pip

```bash
pip install boostylib
```

## Install with uv

```bash
uv add boostylib
```

## Development Installation

```bash
git clone https://github.com/BazZziliuS/boostylib.git
cd boostylib
uv sync --extra dev
```

## Verify Installation

```python
import boostylib
print(boostylib.__version__)
```

## Optional Dependencies

| Extra | Command | What it adds |
|---|---|---|
| `dev` | `uv sync --extra dev` | pytest, ruff, mypy, respx |
| `docs` | `uv sync --extra docs` | mkdocs-material, mkdocstrings |
