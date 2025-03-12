"""
Testing the extract_text_from_pdf function which returns a list of strings
"""
import os

import unittest

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from experimental_llm_manager import extract_text_from_pdf, parse_bill_info, chunk_pdf_pages


class TestPdfExtraction(unittest.TestCase):
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

class TestLlmModel(unittest.TestCase):
    """
    General unittests for llm_manager
    """

    def setUp(self):
        self.pdf_path = './pdfs/Texas/HB 186 Social_media_children.pdf'
        self.bill_info = {}

    def test_parse_bill_info(self):
        """
        Test whether parse_bill_info produces expected results.
        """

        self.pages_of_pdf = extract_text_from_pdf(self.pdf_path)
        full_pdf_text = "\n".join(self.pages_of_pdf)
        self.bill_info = parse_bill_info(full_pdf_text)

        self.assertEqual(len(self.bill_info.keys()), 5)
        self.assertEqual(self.bill_info['State'], 'Texas')
        self.assertEqual(self.bill_info['Title'], 'Texas: Act prohibiting social media use by children')
        self.assertEqual(self.bill_info['Date'], '09012025')
        self.assertEqual(self.bill_info['Type'], 'State level sectoral')
        self.assertEqual(self.bill_info['Sector'], 'Children’s Data Protection')

    def test_chunk_pdf_pages(self):
        """
        Test whether chunk_pdf_pages produces expected results.
        """
        if len(self.bill_info) == 0:
            self.test_parse_bill_info()
        else:
            pass
        chunk_texts, chunk_metadatas = chunk_pdf_pages(self.pages_of_pdf, self.pdf_path)
        for chunck_text in chunk_texts:
            self.assertLessEqual(len(chunck_text), 800)
        
        self.assertEqual(len(chunk_metadatas), len(chunk_texts))
        max_page =max([int(metadata['Page']) for metadata in chunk_metadatas])
        self.assertEqual(max_page, len(self.pages_of_pdf))
        # return chunk_texts



if __name__ == '__main__':
    unittest.main()
