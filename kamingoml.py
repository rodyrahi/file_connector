import json
import inspect
import os

test = ""

def save(data, file_name=None):
    global test
    test = data

   
    if file_name is None:
       
        caller_frame = inspect.stack()[1]
        caller_file = caller_frame.filename
        
        file_name = "data.json"

    data = { "filename" : caller_file ,"data": data}

    # Save data to JSON
    with open(file_name, "w") as f:
        json.dump(data, f)
