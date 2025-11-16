

import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from typing import Optional, Dict, Any, List
app = FastAPI(
    title="ML Pipeline Connector API",
    description="Dynamically chain Python files in an ML pipeline."
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ModuleConfig(BaseModel):
    file_name: str
    outputfolder: str
    outputfile: str

class PipelineRequest(BaseModel):
    modules: List[ModuleConfig]

@app.post("/runflow")
async def run_pipeline(request: PipelineRequest):
    if not request.modules:
        raise HTTPException(status_code=400, detail="At least one module must be provided")
    
    try:
        results = []
        for module in request.modules:
            
            print(module)
            
            json_path = module.file_name
            # Call the runfile function from kamingoml.py
            from kamingoml import runfile
            runfile(json_path , module.outputfolder)
            results.append(f"Executed {json_path}")
        return {"status": "success", "results": results}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("new_app:app", host="0.0.0.0", port=8000, reload=True)