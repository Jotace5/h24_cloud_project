## Layer 3

- Preprocessing of PDFs in OCR Project

### Objective

- Optimize the quality and consistency of a set of PDF documents in order to prepare the data for training an Optical Character Recognition (OCR) model.

---

### Methodology

### 1- Data Separation by Quality

- **Purpose**: Separate files into high and low quality formats for model training.
- **Methodology**: Separation is done using a Python script that reads a CSV file containing metadata of the files, including the producer. Then, based on this information, it moves the files to the corresponding folders.

### 2- Analysis of PDF File Quality

- **Purpose**: Analyze the quality of PDF files based on the data source.
- **Methodology**: We will analyze the proportion and distribution of these files and their associated data to determine which ones are ideal for model training.

### 3- Segmentation of PDF Files

- **Purpose**: Divide PDF files into smaller sections or segments for more efficient handling during training.
- **Methodology**: Using specific PDF tools, the documents will be segmented to use the smaller ones, maximizing the amount of information for training.

### 4- Subdivision into 1GB Folders

- **Purpose**: Organize files into folders so that each folder does not exceed a size of 1GB for easier management.
- **Methodology**: A Python script will be used to distribute the files into folders based on their accumulated size until the 1GB limit is reached.

### 5- Analysis of the 10 High Quality Data Folders

- **Purpose**: Evaluate and ensure the quality of the data within the 10 folders labeled as high quality.
- **Methodology**: A detailed analysis of the files within these folders will be conducted, verifying their integrity, relevance, and consistency with high quality criteria.

### 6- Maximization of Files

- **Purpose**: A collection of files will be gathered to form a final group of high quality files for model training.
- **Methodology**: New high quality files will be identified and added to the collection, ensuring they meet the required standards and enhance the capacity and accuracy of the model in training.

---
