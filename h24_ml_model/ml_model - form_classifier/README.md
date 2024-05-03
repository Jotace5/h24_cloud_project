# PDF Data Processing with Google Document AI

## Overview
This Python script automates the processing and analysis of PDF documents using Google Document AI. It is designed to separate the sheets of PDF files and process only the first sheet. The script then utilizes the Document AI Online Processing API to extract data from the processed documents, such as entities and their confidence levels. The extracted data is then analyzed and saved to a CSV file for further review or integration into other systems.

## Key Features
- **Sheet Separation:** The script separates the sheets of PDF files and processes only the first sheet to optimize processing time.
- **Google Document AI Integration:** Utilizes the Google Document AI Online Processing API to extract data from processed documents.
- **Entity Extraction:** Extracts entities from documents along with their confidence levels for analysis.
- **CSV Output:** Saves the analyzed data to a CSV file for easy review and integration into other systems.

## Prerequisites
Before using the script, ensure you have the following:

1. **Google Cloud Account:** Access to Google Cloud services and the Document AI API.
2. **Service Account Key:** Generate a service account key file and set the path in the `GOOGLE_APPLICATION_CREDENTIALS` environment variable.
3. **Python Environment:** Python installed on your system along with the necessary dependencies listed in `requirements.txt`.

## Usage
1. **Configuration:**
   - Replace the placeholders in the script with your Google Cloud project ID, location, processor ID, and MIME type.
   - Set the `FOLDER_PATH` variable to the path of the folder containing the input PDF files.
   - Set the `OUTPUT_PATH` variable to the path of the folder where output files will be saved.

2. **Sheet Separation:**
   - The script will separate the sheets of the PDF files in the input folder and process only the first sheet.

3. **Document Processing:**
   - The script will process each PDF document using the Google Document AI Online Processing API.
   - Extracted entities and confidence levels will be printed for each document.

4. **CSV Output:**
   - The analyzed data will be saved to a CSV file named `output_model_v4.csv` in the `output_analysis` directory.

## Folder Contents
Inside the `form_classifier` folder, you will find two subfolders: `training_data` and `output_analysis`. 

   - **`training_data`**
      This folder contains an csv file with a list of the files were useded to train the model.

   - **`output_analysis`**
      In this folder, you will find `v4_data_extraction_analysis.ipynb`. This jupyter notebook analyse the content of `output_model_v4.csv`. More details on the file.

## Notes
- This script is useful for automating the extraction and analysis of data from PDF documents, particularly in scenarios where large volumes of documents need to be processed efficiently.

- Ensure that your Google Cloud account has the necessary permissions to access the Document AI API and perform document processing tasks.