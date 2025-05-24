# Python Virtual Environment Setup (.venv)

This project now uses a local Python virtual environment for development and testing. Follow these steps to set up your environment on Windows:

## 1. Create a Virtual Environment

Open a terminal in the project root and run:

```
python -m venv .venv
```

## 2. Activate the Virtual Environment

In PowerShell (default on Windows):

```
.venv\Scripts\Activate.ps1
```

In Command Prompt:

```
.venv\Scripts\activate.bat
```

## 3. Install Dependencies

```
pip install -r requirements.txt
```

Or, if you use `pyproject.toml`:

```
pip install .
```

## 4. Select Interpreter in VS Code

- Press `Ctrl+Shift+P` and select `Python: Select Interpreter`.
- Choose the `.venv` interpreter from the list.

## 5. Deactivate When Done

```
deactivate
```

---

- The `.venv/` directory is git-ignored.
- Remove any Codespaces or devcontainer configuration if present.
- For environment variables, continue to use the `.env` file as described in the README.
