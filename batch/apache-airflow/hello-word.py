import json

# Define the paths to your input and output JSON files
input_file_path = 'data.json'
output_file_path = 'data2.json'

# Read data from the input JSON file
with open(input_file_path, 'r') as input_file:
    data = json.load(input_file)

# Modify the data if needed
# For example, you can add, remove, or manipulate keys and values in the 'data' dictionary.

# Write the modified data to the output JSON file
with open(output_file_path, 'w') as output_file:
    json.dump(data, output_file, indent=4)  # indent argument for pretty formatting
