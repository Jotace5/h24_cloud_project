import os
import pandas as pd
import json
import numpy as np
from typing import List, Sequence, Dict
from google.cloud import documentai

# Description 
"""
This script automates the extraction and analysis of data from PDF documents using Google Document AI. 
It processes documents to extract text data, including form fields and tables, from specified input directories.
The extracted data is combined into a structured JSON format for further analysis or integration into other systems.

Key Functionalities:
- Setting up Google Cloud credentials
- Defining project-specific parameters
- Processing documents to extract text and table data with detailed layout and confidence scores
- Saving extracted data as JSON files

Usage:
1. Set up Google Cloud credentials by specifying the path to your service account key file in the environment variable GOOGLE_APPLICATION_CREDENTIALS.
2. Configure project-specific parameters such as PROJECT_ID, LOCATION, PROCESSOR_ID, MIME_TYPE, FOLDER_PATH, and OUTPUT_PATH.
3. Run the process_file function to process all PDF files in the input folder, extract the data, and save it as JSON files in the output folder.

This script is particularly useful for businesses or researchers looking to streamline the processing of large volumes of PDF documents for data analysis or digital transformation initiatives.
"""

# Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"put/your/credentials/here/credentials.json"

# Configuration
PROJECT_ID = "complete-your-project-id-here"
LOCATION = "complete-your-location-here"
PROCESSOR_ID = "complete-your-processor-id-here" 
MIME_TYPE = "complete-your-mime-type-here"
FOLDER_PATH = r'put/your/input_folder/here'
OUTPUT_PATH = r'put/your/output_folder/here'

def process_document(
    project_id: str,
    location: str,
    processor_id: str,
    file_path: str, 
    mime_type: str
) -> documentai.Document:
    """
    Processes a document using Google Document AI.
    """
    client = documentai.DocumentProcessorServiceClient()
    resource_name = client.processor_path(project_id, location, processor_id)

    with open(file_path, "rb") as image:
        image_content = image.read()

    request = documentai.ProcessRequest(
        name=resource_name,
        raw_document=documentai.RawDocument(content=image_content, mime_type=mime_type)
    )

    result = client.process_document(request=request)
    return result.document

def text_anchor_data_table(text_anchor: documentai.Document.TextAnchor, text: str) -> str:
    """
    Converts text anchors to string.
    """
    response = ""
    for segment in text_anchor.text_segments:
        start_index = int(segment.start_index)
        end_index = int(segment.end_index)
        response += text[start_index:end_index]
    return response.strip().replace("\n", " ")

def extract_position(bounding_poly):
    """
    Extracts the position from the bounding_poly. Returns the top-left and bottom-right coordinates.
    """
    # Assuming bounding_poly.vertices is a list of vertices in order: top-left, top-right, bottom-right, bottom-left
    if not bounding_poly or not bounding_poly.vertices or len(bounding_poly.vertices) < 4:
        return None

    top_left = bounding_poly.vertices[0]
    bottom_right = bounding_poly.vertices[2]

    return {
        "x_min": top_left.x,  # Left-most X coordinate
        "y_min": top_left.y,  # Top-most Y coordinate
        "x_max": bottom_right.x,  # Right-most X coordinate
        "y_max": bottom_right.y  # Bottom-most Y coordinate
    }
    
def convert_vertices_to_dict(vertices):
    """
    Converts a list of vertices to a list of dictionaries with x and y coordinates.
    """
    return [{"x": vertex.x, "y": vertex.y} for vertex in vertices]

