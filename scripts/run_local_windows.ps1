# run_local_windows.ps1
# Setup and run DocuShield AI on Windows

Write-Host "Starting DocuShield AI (Windows)..."

# 1. Create Python virtual environment if not exists
if (!(Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

# 2. Activate virtual environment
Write-Host "Activating virtual environment..."
. .\.venv\Scripts\Activate.ps1

# 3. Install backend dependencies
Write-Host "Installing backend dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# 4. Install frontend dependencies & build
Write-Host "Building frontend..."
cd frontend
npm install
npm run build
cd ..

# 5. Start backend server
Write-Host "Starting backend server..."
cd backend
python app.py
