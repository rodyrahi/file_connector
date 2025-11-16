# D:/startup/file_connector/app.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from connect import PipelineConnector
from fastapi.middleware.cors import CORSMiddleware
import os
import inspect
import importlib.util

# Folder where your Python modules exist
MODULES_DIR = "D:/startup/file_connector/modules"  # change if needed

app = FastAPI(
    title="ML Pipeline Connector API",
    description="Dynamically chain Python files in an ML pipeline."
)

# Allow all CORS origins (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
#  MODELS
# -------------------------

class ModuleConfig(BaseModel):
    module_name: str
    func_name: str
    params: Optional[Dict[str, Any]] = None

class PipelineRequest(BaseModel):
    modules: List[ModuleConfig]

# -------------------------
#  HEALTH CHECK
# -------------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# -------------------------
#  RUN PIPELINE
# -------------------------

@app.post("/pipeline/run")
async def run_pipeline(request: PipelineRequest):
    if not request.modules:
        raise HTTPException(status_code=400, detail="At least one module must be provided")
    
    try:
        # Prepare module info for PipelineConnector
        modules = [
            (m.module_name, m.func_name, m.params)
            for m in request.modules
        ]
        connector = PipelineConnector(modules)
        result = connector.execute()
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

# -------------------------
#  DISCOVER MODULES & FUNCTIONS
# -------------------------

def discover_python_files():
    """Return all python files inside MODULES_DIR."""
    if not os.path.exists(MODULES_DIR):
        return []
    return [f for f in os.listdir(MODULES_DIR) if f.endswith(".py") and f != "__init__.py"]

def load_module_functions(filepath: str):
    """Load a module and return all functions defined inside it."""
    module_name = os.path.splitext(os.path.basename(filepath))[0]

    spec = importlib.util.spec_from_file_location(module_name, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    funcs = [
        name for name, obj in inspect.getmembers(module, inspect.isfunction)
        if obj.__module__ == module_name
    ]
    return funcs

@app.get("/pipeline/discover")
async def discover_pipeline_modules():
    try:
        result = {}
        for file in discover_python_files():
            full_path = os.path.join(MODULES_DIR, file)
            result[file] = load_module_functions(full_path)
        return {"status": "success", "modules": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Discovery error: {str(e)}")

# -------------------------
#  RUN SERVER
# -------------------------

# Only run Uvicorn server if executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
