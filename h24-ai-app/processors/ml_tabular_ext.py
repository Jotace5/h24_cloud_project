# ml_tabular_ext.py
import sys
import json
from google.cloud import documentai
from typing import List
from google.cloud.documentai_v1.types import Document
import os
import logging
from google.api_core.exceptions import GoogleAPICallError, RetryError
import itertools

"""
A script for processing PDF documents using Google Cloud Document AI to extract tabular data.

This script performs the following steps:
1. Configuration Loading: Loads the Google Cloud Document AI processor details 
   (project_id, location, processor_id) from a JSON configuration file named ml_tabular_config.json.
2. Document Processing: Utilizes the online_process function to send PDF documents to 
   Google Cloud Document AI for analysis and processing. The function requires the document's file path and 
   leverages the MIME type 'application/pdf' for processing.
3.  
4. JSON Output: Generates and prints a JSON object that includes the processor used, the name of the 
   processed file, the predicted category, and the confidence in that prediction.

Usage:
    python ml_cat_prediction.py <path_to_pdf_document>

Example:
    python ml_cat_prediction.py documents/invoice.pdf

Note:
    Before running this script, ensure that the ml_tabular_config.json file exists in the same directory 
    and is properly configured with your Google Cloud project's Document AI processor details. Additionally, 
    the GOOGLE_APPLICATION_CREDENTIALS environment variable should be set to the path of your Google Cloud 
    service account key file.
"""

#Configuration
MIME_TYPE = "application/pdf" # MIME_TYPE of the file will be process
# Get the directory of the currently executing script
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)

TEMP_FOLDER = os.path.join(parent_dir, 'temp') #CAMBIO REALIZADO POR "h24_ai_app/temp"
KEYS_FILE_PATH = os.path.join(parent_dir, 'keys', 'credentials.json')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEYS_FILE_PATH 

def load_config(file_path):
    """Loads configuration details from a JSON file."""
    with open(file_path, 'r') as config_file:
        return json.load(config_file)

def online_process(project_id, location, processor_id, file_path, mime_type):
    """
    Sends the document to Google Cloud Document AI for processing.
    
    Args:
        project_id (str): The Google Cloud project ID.
        location (str): The location of the Document AI processor.
        processor_id (str): The ID of the Document AI processor.
        file_path (str): The path to the PDF file to be processed.
        mime_type (str): The MIME type of the document.
        
    Returns:
        documentai.Document: The processed document object.
    """
    client_options = {"api_endpoint": f"{location}-documentai.googleapis.com"}
    client = documentai.DocumentProcessorServiceClient(client_options=client_options)
    resource_name = client.processor_path(project_id, location, processor_id)
    
    with open(file_path, "rb") as f:
        file_content = f.read()
    
    raw_document = documentai.RawDocument(content=file_content, mime_type=mime_type)
    request = documentai.ProcessRequest(name=resource_name, raw_document=raw_document)
    
    result = client.process_document(request=request)
    return result.document

def text_anchor_data_table(text_anchor: documentai.Document.TextAnchor, text: str) -> dict:
    """
    Converts text anchors to string and returns the text along with its start and end indices.
    
    Args:
    - text_anchor: The TextAnchor object from a Document AI document.
    - text: The full text of the document.
    
    Returns:
    A dictionary with the extracted text and its start and end indices in the document.
    """
    extracted_text = ""
    start_indices = []
    end_indices = []

    for segment in text_anchor.text_segments:              
        # Convert indices from string to int, assuming they're in int64 format but represented as strings
        start_index = int(segment.start_index)
        end_index = int(segment.end_index)

        extracted_text += text[start_index:end_index]
        start_indices.append(start_index)
        end_indices.append(end_index)

    # Optionally, clean up the extracted text
    clean_text = extracted_text.strip().replace("\n", " ")

    # Return a dictionary containing the text and its boundary indices
    return {
        "text": clean_text,
        "start_index": min(start_indices) if start_indices else None,
        "end_index": max(end_indices) if end_indices else None
    }

def get_token_check(tokens: List[Document.Page.Token]) -> bool:
    """
    Checks if any token in a list of Document AI tokens is handwritten.
    """
    # If the list of tokens is not empty, then the cell has at least one token
    return bool(tokens)  # Returns True if tokens list is not empty, False otherwise

