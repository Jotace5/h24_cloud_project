# ml_key_value_pair_ext.py
import sys
import json
from google.cloud import documentai
import os
import logging
from google.api_core.exceptions import GoogleAPICallError, RetryError

"""
This script processes PDF documents using Google Cloud's Document AI API to extract valuable information. 
It supports two types of information extraction: entity recognition and key-value pair extraction, utilizing separate processor scripts for each task. 
The script dynamically handles the processing of PDF files, whether they contain a single page or multiple pages, and saves the extracted information into JSON files.

Configuration:
- The script uses a MIME_TYPE of "application/pdf" for processing.
- Configuration details for the Document AI processor are loaded from a JSON file located in a 'keys' directory.
- The GOOGLE_APPLICATION_CREDENTIALS environment variable is set to point to the service account key file for authentication with Google Cloud services.

Functionality:
- The script loads processor details from a specified configuration file.
- It sends documents to the Document AI API for processing, handling both single-page and multi-page PDF files.
- Extracted information includes entities' types, texts, and confidence scores, which are logged and saved in a JSON file.
- The script supports running additional processors from the 'processors' directory, allowing for modular expansion of processing capabilities.

Usage:
- The script is intended to be run from the command line, requiring the path to a PDF document as an argument.
- It logs processing information, including errors and the location of saved output files.

Requirements:
- Google Cloud Document AI API access and a valid service account key.
- The 'documentai' Python package for interacting with the Document AI API.
- Python 3.6+ due to the use of f-strings and async features.

Example Command:
    python script_name.py path_to_pdf_document #modify

Where 'script_name.py' is the name of this script, and 'path_to_pdf_document' is the path to the PDF file to be processed.
"""
  
#Configuration
MIME_TYPE = "application/pdf" # MIME_TYPE of the file will be process
# Get the directory of the currently executing script
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)

TEMP_FOLDER = os.path.join(parent_dir, 'temp') #CAMBIO REALIZADO POR "h24_ai_app/temp"
KEYS_FILE_PATH = os.path.join(parent_dir, 'keys', 'credentials.json')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEYS_FILE_PATH 


def load_config(file_path):
    """
    Loads processor details from ml_key_value_config.json.
    
    Args:
        file_path (str): The path to the configuration JSON file.
        
    Returns:
        dict: A dictionary containing the loaded configuration details.
    """
    with open(file_path, 'r') as config_file:
        return json.load(config_file)

def online_process(project_id, location, processor_id, file_path, mime_type):
    """
    Sends the document to Google Cloud Document AI for processing.
    
    Args:
        project_id (str): The Google Cloud project ID.
        location (str): The location of the Document AI processor.
        processor_id (str): The ID of the Document AI processor.
        file_path (str): The path to the PDF file to be processed.
        mime_type (str): The MIME type of the document.
        
    Returns:
        documentai.Document: The processed document object.
    """
    client_options = {"api_endpoint": f"{location}-documentai.googleapis.com"}
    client = documentai.DocumentProcessorServiceClient(client_options=client_options)
    resource_name = client.processor_path(project_id, location, processor_id)
    
    with open(file_path, "rb") as f:
        file_content = f.read()
    
    raw_document = documentai.RawDocument(content=file_content, mime_type=mime_type)
    request = documentai.ProcessRequest(name=resource_name, raw_document=raw_document)
    
    result = client.process_document(request=request)
    return result.document

def extract_all_data(document):
    """
    Extracts entities and their details from the processed document.

    Args:
        document (documentai.Document): The document object returned by Document AI.

    Returns:
        List[Tuple[str, str, float]]: A list of tuples, each containing the entity type, text, and confidence score for an entity.
    """
    extracted_data = []  # Initialize an empty list to hold extracted data

    # Check if the document has entities
    if document.entities:
        for entity in document.entities:
            # Extract the entity type, text, and confidence, and append as a tuple
            extracted_data.append((entity.type_, entity.mention_text, entity.confidence))
        # Log the number of extracted entities
        logging.info(f"Extracted {len(extracted_data)} entities from the document.")
    else:
        # Log a warning if no entities are found in the document
        logging.warning("No entities were found in the document.")
        
    return extracted_data


if __name__ == "__main__":
    """ 
    Main function to run the script.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Assuming this script is located in h24_ai_app, directly find the keys directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Navigate to the parent directory of the current directory to then access the 'keys' folder
    parent_dir = os.path.dirname(current_dir)
    keys_dir = os.path.join(parent_dir, 'keys') # This now correctly points to h24_ai_app/keys
        
    config_path = os.path.join(keys_dir, 'ml_key_value_config.json')
        
    try:
        config = load_config(config_path)
    except FileNotFoundError:
        logging.error(f"Configuration file not found in {config_path}")
        sys.exit(1)
    
    if len(sys.argv) < 2:
        logging.error("Error: Expects to receive a PDF file as an argument from the main script. Usage: python main_script_name.py path_to_pdf_document")
        sys.exit(1)
    
    file_path = sys.argv[1]
    file_name = os.path.basename(file_path)
    
    try:
        document = online_process(config['PROJECT_ID'], config['LOCATION'], config['PROCESSOR_ID'], file_path, MIME_TYPE)
    except GoogleAPICallError as e:
        logging.error(f"API call failed: {e.message}")
        sys.exit(1)
    except RetryError as e:
        logging.error(f"Request to Document AI exceeded retry limits: {e.message}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)
        
        
    extracted_data = extract_all_data(document)
    
    # Prepare the document data for JSON output
    document_data = {
        "processor": 'ml_key_value_pair_ext',
        "file_name": file_name,
        "document_entities": [
            {
                "entity_type": data[0],
                "entity_text": data[1],
                "entity_confidence": data[2]
            } for data in extracted_data
        ]
    }
    
    # Write the results to a JSON format
    # Convert document_data to a JSON string
    json_document_data = json.dumps(document_data, indent=4)
       
        # Print the JSON string to standard output
    print(json_document_data)
    
    logging.info("Document results processed.") 