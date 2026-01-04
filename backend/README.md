# 🚀 Quick Start Backend

## Easy Way (Recommended)

```bash
cd backend
python run.py
```

## Alternative Ways

### Option 1: With module
```bash
cd backend
python -m app.main
```

### Option 2: With PYTHONPATH (PowerShell)
```bash
cd backend
$env:PYTHONPATH="$pwd"
python app/main.py
```

### Option 3: With PYTHONPATH (Bash)
```bash
cd backend
export PYTHONPATH=$(pwd)
python app/main.py
```

## Access

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/system/status