def extract_data_format(document: documentai.Document
) -> str:
    
    # Read form fields and tables from the document
    document_data = {
        "fields": [],
        "tables": []
    }

    for page in document.pages:
        page_data = {
            "tables": []
        }

        for table in page.tables:
            table_data = {
                "num_columns": len(table.header_rows[0].cells),
                "num_rows": len(table.body_rows),
                "header_rows": [],
                "body_rows": []
            }

            # Extract header rows
            for header_row in table.header_rows:
                header_row_data = [text_anchor_data_table(cell, document.text) for cell in header_row.cells]
                table_data["header_rows"].append(header_row_data)

            # Extract data rows
            for body_row in table.body_rows:
                body_row_data = [text_anchor_data_table(cell, document.text) for cell in body_row.cells]
                table_data["body_rows"].append(body_row_data)

            page_data["tables"].append(table_data)
        
        document_data["pages"].append(page_data)

    return document_data

def get_table_data(header_rows: Sequence[documentai.Document.Page.Table.TableRow], body_rows: Sequence[documentai.Document.Page.Table.TableRow], text: str) -> List[dict]:
    """
    Extracts text data, layout information, and positions from table rows.
    Includes column names and confidence scores for each cell.
    """
    # Extract headers
    headers = []
    if header_rows:
        for header_cell in header_rows[0].cells:  # Assuming the first row is the header
            header_text = text_anchor_data_table(header_cell.layout.text_anchor, text)
            headers.append(header_text)
    
    all_rows_data = []
    for row_index, row in enumerate(body_rows):
        row_data = {
            "row_index": row_index,
            "row_limits": None,  # Initialize row position
            "cells": []
        }
        for cell_index, cell in enumerate(row.cells):
            cell_text = text_anchor_data_table(cell.layout.text_anchor, text)
            cell_position = extract_position(cell.layout.bounding_poly)
            cell_confidence = cell.layout.confidence  # Extract confidence score
            bounding_poly_dict = convert_vertices_to_dict(cell.layout.bounding_poly.vertices)
            # Associate cell with corresponding header
            column_name = headers[cell_index] if cell_index < len(headers) else None

            cell_data = {
                "column_name": column_name,
                "cell_text": cell_text,
                "cell_confidence": cell_confidence,  # Include confidence score
                "position": cell_position,
                "bounding_poly": bounding_poly_dict # Correct attribute for bounding polygon
            }
            row_data["cells"].append(cell_data)

            if not row_data["row_limits"]:  # If row position not set, initialize it
                row_data["row_limits"] = cell_position
            else:
                # Update row position to include current cell (if needed)
                row_data["row_limits"]["x_max"] = max(row_data["row_limits"]["x_max"], cell_position["x_max"])
                row_data["row_limits"]["y_max"] = max(row_data["row_limits"]["y_max"], cell_position["y_max"])

        all_rows_data.append(row_data)
    return all_rows_data

def combine_data(document_data, all_rows_data):
    """
    Combines the extracted data from tables and forms into a single dictionary.
    """
    combined_data = {
        "form_data": document_data,
        "table_data": all_rows_data
        
    }
    return combined_data

def process_file(
    folder_path: str, 
    project_id: str, 
    location: str, 
    processor_id: str, 
    mime_type: str
):
    """
    Processes all PDF files in a given folder, extracts the data, and combines it into a single JSON file.
    """
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            document = process_document(project_id, location, processor_id, file_path, mime_type)
            
            for page_number,page in enumerate(document.pages, start=1):
                for table_number,table in enumerate(page.tables, start=1):
                    # Extract table data including headers, cell text, and positions
                    table_data = get_table_data(table.header_rows, table.body_rows, document.text)
            
            # Process the document again to get form data
            form_data = extract_data_format(document)

            # Combine table and form data
            combined_data = combine_data(form_data, table_data)

            # Save the combined data to a JSON file
            json_filename = f"{os.path.splitext(filename)[0]}_combined_extracted.json"
            output_file_path = os.path.join(OUTPUT_PATH, json_filename)
            with open(output_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(combined_data, json_file, ensure_ascii=False, indent=4)


# Main call to process_folder
process_file(FOLDER_PATH, PROJECT_ID, LOCATION, PROCESSOR_ID, MIME_TYPE)
