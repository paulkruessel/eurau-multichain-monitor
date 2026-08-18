# EURAU-Multichain-Monitor
This is a learning project aimed to learn and understand the EURAU API made by AllUnity.

## Commands
To start the backend locally:

1. `cd backend`
2. `python -m venv .venv`
3. `source .venv/bin/activate` (or `.venv\Scripts\Activate.ps1` on Windows PowerShell)
4. `python -m pip install --upgrade pip`
5. `python -m pip install -e .`
6. `python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000`

To start the frontend type `npm start` from the eurau-client folder.
