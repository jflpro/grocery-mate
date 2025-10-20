# PowerShell script to run backend + frontend together

# Run backend
Write-Host "Starting backend..."
cd ..\backend
pip install -r requirements.txt
uvicorn main:app --reload

# Run frontend (in a separate terminal or after backend is ready)
Write-Host "Starting frontend..."
cd ..\frontend
npm install
npm run dev
