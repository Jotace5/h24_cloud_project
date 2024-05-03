import os
import pandas as pd
import csv
import json
from tqdm import tqdm
from google.cloud import documentai_v1 as documentai

# Description 
"""
This Python script utilizes Google Document AI's Online Processing API to process PDF documents for data extraction. It extracts various entities from the documents and saves the extracted data into a structured JSON format. The script is designed to handle multiple PDF files within a specified input folder and output the extracted data to a specified output folder. Additionally, it provides error handling to manage exceptions during the document processing workflow. 

Ensure to configure the script with appropriate credentials, project ID, location, processor ID, MIME type, input folder path, and output folder path before running it.

Usage:
1. Set up Google Cloud credentials by specifying the path to your service account key file in the environment variable GOOGLE_APPLICATION_CREDENTIALS.
2. Configure project-specific parameters such as PROJECT_ID, LOCATION, PROCESSOR_ID, MIME_TYPE, FOLDER_PATH, and OUTPUT_PATH.
3. Run the process_file function to process all PDF files in the input folder, extract the data, and save it as JSON files in the output folder.

This script is particularly useful for businesses or researchers looking to streamline the processing of large volumes of PDF documents for data analysis or digital transformation initiatives.
"""

# Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"put/your/credentials/here/credentials.json"

# Configuration
PROJECT_ID = "complete-your-project-id-here"
LOCATION = "complete-your-location-here"
PROCESSOR_ID = "complete-your-processor-id-here" 
MIME_TYPE = "complete-your-mime-type-here"

FOLDER_PATH = r'put/your/input_folder/here'
OUTPUT_PATH = r'put/your/output_folder/here'

def online_process(
    project_id: str,
    location: str,
    processor_id: str,
    file_path: str,
    mime_type: str,
) -> documentai.Document:
    """
    Processes a document using the Document AI Online Processing API.
    """
    opts = {"api_endpoint": f"{location}-documentai.googleapis.com"}

    # Instantiates a client
    documentai_client = documentai.DocumentProcessorServiceClient(client_options=opts)

    # The full resource name of the processor
    resource_name = documentai_client.processor_path(project_id, location, processor_id)

    # Read the file into memory
    with open(file_path, "rb") as file:
        file_content = file.read()

    # Load Binary Data into Document AI RawDocument Object
    raw_document = documentai.RawDocument(content=file_content, mime_type=mime_type)

    # Configure the process request
    request = documentai.ProcessRequest(name=resource_name, raw_document=raw_document)

    # Process the sample form
    result = documentai_client.process_document(request=request)

    return result.document


def extract_all_data(document):
    all_data = []
    
    # Extracting entities
    for entity in document.entities:
        all_data.append({
            "Type": "Entity",
            "EntityType": entity.type_,
            "Text": entity.mention_text,
            "Confidence": entity.confidence
        })

    return all_data

# Process documents and extract data
results = []

# Check if there are PDF files in the directory
pdf_files = [f for f in os.listdir(FOLDER_PATH) if f.endswith('.pdf')]

if not pdf_files:
    print("No PDF files found in the specified folder.")
else:
    for file_name in tqdm(pdf_files, desc="Processing Files"):
        try:
            file_path = os.path.join(FOLDER_PATH, file_name)
            document = online_process(PROJECT_ID, LOCATION, PROCESSOR_ID, file_path, MIME_TYPE)
            file_data = extract_all_data(document)
            results.extend(file_data)
        except Exception as e:
            print(f"Error processing {file_name}: {e}")

# Save results to JSON file
json_file_path = os.path.join(OUTPUT_PATH, 'extracted_data.json')
with open(json_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(results, json_file, ensure_ascii=False, indent=4)
