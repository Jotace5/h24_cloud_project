
#frameworks & Libraries
import os
import pandas as pd
import csv
import json
from tqdm import tqdm 
import sys
import fitz  
import logging
import subprocess
import asyncio
from functools import partial
import logging 

from google.cloud import documentai_v1 as documentai
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.api_core.client_options import ClientOptions
from google.api_core.exceptions import FailedPrecondition
from google.cloud import documentai  # type: ignore

'''
This script is designed to process PDF documents using the Google Cloud Document AI service and additional custom processors. Here's a breakdown of its functionality:

Imports: The script imports necessary libraries and frameworks, including os, pandas, csv, json, tqdm, sys, fitz, logging, subprocess, asyncio, and specific modules from the google.cloud package for Document AI.

Configuration: It sets up configuration parameters such as input/output paths, service account credentials, and project ID for Google Cloud.

API Enablement/Disabling: Functions are defined to enable and disable Google Cloud APIs and Document AI processors.

PDF File Handling: Functions are provided to check and split PDF files into individual pages.

External Processor Execution: The script asynchronously executes external processor scripts on the first page of each PDF document.

Processor Configuration Loading: It loads processor configurations from JSON files.

Asynchronous Execution: The main function (main()) coordinates the execution of various tasks, including enabling APIs, processing PDF files, and disabling APIs.

Result Processing and Storage: Results from processing are merged and stored in JSON format.

Execution: The script is executed when run as the main program, utilizing Python's asyncio module.
'''

# Data Entry - Configuration
# Get the directory of the currently executing script
script_dir = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH = os.path.join(script_dir, 'input_data')

OUTPUT_DIR = os.path.join(script_dir, 'temp')
# Path to your service account key file
KEY_FILE_PATH = os.path.join(script_dir, 'keys', 'credentials.json')
# Your Google Cloud Project ID
PROJECT_ID = 'your-project-name' 
# The API you want to enable
SERVICE_NAME = 'documentai.googleapis.com'
# Setting the GOOGLE_APPLICATION_CREDENTIALS environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_FILE_PATH


# Basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# API ON
def enable_api(service_name, project_id, key_file_path):
    """Enable a Google Cloud API for a project."""
    credentials = service_account.Credentials.from_service_account_file(
        key_file_path,
        scopes=['https://www.googleapis.com/auth/cloud-platform'],
    )

    service = build('serviceusage', 'v1', credentials=credentials)
    request = service.services().enable(
        name=f'projects/{project_id}/services/{service_name}'
    )
    response = request.execute()

    print(response)
    
# API OFF
def disable_api(service_name, project_id, key_file_path):
    """Disable a Google Cloud API for a project."""
    credentials = service_account.Credentials.from_service_account_file(
        key_file_path,
        scopes=['https://www.googleapis.com/auth/cloud-platform'],
    )

    service = build('serviceusage', 'v1', credentials=credentials)
    request = service.services().disable(
        name=f'projects/{project_id}/services/{service_name}'
    )
    response = request.execute()

    print(response)

# Processor ON
def enable_processor(project_id: str, location: str, processor_id: str) -> None:
    # You must set the api_endpoint if you use a location other than 'us'.
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")

    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    # The full resource name of the location
    processor_name = client.processor_path(project_id, location, processor_id)
    request = documentai.EnableProcessorRequest(name=processor_name)

    # Make EnableProcessor request
    try:
        operation = client.enable_processor(request=request)

        # Print operation name
        print(operation.operation.name)
        # Wait for operation to complete
        operation.result()
    # Cannot enable a processor that is already enabled
    except FailedPrecondition as e:
        print(e.message)
      
# Processor OFF
def disable_processor(project_id: str, location: str, processor_id: str) -> None:
    # You must set the api_endpoint if you use a location other than 'us'.
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")

    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    # The full resource name of the processor
    # e.g.: projects/project_id/locations/location/processors/processor_id
    processor_name = client.processor_path(project_id, location, processor_id)
    request = documentai.DisableProcessorRequest(name=processor_name)

    # Make DisableProcessor request
    try:
        operation = client.disable_processor(request=request)

        # Print operation name
        print(operation.operation.name)
        # Wait for operation to complete
        operation.result()
    # Cannot disable a processor that is already disabled
    except FailedPrecondition as e:
        print(e.message)

# PDF Check
def files_checker(INPUT_PATH):
    """
    Detect files in the input directory to check if they are in the allowed format (.PDF),
    storing their paths in file_paths and logging a warning for files in other formats.
    """
    file_paths = []  # Initialize list to store file paths
    
    for file in os.listdir(INPUT_PATH):
        if file.lower().endswith('.pdf'):
            # Add file path to list if file ends with .pdf (case-insensitive)
            file_paths.append(os.path.join(INPUT_PATH, file))
        else:
            # Log warning if file is not a PDF
            logging.warning(f"Warning: The file format of '{file}' is not recognized as a PDF.")
    
    return file_paths

