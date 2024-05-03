import json
import csv
#Description
'''
Usage Description
This Python script is designed to convert JSON data extracted from a document analysis process into a structured CSV format. The JSON data is assumed to contain information about specific days, professionals, and their signatures extracted from a set of documents. The script iterates through the JSON data, corrects any discrepancies in the day sequence, and assigns binary values (1 or 0) based on the presence of values in certain cells. Finally, it writes the processed data into a CSV file.

Script Output
The script generates a CSV file containing the following columns:

    Day: Represents the day number.
    Professional: Indicates whether there is data related to a professional on that day (1 if present, 0 if absent).
    Professional Signature: Indicates whether there is a professional signature on that day (1 if present, 0 if absent).
    Family Signature: Indicates whether there is a family signature on that day (1 if present, 0 if absent).
    
The CSV file is saved at the specified path, and upon completion, the script prints a confirmation message indicating the successful saving of the data.'''

# Replace this with the path to your JSON file
json_path = r'...\output_analysis\Form9- T.O_extracted-v2.json'

# Path for the output CSV file
csv_path = r'...\output_analysis\output_extration_analysis.csv'

# Function to find and fix the day if necessary
def found_fix_day(current_day, day_text):
    # Try to find a number in the text that matches the expected day
    for i in range(1, 32):  # Range of possible days in a month
        if str(i) in day_text:
            return i
    return current_day

# Read and load the content of the JSON file
with open(json_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Prepare the data for the CSV file
csv_rows = []
expected_day = 1

for i, item in enumerate(data):
    day_text = item['cells'][0]['cell_text']
    current_day = int(day_text) if day_text.isdigit() else expected_day

    # Check and correct the sequence of days
    if current_day != expected_day:
        corrected_day = found_fix_day(current_day, day_text)
        if corrected_day == expected_day:
            current_day = corrected_day
        else:
            print(f"Warning: Day sequence interrupted at {expected_day}, text found: '{day_text}'")

    # Check and assign 1 or 0 depending on whether there is a value in the cell
    professional = 1 if item['cells'][1]['cell_text'].strip() else 0
    professional_signature = 1 if item['cells'][2]['cell_text'].strip() else 0
    family_signature = 1 if item['cells'][3]['cell_text'].strip() else 0

    csv_rows.append([current_day, professional, professional_signature, family_signature])
    expected_day = current_day + 1

# Write the data to a CSV file
with open(csv_path, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Day', 'Professional', 'Professional Signature', 'Family Signature'])  # Headers
    writer.writerows(csv_rows)

print(f'Data successfully saved to {csv_path}')



