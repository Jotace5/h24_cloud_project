![Python](https://img.shields.io/badge/-Python-333333?style=flat&logo=python) ![Jupyter](https://img.shields.io/badge/-Jupyter-333333?style=flat&logo=jupyter) ![Visual Studio Code](https://img.shields.io/badge/-Visual%20Studio%20Code-333333?style=flat&logo=visual-studio-code&logoColor=007ACC) ![Google Cloud](https://img.shields.io/badge/-Google%20Cloud-333333?style=flat&logo=google-cloud) ![Pandas](https://img.shields.io/badge/-Pandas-333333?style=flat&logo=pandas) ![Numpy](https://img.shields.io/badge/-Numpy-333333?style=flat&logo=numpy) ![Matplotlib](https://img.shields.io/badge/-Matplotlib-333333?style=flat&logo=matplotlib) ![Seaborn](https://img.shields.io/badge/-Seaborn-333333?style=flat&logo=seaborn) ![Scikitlearn](https://img.shields.io/badge/-Scikitlearn-333333?style=flat&logo=scikitlearn) ![FastAPI](https://img.shields.io/badge/-FastAPI-333333?style=flat&logo=fastapi)

  
# Data Extraction and Analysis System for House24

## Introduction

Welcome to the repository of the project developed specifically for House24, a leading company in home hospitalization services. This data science project was designed to tackle a critical challenge presented by House24: the need for an application capable of detecting, extracting, and efficiently analyzing data from attendance sheets of health professionals.

## Problem

House24 handles a significant amount of information in the form of sheets, coming from various services such as Caregiving, Nursing, Physiotherapy, Speech Therapy, and Occupational Therapy. These sheets contain crucial data like patient names, billing periods, attendance reports, and more, making their efficient processing essential for daily operations and accurate billing.

The human process of selecting and separating these sheets is meticulous and time-consuming, requiring detailed verification of information, such as names, signatures, stamps, and IDs, of both the health professionals and the patients or relatives.

## Solution

Our project addresses this challenge by developing an advanced data science application that replicates and automates this data extraction and analysis process. Using image processing and machine learning techniques, the application identifies, extracts, and verifies relevant information from the sheets, significantly reducing the time and effort required while increasing the accuracy and efficiency of House24's administrative processes.

### Key Features:

- **Automatic Document Detection:** Identifies attendance and evolution sheets among various documents.
- **Data Extraction:** Extracts key information such as names, billing periods, and signatures.
- **Information Analysis:** Analyzes the consistency and completeness of the extracted data, verifying attendance and reported evolution.
- **User-friendly Interface:** Allows House24 users to easily manage the extracted information and make adjustments if necessary.

## Getting Started

Within the project folder, you will find 3 subfolders. One corresponds to the part of **h24_data_engineering** where a data understanding process is carried out to then develop the corresponding training for GCP ML models. Those data are located in the **h24_ml_models** folder, where the process undertaken is explained. The last folder, **h24_ai_app**, corresponds to the backend development of the app and the progress made with it.

## Contributions

We welcome any contributions to this project. If you have a suggestion for improvement, please review our contribution guide or open an issue in this repository.