# File Page Sppliter
def page_splitter(file_paths):#SE MODIFICA COMPORTAMIENTO, SE AGREGA MODELO DE ML PARA DIVIDIR EL ARCHIVO ORIGINAL
    """
    Processes each file splitting it into separate pages. 
    The first page of each file is stored for category prediction,
    and the remaining pages are stored for further processing if necessary.
    """
    first_pages = []  # List to store the paths of the first PDF page of each document
    other_pages = []  # List to store the paths of all other PDF pages

    # Process each document in the list
    for file_path in tqdm(file_paths, desc="Splitting documents"):
        # Open the PDF file
        with fitz.open(file_path) as pdf:
            for page_number in range(len(pdf)):
                # Load the current page
                page = pdf.load_page(page_number)
                single_page_pdf = fitz.open()
                single_page_pdf.insert_pdf(pdf, from_page=page_number, to_page=page_number)
                
                # Define a path for the new single-page PDF
                output_file = f"{file_path[:-4]}-p{page_number + 1}.pdf"
                single_page_pdf.save(output_file)
                
                # Decide where to store the path based on the page number
                if page_number == 0:
                    first_pages.append(output_file)  # Store the first page separately
                else:
                    other_pages.append(output_file)  # Store other pages
                
                # Close the single-page PDF to free resources
                single_page_pdf.close()

    return first_pages, other_pages

# The provided script is designed to asynchronously execute an external script
async def run_external_processor(pdf_page, processor_script):
    process = await asyncio.create_subprocess_exec(
        'python', processor_script, pdf_page,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await process.communicate()
    
    stdout_str = stdout.decode('utf-8', 'ignore')
    stderr_str = stderr.decode('utf-8', 'ignore')

    if process.returncode != 0:
        logging.error(f"Error executing processor {processor_script} for {pdf_page}: {stderr_str}")
        return None  # Indicate an error occurred by returning None

    return stdout  

# Generalized function to send the first page to multiple processors
async def process_first_page(first_page, processors): #QUIZA DEBA SER MODIFICADO PARA TRABAJAR CON MUCHAS PAGINAS DE UN MISMO ARCHIVO
    tasks = []
    for processor_script in processors:
        task = run_external_processor(first_page, processor_script)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results

# Function to load processor configuration from a JSON file
def load_processor_config(json_path):
    with open(json_path, 'r') as file:
        return json.load(file)

async def run_sync_in_executor(func, *args):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(func, *args))

async def main():
    # Get the absolute path to the directory where the main script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the path to the configuration file located in the 'keys' folder
    # The 'keys' folder is at the same level as the main script
    keys_dir = os.path.join(current_dir, 'keys')
    
    # Dynamically load processor configurations from the 'keys' directory
    processor_configs = [os.path.join(keys_dir, json_keys_file) for json_keys_file in os.listdir(keys_dir) if json_keys_file.endswith('_config.json')]
    
    await run_sync_in_executor(enable_api, SERVICE_NAME, PROJECT_ID, KEY_FILE_PATH)
    logging.info("Document AI API has been enabled.")
    
    # Dynamically enable each processor
    for config_path in processor_configs:
        processor_config = load_processor_config(config_path)
        await run_sync_in_executor(enable_processor, processor_config['PROJECT_ID'], processor_config['LOCATION'], processor_config['PROCESSOR_ID'])
        logging.info(f"Processor {processor_config['PROCESSOR_ID']} has been enabled.")

    # Dynamically load processor scripts from the 'processors' directory
    processors_dir = os.path.join(current_dir, 'processors')
    processors = [os.path.join(processors_dir, f) for f in os.listdir(processors_dir) if f.endswith('.py')]
    
    file_paths = files_checker(INPUT_PATH)
    if not file_paths:
        logging.error("No valid PDF files to process.") 
        return

    for pdf_file in tqdm(file_paths, desc="Processing files"):
        # Open the PDF file to check the number of pages
        with fitz.open(pdf_file) as pdf:
            num_pages = len(pdf)
        
        first_pages, other_pages = ([pdf_file], []) if num_pages <= 1 else page_splitter([pdf_file]) #REVISAR SECCION PARA DETERMINAR EL MANEJO DE UN ARCHIVO DE VARIAS HOJAS Y ANALIZARLAS 

        for first_page in first_pages:
            results = await process_first_page(first_page, processors)
            
            merged_results = {"processor_outputs": {}}
            for processor, result in zip(processors, results):
                processor_name = os.path.splitext(os.path.basename(processor))[0]
                try:
                    result_data = json.loads(result)
                    merged_results["processor_outputs"][processor_name] = result_data
                except json.JSONDecodeError as e:
                    logging.error(f"Error decoding JSON from processor {processor_name} output: {e}")
            
            output_filename = os.path.splitext(os.path.basename(first_page))[0] + '_extraction_output.json'
            output_filepath = os.path.join(OUTPUT_DIR, output_filename)
            with open(output_filepath, 'w', encoding='utf-8') as f:
                json.dump(merged_results, f, indent=4)
            
            logging.info(f"Combined processing result for {os.path.basename(first_page)} saved to {output_filepath}")
    
    for config_path in processor_configs:
        processor_config = load_processor_config(config_path)
        await run_sync_in_executor(disable_processor, processor_config['PROJECT_ID'], processor_config['LOCATION'], processor_config['PROCESSOR_ID'])
        logging.info(f"Processor {processor_config['PROCESSOR_ID']} has been disabled.")
    
    await run_sync_in_executor(disable_api, SERVICE_NAME, PROJECT_ID, KEY_FILE_PATH)
    logging.info("Document AI API has been disabled.")

if __name__ == "__main__":
    asyncio.run(main())
  

