import os
import pandas as pd
import csv
from tqdm import tqdm
from google.cloud import documentai_v1 as documentai
import fitz  # PyMuPDF

'''
Script Description:
This Python script facilitates the extraction and analysis of data from PDF documents using Google Document AI. It involves multiple steps, including separating the pages of PDF files and processing only the first page, utilizing Google Document AI for online document processing, and analyzing the extracted data to identify the classification with the highest confidence level.

Usage:
The script begins by setting up the necessary credentials and configuration parameters, including the Google Cloud project ID, location, processor ID, and MIME type. It also defines a function to extract the first page from PDF files to process only the relevant information efficiently.

After processing the documents, it proceeds to utilize Google Document AI's online processing API to extract data from each document. The script then analyzes the extracted data to identify the classification with the highest confidence level. It prints the analysis results for each document, indicating the corresponding classification and the margin of error.

Finally, it writes the analysis results into a CSV file named "info_files_training_data.csv", containing columns for the file name, category prediction, and confidence level.

The script provides insights into the classification of each document, aiding in automated document processing and categorization tasks. Additionally, it serves as a practical example of integrating Google Document AI capabilities into document analysis workflows.
'''


# Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"put/your/credentials/here/credentials.json"

# Configuration
PROJECT_ID = "complete-your-project-id-here"
LOCATION = "complete-your-location-here"
PROCESSOR_ID = "complete-your-processor-id-here" 
MIME_TYPE = "complete-your-mime-type-here"

FOLDER_PATH = r'put/your/input_folder/here'
OUTPUT_PATH = r'put/your/output_folder/here'

# The program should separate the sheets of the PDF files and process only the 1st sheet.
def extract_first_page(pdf_input, pdf_output):
    document = fitz.open(pdf_input)
    output_document = fitz.open()
    output_document.insert_pdf(document, from_page=0, to_page=0)
    output_document.save(pdf_output)
    document.close()
    output_document.close()
    
    return pdf_output  # Returns the path of the generated file

# Process each PDF file in the folder
file_paths = [os.path.join(FOLDER_PATH, file) for file in os.listdir(FOLDER_PATH) if file.endswith('.pdf')]

for file_path in tqdm(file_paths, desc="Processing documents"):
    base_name = os.path.basename(file_path)
    new_file_name = base_name.replace('.pdf', '_1pg.pdf')
    new_file_path = os.path.join(SAVE_FOLDER, new_file_name)
    
    extract_first_page(file_path, new_file_path)

# Async function to avoid processing useless pages.
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


# List all files in the folder
file_paths = [os.path.join(SAVE_FOLDER, file) for file in os.listdir(SAVE_FOLDER) if file.endswith('.pdf')]

# List to store the results
results = []

# Process each document in the folder
for file_path in tqdm(file_paths, desc="Processing documents"):
    document = online_process(
        project_id=PROJECT_ID,
        location=LOCATION,
        processor_id=PROCESSOR_ID,
        file_path=file_path,
        mime_type=MIME_TYPE,
    )

    # Find the entity with the highest confidence
    highest_confidence_entity = None
    highest_confidence = 0
    for entity in document.entities:
        if entity.confidence > highest_confidence:
            highest_confidence_entity = entity
            highest_confidence = entity.confidence

    # Extract file name from FILE_PATH
    file_name = os.path.basename(file_path)

    # Analyze results
    if highest_confidence_entity:
        classification = highest_confidence_entity.type_
        error_margin = 100 - int(highest_confidence * 100)
        print(f"The file '{file_name}' analyzed corresponds to {classification}, the error margin is {error_margin}%.")
    else:
        print(f"No entities found in the file '{file_name}'.")

    # Analyze results and append them to the list
    if highest_confidence_entity:
        classification = highest_confidence_entity.type_
        confidence = highest_confidence
        results.append([file_name, classification, confidence])
    else:
        results.append([file_name, "No category found", 0])

# Write results to a CSV file
with open('output_model_v4.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['file_name', 'category_prediction', 'confidence'])
    writer.writerows(results)
