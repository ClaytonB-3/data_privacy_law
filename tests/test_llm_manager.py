"""
Testing the extract_text_from_pdf function which returns a list of strings
"""
import os

import unittest

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from components.experimental_llm_manager import extract_text_from_pdf

class PdfExtractionMethod(unittest.TestCase):
    """
    Testing whether the PDF's extraction function is working properly 
    and giving response in the right format. 

    Args for the function --> pdf_path (str): The path to the PDF file.
    Returns --> list: A list of strings, each representing a page of the PDF file.
    """
    def setUp(self):
        """
        Creating a temporary pdf file with 2 pages to test the extract pdf function"
        """
        self.temp_pdf_path = "pdf_created_for_testing.pdf"
        playground = canvas.Canvas(self.temp_pdf_path, pagesize = letter)

        # Creating the first page
        playground.drawString(100,750, "This is the first page in the project TPLC")
        playground.showPage()

        # Creating the second page
        playground.drawString(100,750, "Second page in the project TPLC")
        playground.save()

    def tearDown(self):
        """
        Deleting the temporary pdf that was created in the setUp function
        """
        if os.path.exists(self.temp_pdf_path):
            os.remove(self.temp_pdf_path)

    def test_pdf_extraction(self):
        """
        Passing the created pdf file to the extract_pdf_function 
        and then comparing the result vs expected
        """
        pages = extract_text_from_pdf(self.temp_pdf_path)

        # Check that the output is a list.
        self.assertIsInstance(pages, list, "The output should be a list.")

        # Check that we have two pages.
        self.assertEqual(len(pages), 2, "There should be 2 pages extracted.")

        # Check that each page is a string.
        for page in pages:
            self.assertIsInstance(page, str, "Each page should be a string.")

        # Verify that expected text appears on each page.
        self.assertIn("This is the first page in the project TPLC",
                      pages[0],
                      "Page 1 text does not match.")
        self.assertIn("Second page in the project TPLC",
                      pages[1],
                      "Page 2 text does not match.")

if __name__ == '__main__':
    unittest.main()
