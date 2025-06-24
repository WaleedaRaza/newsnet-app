#!/usr/bin/env python3

from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    print("Starting minimal test server on port 8080...")
    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="info") 