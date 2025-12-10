##Part of the cleanup process that allows Dell-Ent ZTP to use the config_db.json files on factory new switches
##It removes 3 keys from the files that can cause conflict: {"hwsku", "mac", "platform"}
##Uses folder name backup_configdbs
import os
import json

# Directory containing the JSON files
folder_path = "backup_configdbs"

# Keys to remove
keys_to_remove = {"hwsku", "mac", "platform"}

# Iterate over all files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)
        
        # Read the JSON file
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Skipping invalid JSON file: {filename} - {e}")
                continue

        # Check if DEVICE_METADATA and localhost exist
        if "DEVICE_METADATA" in data and "localhost" in data["DEVICE_METADATA"]:
            localhost = data["DEVICE_METADATA"]["localhost"]
            # Remove specified keys if they exist
            for key in keys_to_remove:
                localhost.pop(key, None)  # pop with default to avoid KeyError

        # Write the modified data back to the file
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

        print(f"Processed: {filename}")

print("All files processed.")