def get_boundaries_limits(bounding_poly): 
    """
    Extracts the boundary limits from a bounding_poly, assuming the polygon represents an axis-aligned rectangle.
    This function returns the coordinates for the left, right, top, and bottom limits of a layout element.
    
    Note: This function assumes the layout element is not rotated. For rotated or skewed elements, a more
    complex approach that considers the orientation would be needed.

    Parameters:
    - bounding_poly: A polygon defining the boundaries of a layout element, expected to have at least 4 vertices.

    Returns:
    A dictionary with the calculated limits for each side of the polygon, including both position and extent:
    - left_limit: The x coordinate of the left boundary and its vertical extent.
    - right_limit: The x coordinate of the right boundary and its vertical extent.
    - top_limit: The y coordinate of the top boundary and its horizontal extent.
    - bottom_limit: The y coordinate of the bottom boundary and its horizontal extent.
    """

    # Validate the input
    if not bounding_poly or not bounding_poly.vertices or len(bounding_poly.vertices) < 4:
        return None
    
    # Extract vertices
    top_left = bounding_poly.vertices[0]
    top_right = bounding_poly.vertices[1]
    bottom_right = bounding_poly.vertices[2]
    bottom_left = bounding_poly.vertices[3]

    # Define boundary limits with more descriptive key naming
    left_limit = {"x_position": top_left.x, "vertical_extent": {"top": top_left.y, "bottom": bottom_left.y}}
    right_limit = {"x_position": top_right.x, "vertical_extent": {"top": top_right.y, "bottom": bottom_right.y}}
    top_limit = {"y_position": top_left.y, "horizontal_extent": {"left": top_left.x, "right": top_right.x}}
    bottom_limit = {"y_position": bottom_left.y, "horizontal_extent": {"left": bottom_left.x, "right": bottom_right.x}}

    return {
        "left_limit": left_limit,
        "right_limit": right_limit,
        "top_limit": top_limit,
        "bottom_limit": bottom_limit
    } 

def get_table_data(document): 
    """Extracts table data from the document, focusing on total rows, total columns, and table boundaries."""
    tables_data = []  # List to hold all tables' data extracted from the document

    # Iterate through each page in the document
    for page in document.pages:
        # Check if the page has tables
        if page.tables:
            # Iterate through each table on the page
            for table in page.tables:
                # Initialize structure to hold data for the current table
                table_dict = {
                    "total_rows": len(table.body_rows) + len(table.header_rows),
                    "total_cols": 0,  # Will be updated based on the number of columns
                    "table_limits": None,  # To store the table boundaries
                }

                # Extract table boundaries
                if table.layout.bounding_poly:
                    table_dict["table_limits"] = get_boundaries_limits(table.layout.bounding_poly)

                # Determine the maximum number of columns in any row to estimate total columns
                # This involves checking both header and body rows
                max_cols = 0
                # Using itertools.chain to iterate over both header and body rows without explicit conversion
                for row in itertools.chain(table.header_rows, table.body_rows):
                    max_cols = max(max_cols, len(row.cells))
                table_dict["total_cols"] = max_cols

                # Append the table's information to the tables_data list
                tables_data.append(table_dict)

    return tables_data

def get_row_data(document): 
    """Extracts row data from each table in the document, including row limits."""
    row_data = []

    # Iterate over all pages in the document
    for page in document.pages:
        # Check if the page has tables
        if page.tables:
            # Iterate over each table on the page
            for table in page.tables:
                # Iterate over each body row in the table
                for row_index, row in enumerate(table.body_rows):
                    # Initialize a dictionary to store data for the current row
                    row_dict = {
                        "row_index": row_index,  # The index of the row within its table
                        "row_first_cell_text": None,  # Will store text from the row's first cell, if available
                        "row_limits": None  # Will store spatial limits of the row, calculated below
                    }

                    # Check if the row contains any cells and extract text from the first one
                    if row.cells:
                        first_cell = row.cells[0]  # Assuming the first cell is representative for the row
                        row_dict["row_first_cell_text"] = text_anchor_data_table(first_cell.layout.text_anchor, document.text)

                    # Calculate row limits based on cells' bounding polygons
                    x_mins, x_maxs, y_mins, y_maxs = [], [], [], []
                    for cell in row.cells:
                        if cell.layout.bounding_poly:
                            bounds = get_boundaries_limits(cell.layout.bounding_poly)
                            x_mins.append(bounds["left_limit"]["x_position"])
                            x_maxs.append(bounds["right_limit"]["x_position"])
                            y_mins.append(bounds["top_limit"]["y_position"])
                            y_maxs.append(bounds["bottom_limit"]["y_position"])
                    
                    # Update row limits if there are any cells in the row
                    if x_mins and x_maxs and y_mins and y_maxs:
                        row_dict["row_limits"] = {
                            "left_limit": min(x_mins),
                            "right_limit": max(x_maxs),
                            "top_limit": min(y_mins),  # The minimum y_min gives the top boundary of the row.
                            "bottom_limit": max(y_maxs)  # The maximum y_max gives the bottom boundary of the row.
                        }
                    else:
                        # Consider explicitly handling rows without any cells or without bounding polygons
                        row_dict["row_limits"] = {"left_limit": None, "right_limit": None, "top_limit": None, "bottom_limit": None}

                    # Append the row's data to the row_data list
                    row_data.append(row_dict)

    return row_data

