import re
import easyocr
import numpy as np
from PIL import Image

# Initialize the EasyOCR reader with the desired languages
# This can be done once and reused for all requests for better performance.
try:
    reader = easyocr.Reader(['en'])
except Exception as e:
    print(f"Error initializing EasyOCR: {e}")
    # Handle the error gracefully, e.g., by creating a dummy reader or logging.
    reader = None

def process_image_for_ocr(image_path):
    """
    Extracts text from an image using EasyOCR.
    
    Args:
        image_path (str): The path to the image file.
        
    Returns:
        str: A single string containing all the extracted text.
    """
    if reader is None:
        print("EasyOCR reader is not initialized. Cannot process image.")
        return ""
        
    try:
        # EasyOCR's readtext function is very powerful and handles most pre-processing.
        # It returns a list of tuples, with each tuple containing:
        # ([bounding_box], text, confidence)
        results = reader.readtext(image_path)
        
        # We need to extract the text from the results and join them.
        # Using a newline character to separate lines can help the parser.
        extracted_text = " ".join([text[1] for text in results])
        
        return extracted_text
        
    except Exception as e:
        print(f"Error processing image with EasyOCR: {e}")
        return ""

def parse_transaction_from_text(text):
    """
    Parses OCR text to extract one or more transactions.
    Detects 'income' and 'expense' with nearby numbers.
    """
    transactions = []

    # Regex: optional keyword + optional ₱/PHP/P + number
    pattern = r"(income|expense)?\s*(?:₱|PHP|P)?\s*([\d,]+\.?\d{0,2})"

    matches = re.findall(pattern, text, re.IGNORECASE)

    for keyword, amount_str in matches:
        amount = float(amount_str.replace(",", ""))

        if keyword.lower() == "income":
            t_type = "income"
        elif keyword.lower() == "expense":
            t_type = "expense"
        else:
            # If no explicit keyword, decide default
            t_type = "expense"

        transactions.append({
            "type": t_type,
            "amount": amount,
            "description": f"Scanned {t_type.capitalize()}",
            "source": "OCR Scan"
        })

    # Return list of transactions instead of just one
    return transactions if transactions else None

