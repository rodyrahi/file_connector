# import json
# import inspect
# import os

# test = ""

# def save(data, file_name=None):
#     global test
#     test = data

#     # Get caller file if filename not provided
#     caller_frame = inspect.stack()[1]
#     caller_file = caller_frame.filename
#     if file_name is None:
#         file_name = "out.json"

#     # Attempt to get variable name from caller's code
#     var_name = "unknown"
#     try:
#         # Get the line that called save()
#         caller_line = caller_frame.code_context[0].strip()
#         # Extract the part inside save(...)
#         start = caller_line.find("save(") + len("save(")
#         end = caller_line.rfind(")")
#         var_name = caller_line[start:end].strip()
#     except:
#         pass

#     # Prepare data to save
#     json_data = {
#         "filename": os.path.basename(caller_file),
#         "variable_name": var_name,
#         "data": data
        
#     }

#     # Save to JSON
#     with open(file_name, "w") as f:
#         json.dump(json_data, f, indent=4)




import json
import subprocess
import sys
import os


def runfile(json_path , folder):

    # print(f"Running file with config: {json_path}")
    # # Read the JSON file
    with open('config.json', "r") as f:
        config = json.load(f)

    # run_file = config.get("run_file")

    config["output_folder"] = folder

    with open('config.json', "w") as f:
        json.dump(config, f, indent=4)
    

    run_file = json_path  
    if not run_file or not os.path.exists(run_file):
        print(f"Error: run_file '{run_file}' does not exist.")
        return

    # Run the Python file in a subprocess
    result = subprocess.run([sys.executable, run_file], capture_output=True, text=True)

    # Check for errors
    if result.returncode != 0:
        print(f"Error running {run_file}:")
        print(result.stderr)
        return

    print(f"Successfully ran {run_file}")

def savefile(filename, data):
    # Read config
    with open("./config.json", "r") as f:
        config = json.load(f)

    output_folder = config.get("output_folder", "output")  # Default to "output" if not specified

    # Create folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Save the data
    with open(f"{output_folder}/{filename}", "w") as f:
        f.write(data)

    print(f"Saved file: {output_folder}/{filename}")

if __name__ == "__main__":
    runfile("config.json")
    