def get_col_data(document): 
    """Extracts column data from the single table in the document, including column texts and limits."""
    col_data = []

    # Check if the first page has tables
    if not document.pages[0].tables:
        return col_data  # Return empty list if no tables found
    
    table = document.pages[0].tables[0] # Assuming there is exactly one table in the document
    num_cols = len(table.body_rows[0].cells) # Number of columns determined from the body row

    for col_index in range(num_cols):
        # Initialize col_dict for the current column
        col_dict = {
            "col_index": col_index,
            "col_cell_text": None,
            "col_limits": {
                "left_limit": None,
                "right_limit": None,
                "top_limit": None,
                "bottom_limit": None
            }
        }

        # Extract column text from the header row cell
        header_cell = table.header_rows[0].cells[col_index]
        col_dict["col_cell_text"] = text_anchor_data_table(header_cell.layout.text_anchor, document.text)
        
        # Initialize variables to track column limits
        x_mins, x_maxs, y_mins, y_maxs = [], [], [], []

        # Add header cell boundaries to lists
        if header_cell.layout.bounding_poly:
            bounds = get_boundaries_limits(header_cell.layout.bounding_poly)
            x_mins.append(bounds["left_limit"]["x_position"])
            x_maxs.append(bounds["right_limit"]["x_position"])
            y_mins.append(bounds["top_limit"]["y_position"])
            y_maxs.append(bounds["bottom_limit"]["y_position"])
            
        # Iterate over body rows to update column limits
        for row in table.body_rows:
            if col_index < len(row.cells):
                cell = row.cells[col_index]
                if cell.layout.bounding_poly:
                    bounds = get_boundaries_limits(cell.layout.bounding_poly)
                    x_mins.append(bounds["left_limit"]["x_position"])
                    x_maxs.append(bounds["right_limit"]["x_position"])
                    y_mins.append(bounds["top_limit"]["y_position"])
                    y_maxs.append(bounds["bottom_limit"]["y_position"])

        # Update column limits in col_dict
        col_dict["col_limits"]["left_limit"] = min(x_mins) if x_mins else None
        col_dict["col_limits"]["right_limit"] = max(x_maxs) if x_maxs else None
        col_dict["col_limits"]["top_limit"] = min(y_mins) if y_mins else None
        col_dict["col_limits"]["bottom_limit"] = max(y_maxs) if y_maxs else None

        # Append the column's data to col_data list
        col_data.append(col_dict)

    return col_data

def get_cell_data(document):
    """
    Extracts detailed cell data from each table in the document, using attribute access for a cleaner approach.
    """
    all_cell_data = []

    for page in document.pages:
        if page.tables:
            for table in page.tables:
                total_header_rows = len(table.header_rows)
                # Unified processing for both header and body rows for consistency
                for is_header, rows in ((True, table.header_rows), (False, table.body_rows)):
                    for row_index, row in enumerate(rows, start=(0 if is_header else total_header_rows)):
                        for col_index, cell in enumerate(row.cells):
                            # Assuming text_anchor_data_table and get_boundaries_limits are correctly defined
                            cell_text_data = text_anchor_data_table(cell.layout.text_anchor, document.text)
                            cell_boundaries = get_boundaries_limits(cell.layout.bounding_poly) if cell.layout.bounding_poly else None
                                               
                            # Create and append cell data within the correct scope
                            cell_data = {
                                "row_type": "header" if is_header else "body",
                                "row_index": row_index,
                                "col_index": col_index,
                                "cell_data": {
                                    "cell_content": cell_text_data,
                                    "cell_extraction_confidence": cell.layout.confidence if hasattr(cell.layout, 'confidence') else None,
                                    "cell_limits": cell_boundaries
                                }
                            }
                            all_cell_data.append(cell_data)

    return all_cell_data

if __name__ == "__main__":
    # Load processor configuration
    # Assuming this script is located in h24_ai_app, directly find the keys directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Navigate to the parent directory of the current directory to then access the 'keys' folder
    parent_dir = os.path.dirname(current_dir)
    keys_dir = os.path.join(parent_dir, 'keys') # This now correctly points to h24_ai_app/keys
        
    config_path = os.path.join(keys_dir, 'ml_tabular_config.json')
    try:
        config = load_config(config_path)
    except FileNotFoundError:
        logging.error(f"Configuration file not found in {config_path}")
        sys.exit(1)
    
    if len(sys.argv) < 2:
        logging.error("Error: Expects to receive a PDF file as an argument from the main script. Usage: python main_script_name.py path_to_pdf_document")
        sys.exit(1)    
        
    file_path = sys.argv[1]
    file_name = os.path.basename(file_path)      
          
    # Process document
    
    try:
        document = online_process(config['PROJECT_ID'], config['LOCATION'], config['PROCESSOR_ID'], file_path, MIME_TYPE)
    except GoogleAPICallError as e:
        logging.error(f"API call failed: {e.message}")
        sys.exit(1)
    except RetryError as e:
        logging.error(f"Request to Document AI exceeded retry limits: {e.message}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)
    
    
    # Extract data
    table_data = get_table_data(document)
    col_data = get_col_data(document)
    row_data = get_row_data(document) 
    cell_data = get_cell_data(document)

    # Assemble JSON response
    table_data = {
        "processor": 'ml_tabular_ext',
        "file_name": file_name,
        "table_entities": {
            "table_data": table_data,
            "column_data": col_data,
            "row_data": row_data,
            "content_data": cell_data
        }
    }
    
    # Write the results to a JSON format
    # Convert document_data to a JSON string
    json_table_data = json.dumps(table_data, indent=4)
       
    # Print the JSON string to standard output
    print(json_table_data)
    
    logging.info("Table results processed.")

