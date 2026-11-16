from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Terra Spectra Backend")

# Frontend (React) theke request allow korar jonno CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development-er jonno sob origin allow kora holo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Terra Spectra Backend API!"}

@app.get("/api/status")
def get_status():
    return {"status": "Active", "model": "Double Machine Learning Pipeline Ready"}