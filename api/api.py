from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
from core import timesheets

from fastapi.responses import FileResponse

app = FastAPI()


    
class Info(BaseModel):
    hours: int
    month: int
    holidays: list[int]
    period_start: int
    period_end: int
    wps_names: list[str]
    wps_weights: list[int]
    year: int
    
class Filename(BaseModel):
    filepath: str




@app.post("/process")
def process_data_post(data: Info) -> Dict[str, Any]:
    
    
    
    hours = data.hours
    month = data.month
    holidays = data.holidays
    period_start = data.period_start
    period_end = data.period_end
    wps_names = data.wps_names
    wps_weights = data.wps_weights
    year = data.year
    
    scaled_wps_weights = [weight / 100 for weight in wps_weights]

    

    t = timesheets(
        period_start=int(period_start),
        period_end=int(period_end),
        hours=int(hours),
        exception=holidays,
        wps=wps_names,
        wps_weights=scaled_wps_weights,
        month=int(month),
        year=int(year)
    )
    
    
    return {
        "status": "success" if t.r == 0 else "failure",
        "message": "Data processed successfully." if t.r == 0 else t.error,
        "filepath": t.filepath if t.r == 0 else ""
    }
    
    
@app.post("/download")
def download_data(data: Filename) -> Dict[str, Any]:
    
    return FileResponse(
        path=data.filepath,
        media_type='text/csv',
        filename=f"timsheet.csv", 
    )