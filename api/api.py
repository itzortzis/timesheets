from fastapi import FastAPI
from pydantic import BaseModel
import csv
import uuid

app = FastAPI()

class InputData(BaseModel):
    text: str
    number: int

@app.post("/generate")
def generate_csv(data: InputData):
    filename = f"{uuid.uuid4()}.csv"

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "number"])
        writer.writerow([data.text, data.number])

    return {"status": "success", "file": filename}