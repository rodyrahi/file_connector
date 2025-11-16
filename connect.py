import importlib
import sys
import os
from prefect import flow, task, get_run_logger
from typing import Optional, Dict, Any, List, Tuple

# Add modules folder to sys.path
MODULES_DIR = "D:/startup/file_connector/modules"
if MODULES_DIR not in sys.path:
    sys.path.append(MODULES_DIR)

@task(retries=2, retry_delay_seconds=5)
def run_module(module_name: str, func_name: str, input_data: Any = None, 
               params: Optional[Dict[str, Any]] = None):
    logger = get_run_logger()
    try:
        logger.info(f"Loading module: {module_name}.{func_name}")
        mod = importlib.import_module(module_name)  # now it will find modules in MODULES_DIR
        if not hasattr(mod, func_name):
            raise AttributeError(f"Function '{func_name}' not found in '{module_name}'")
        func = getattr(mod, func_name)
        # Call function with input_data and params if provided
        if input_data is not None and params is not None:
            output = func(input_data, params)
        elif input_data is not None:
            output = func(input_data)
        elif params is not None:
            output = func(params)
        else:
            output = func()
        logger.info(f"Module {module_name}.{func_name} executed")
        return output
    except (ImportError, AttributeError) as e:
        logger.error(f"Module error: {e}")
        raise

class PipelineConnector:
    def __init__(self, modules: List[Tuple[str, str, Optional[Dict[str, Any]]]]):
        """
        Initialize pipeline with a list of (module_name, func_name, params).
        First module is the start file (producer); others are consumers.
        """
        self.modules = modules
        self.logger = None

    @flow(name="Dynamic ML Pipeline")
    def run_pipeline(self):
        """Run the pipeline: chain modules in sequence."""
        self.logger = get_run_logger()
        self.logger.info("Starting ML pipeline...")
        current_input = None
        for i, (module_name, func_name, params) in enumerate(self.modules):
            self.logger.info(f"Executing module {i+1}/{len(self.modules)}: {module_name}.{func_name}")
            current_input = run_module(module_name, func_name, current_input, params)
        self.logger.info("Pipeline completed")
        return current_input

    def execute(self):
        """Execute the pipeline and return result."""
        return self.run_pipeline()
