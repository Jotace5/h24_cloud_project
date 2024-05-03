
# Data Engineering Process for ML Models in GCP Document AI

## Introduction:
This README file serves as a documentation of the data engineering process for training each ML model using the GCP Document AI service. The purpose is to explain how data engineering was conducted to train the ML models, which are integral parts of our automated PDF processing application.


## ML Models:
The following ML models trained in the GCP Document AI service are being documented:

1. **Page Classifier:** Identifies different types of pages within PDFs.
2. **Form Classifier:** Recognizes different types of forms within PDFs.
3. **Tabular Extractor:** Extracts tabular data from PDFs.
4. **Daily Evolution Extractor:** Extracts daily evolution data from PDFs.
5. **Entity Extractor:** Extracts entities from PDFs.

**Note:** The five models represent different stages of the automated process for parsing PDF files. Each model is responsible for extracting specific data from PDF files, which will be used by the application we are developing.

## Overview:
The data engineering process involves segmenting the files for each specific model and executing the trained model in GCP to extract the required information. Each model requires different types of training data to achieve the desired extraction. 

**Note:** Each model has its own dedicated folder containing data engineering files and a script for executing the trained model in GCP. These files help in understanding the training process and the functionality of GCP technologies.

## Data Collection:
- **Sources:** Files provided by the company representing their activity over the last two years (2022, 2023).
- **Quality:** Only files scanned by a specific scanner were used for training due to their superior quality.

## Model Training:
- The training of the models is carried out through GCP, where through a visual and inductive process, a selection of the data that will be relevant to be extracted is made. The trainings require different amounts of files to acquire better confidence values.

## Model Evaluation:
- The model evaluation is performed through the confidence scores obtained by each of the models when extracting the required data.

## Example Usage:
- Code snippets for using the trained models and interacting with them for inference or prediction are provided within each model's folder.
