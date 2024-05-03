# PDF Data Extraction with Google Document AI

## Overview
This Python script automates the extraction and analysis of data from PDF documents using Google Document AI. It processes documents to extract text data, including form fields and tables, from specified input directories. The extracted data is then combined into a structured JSON format for further analysis or integration into other systems.

## Key Features
- **Google Document AI Integration:** Utilizes Google Document AI for processing PDF documents.
- **Text and Table Extraction:** Extracts text data, including form fields and tables, from PDF documents.
- **Structured JSON Output:** Combines extracted data into a structured JSON format for easy analysis and integration.
- **Customizable Configuration:** Allows configuration of project-specific parameters such as project ID, location, processor ID, MIME type, input folder path, and output folder path.
- **Automated Processing:** Processes all PDF files within the specified input folder automatically.

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
     pip install google-cloud-documentai
     ```

3. **Running the Script:**
   - Execute the script by running the `process_file` function with the specified input folder path:
     ```python
     process_file(FOLDER_PATH, PROJECT_ID, LOCATION, PROCESSOR_ID, MIME_TYPE)
     ```

4. **Reviewing Output:**
   - Once the script completes execution, review the output JSON files in the specified output folder.

## Folder Contents
Inside the `tabular_extractor` folder, you will find two subfolders: `data_to_test` and `output_analysis`. 

   - **data_to_test**
      This folder contains an example file used to understand the functioning of the model and the confidence obtained in the extracted data.

   - **output_analysis**
      In this folder, you will find `extraction_analysis.py`.

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
process_file(FOLDER_PATH, PROJECT_ID, LOCATION, PROCESSOR_ID, MIME_TYPE)
```

## Notes
   - This script is particularly useful for businesses or researchers looking to streamline the processing of large volumes of PDF documents for data analysis or digital transformation initiatives.
   - Ensure that your Google Cloud account has the necessary permissions to access the Document AI API and perform document processing tasks.