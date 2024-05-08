# ml_cat_prediction.py
import sys
import json
from google.cloud import documentai
import os
import logging
from google.api_core.exceptions import GoogleAPICallError, RetryError

"""
A script for processing PDF documents using Google Cloud Document AI to predict categories.

This script performs the following steps:
1. Configuration Loading: Loads the Google Cloud Document AI processor details 
   (project_id, location, processor_id) from a JSON configuration file named ml_cat_prediction_config.json.
2. Document Processing: Utilizes the online_process function to send PDF documents to 
   Google Cloud Document AI for analysis and processing. The function requires the document's file path and 
   leverages the MIME type 'application/pdf' for processing.
3. Result Analysis: Implements logic within the analyze_result function to extract meaningful 
   information from the processed document, such as category prediction and confidence levels. 
   Users need to adapt this function based on their specific requirements and the output structure 
   provided by their configured Document AI processor.
4. JSON Output: Generates and prints a JSON object that includes the processor used, the name of the 
   processed file, the predicted category, and the confidence in that prediction.

Usage:
    python ml_cat_prediction.py <path_to_pdf_document>

Example:
    python ml_cat_prediction.py documents/invoice.pdf

Note:
    Before running this script, ensure that the ml_cat_prediction_config.json file exists in the same directory 
    and is properly configured with your Google Cloud project's Document AI processor details. Additionally, 
    the GOOGLE_APPLICATION_CREDENTIALS environment variable should be set to the path of your Google Cloud 
    service account key file.
"""

#Configuration
MIME_TYPE = "application/pdf" # MIME_TYPE of the file will be process
# Get the directory of the currently executing script
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)

TEMP_FOLDER = os.path.join(parent_dir, 'temp') 
KEYS_FILE_PATH = os.path.join(parent_dir, 'keys', 'credentials.json')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEYS_FILE_PATH 


def load_config(file_path):
    """
    Loads processor details from ml_cat_prediction_config.json.
    
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

def analyze_result(document):
    """
    Extracts the category and confidence from the processed document. Specific logic needs to be implemented
    to extract meaningful information based on the structure of your documents and what Document AI returns.
    
    Args:
        document (documentai.Document): The document object returned by Document AI.
        
    Returns:
        tuple: A tuple containing the predicted category (str) and the confidence (float).
    """
    highest_confidence_entity = max(document.entities, key=lambda entity: entity.confidence, default=None)
    
    if highest_confidence_entity:
        category = highest_confidence_entity.type_
        confidence = highest_confidence_entity.confidence
    else:
        category = "No category found"
        confidence = 0
    
    return category, confidence

if __name__ == "__main__":
    """ 
    Main function to run the script.
    """
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Navigate to the parent directory of the current directory to then access the 'keys' folder
    parent_dir = os.path.dirname(current_dir)
    keys_dir = os.path.join(parent_dir, 'keys') # This now correctly points to h24_ai_app/keys

    # Constructs the path to the configuration file located inside the 'keys' folder
    config_path = os.path.join(keys_dir, 'ml_cat_prediction_config.json')
    
    # Load the configuration
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
    
    category, confidence = analyze_result(document)
    
    category_data = {
        "processor": "ml_cat_prediction",
        "file_name": os.path.basename(file_path),
        "category_prediction": category,
        "confidence": confidence
    }   
    
    # Write the results to a JSON format
    # Convert document_data to a JSON string
    json_category_data = json.dumps(category_data, indent=4)
       
    # Print the JSON string to standard output
    print(json_category_data)
    
    logging.info("Category prediction results processed.")


