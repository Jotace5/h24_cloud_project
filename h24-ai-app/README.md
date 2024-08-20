# PDF Document Processing Backend for House 24

## Introduction
Welcome to the PDF document processing backend developed for House 24. This Python script harnesses the power of Google Cloud Document AI service along with custom processors to streamline and expedite the invoicing process.

## Project Development Journey
I initiated the development process in October 2023, spending three months training various data reading and extraction models using the GCP Document AI service. Once I acquired sufficient knowledge, I aimed to develop an automated document management system. I synthesized the client's request and based on the methods used by the data entry employees, I designed an automated workflow where PDF files are divided based on page type. Each part of the document is then sent through different processors trained on GCP. Once each processor extracts the corresponding information, a confidence value is added to determine the effectiveness of the result. All processor extractions are collected in a single JSON file, which is later interpreted and analyzed by another section of the app before displaying the results through a web interface.

## Functionality Overview
The backend script provides the following functionalities:

### 1. Frameworks & Libraries
The script imports various libraries and frameworks necessary for PDF processing and interaction with Google Cloud Document AI.

### 2. Configuration
It sets up configuration parameters such as input/output paths, service account credentials, and project ID for Google Cloud.

### 3. API Enablement/Disabling
Functions are provided to enable and disable Google Cloud APIs and Document AI processors.

### 4. PDF File Handling
Functions are available to check and split PDF files into individual pages.

### 5. External Processor Execution
The script asynchronously executes external processor scripts on the first page of each PDF document.

### 6. Processor Configuration Loading
It loads processor configurations from JSON files.

### 7. Asynchronous Execution
The main function coordinates the execution of various tasks, including enabling APIs, processing PDF files, and disabling APIs, utilizing Python's asyncio module.

### 8. Result Processing and Storage
Results from processing are merged and stored in JSON format.

### 9. Updates
Use this section to document updates and changes made to the script over time. Include the date of the update and a brief description of the changes.

- **[2024-02-06]**: Added a functionality to optimize the usage of GCP services, reducing costs.
- **[2024-02-14]**: The first processor is implemented and functionality is tested.
- **[2024-02-16]**: The first of five processors (**ml_key_pair.py**) is integrated.
- **[2024-02-19]**: The second of five processors (**ml_tabular_ext.py**) is added.
- **[2024-02-20]**: The third of five processors (**ml_cat_prediction.py**) is added.
- **[2024-02-22]**: The fourth of five processors (**ml_tabular_ext.py**) is included.
- **[2024-03-01]**: The outputs of the three processors are merged into a single JSON file.
- **[2024-03-13]**: The process of selecting files for training the remaining two models (**ml_evol_data_ext.py** & **ml_page_classif.py**) begins.


### 10. Architecture Overview
 ![Alt text](h24-ai-app/h24%20app.png)

## Usage
1. **Installation:** Ensure that you have Python installed along with the necessary libraries listed in the `requirements.txt` file.

2. **Configuration:** Modify the configuration parameters in the script according to your requirements, including the input/output paths, service account credentials, project ID, and API endpoints.

3. **External Processor Scripts:** Prepare any custom processing scripts you wish to execute on the first page of PDF documents and place them in the 'processors' directory.

4. **Processor Configuration:** Define the configuration for each processor in separate JSON files located in the 'keys' directory.

5. **Execution:** Run the script. Upon execution, it will process PDF files in the specified input directory, execute external processors, and save the results in JSON format in the output directory.

## Note
Ensure that your Google Cloud project has the necessary permissions and billing enabled to use the Document AI API. Also, review and adjust the script's functionality and configurations as needed to fit your specific invoicing workflow.

## Folder Contents
In this folder, you will find:

- **`README.md`**: This file, providing an overview of the PDF document processing backend.
- **`requirements.txt`**: A file listing all the required Python libraries and their versions.
- **`main_file.py`**: contains the main Python script responsible for processing PDF documents using the Google Cloud Document AI service and custom processors.
- **`keys/`**: A directory containing service account credentials and processor configuration files.
- **`processors/`**: A directory where you can place custom processing scripts for PDF documents.
- **`input_data/`**: A directory for storing input PDF files to be processed.
- **`output/`**: A directory where processed results, such as JSON files, are stored. Here you will find an example file. This is the JSON response from the program.
