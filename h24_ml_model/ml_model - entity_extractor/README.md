# PDF Data Extraction with Google Document AI

## Overview
This Python script automates the extraction and analysis of data from PDF documents using Google Document AI. It processes documents to extract various data entities, such as entities, from specified input directories using the Document AI Online Processing API. The extracted data is then saved into a structured JSON format for further analysis or integration into other systems.

## Key Features
- **Google Document AI Integration:** Utilizes the Document AI Online Processing API for processing PDF documents.
- **Data Extraction:** Extracts various data entities, such as entities, from PDF documents.
- **Structured JSON Output:** Saves the extracted data into a structured JSON format for easy analysis and integration.
- **Error Handling:** Provides error handling to handle exceptions during document processing.

## Prerequisites
Before using the script, ensure you have the following:

1. **Google Cloud Account:** You need access to Google Cloud services and the Document AI API.
2. **Service Account Key:** Generate a service account key file and set the path in the `GOOGLE_APPLICATION_CREDENTIALS` environment variable.
3. **Python Environment:** The script requires Python to be installed on your system along with the necessary dependencies.

## Getting Started
1. **Configuration:**
   - Set up the following configuration parameters in the script:
     - `PROJECT_ID`: Your Google Cloud project ID.
     - `LOCATION`: The location of the Document AI processor.
     - `PROCESSOR_ID`: The ID of the Document AI processor.
     - `MIME_TYPE`: The MIME type of the input PDF files.
     - `FOLDER_PATH`: The path to the folder containing input PDF files.
     - `OUTPUT_PATH`: The path to the folder where the output JSON files will be saved.

2. **Installation:**
   - Install the required Python libraries using pip:
     ```sh
     pip install google-cloud-documentai tqdm
     ```

3. **Running the Script:**
   - Execute the script by running it with Python:
     ```sh
     python your_script_name.py
     ```

4. **Reviewing Output:**
   - Once the script completes execution, review the output JSON file in the specified output folder.

## Folder Contents
Inside the `entity_extractor` folder, you will find tree subfolders: `data_to_test`, `data_to_training` and `extracted_data_output`. 

   - **`data_to_test`**
      This folder contains an example file used to test the functioning of the model and the confidence obtained in the extracted data.

   - **`data_to_training`**
      This folder contains a csv file with a list of the files that were used to traing the ml model with the GCP Document AI services

   - **`extracted_data_output`**
      In this folder, you will find `extracted_data_v1.json`. The JSON file is assumed to contain information about specific data extracted from a set of documents,

## Example Usage
Here's an example of how to use the script:

```python
# Set up configuration parameters
PROJECT_ID = "your-project-id"
LOCATION = "us-central1"
PROCESSOR_ID = "your-processor-id" 
MIME_TYPE = "application/pdf"
FOLDER_PATH = "input_folder"
OUTPUT_PATH = "output_folder"

# Run the script
python your_script_name.py
```