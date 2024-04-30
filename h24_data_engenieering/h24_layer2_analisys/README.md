# Layer 2 
- Preprocessing of PDFs in OCR Project

## Objective

- Optimize the quality and consistency of a set of PDF documents, with the aim of preparing the data for training an Optical Character Recognition (OCR) model.

---

## Methodology

## 1. Sampling of PDF Files

- **Purpose**: Study a sample of PDF files to determine the best way to segment them.

- **Methodology**: A random sample of 100 files is separated to analyze their metadata. The `pandas` library is used to load the CSV generated in the previous step and perform an exploratory data analysis.

## 2. Analysis of PDF Metadata

- **Purpose**: Establish a procedure that allows us to segment these files effectively.

- **Methodology**: A Python script is used to process all PDF files in a specific directory and extract their metadata. The `process_directory()` function iterates through each PDF file, extracts its metadata, and saves them in a CSV file.

## 3. Analysis of Files Converted from Images to PDFs

- **Purpose**: Establish a procedure that allows us to segment these files effectively.
- **Methodology**: Based on the identification of a specific set of files that exhibit different characteristics from the rest of the dataset, an analysis of the files is performed to determine the best way to segment them.

## 4. Analysis of File Quality based on Data Creation Source

- **Purpose**: Analyze the proportion of files in each category. After completing this analysis, we will evaluate if it's necessary to apply data balancing techniques.
- **Methodology**: We will generate a CSV containing all files, from which we will analyze the proportion and distribution of these data.

---



