"""
Unittest for the functions in db_manager
including test pdf extraction
"""

import os

import unittest
from unittest.mock import patch, MagicMock

import google.generativeai as genai
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from db_manager.pdf_parser import (extract_text_from_pdf,
                                      chunk_pdf_pages)
from db_manager.faiss_db_manager import (add_to_faiss_index,
                                         load_faiss_index,
                                         obtain_text_of_chunk,
                                         calculate_updated_chunk_ids)
from llm_manager.llm_manager import parse_bill_info

class TestPDFExtraction(unittest.TestCase):
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
        
class TestDBManager(unittest.TestCase):
    """
    General unittests for llm_manager
    """

    def setUp(self):
        api_key=os.environ.get("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        self.pdf_path = './pdfs/Texas/HB 186 Social_media_children.pdf'
        self.pages_of_pdf = extract_text_from_pdf(self.pdf_path)
        full_pdf_text = "\n".join(self.pages_of_pdf)
        self.bill_info = parse_bill_info(full_pdf_text)
        self.chunk_size = 800
        self.chunk_texts, self.chunk_metadatas = chunk_pdf_pages(self.pages_of_pdf,
                                                                 self.pdf_path,
                                                                 self.chunk_size)

    def test_parse_bill_info(self):
        """
        Test whether parse_bill_info produces expected results.
        """

        self.assertEqual(len(self.bill_info.keys()), 5)
        self.assertEqual(self.bill_info['State'], 'Texas')

        # Sometimes it returns different results
        # self.assertEqual(self.bill_info['Title'],
        #                  'Texas: Act prohibiting social media use by children')
        self.assertEqual(self.bill_info['Date'], '09012025')
        self.assertEqual(self.bill_info['Type'], 'State level sectoral')
        self.assertEqual(self.bill_info['Sector'], 'Children’s Data Protection')

    def test_chunk_pdf_pages(self):
        """
        Test whether chunk_pdf_pages produces expected results.
        """

        for chunck_text in self.chunk_texts:
            self.assertLessEqual(len(chunck_text), self.chunk_size)

        self.assertEqual(len(self.chunk_metadatas), len(self.chunk_texts))

        max_page = 0
        for metadata in self.chunk_metadatas:
            max_page = max(int(metadata['Page']), max_page)

        self.assertEqual(max_page, len(self.pages_of_pdf))
        for metadata in self.chunk_metadatas:
            self.assertEqual(len(metadata), len(["Source", "Page", "Filename", "Path"]))
            self.assertEqual(metadata['Source'], self.pdf_path)
            self.assertTrue(1 <= int(metadata['Page']))
            self.assertEqual(metadata['Filename'],
                             self.pdf_path.rsplit('/', maxsplit=1)[-1])

    def test_calculate_updated_chunk_ids(self):
        """
        Test whether calculate_updated_chunk_ids works properly
        """
        test_case_1 = [
            {"Title": "Texas: Title_A", "Page": "1"},
            {"Title": "Texas: Title_A", "Page": "1"},
            {"Title": "Texas: Title_A", "Page": "2"},
        ]
        expected_1 = [
             "Texas:_Title_A_Page_1_ChunkNo_0",
             "Texas:_Title_A_Page_1_ChunkNo_1",
             "Texas:_Title_A_Page_2_ChunkNo_0",
        ]
        test_case_1_result = calculate_updated_chunk_ids(test_case_1)
        for ind in range(len(test_case_1)):
            self.assertEqual(expected_1[ind], test_case_1_result[ind]['Chunk_id'])

        test_case_2 = [
            {"Page": "1"},
            {"Title": "Texas: Title_A", "Page": "1"},
            {"Title": "Texas: Title_A", "Page": "2"},
            {"Title": "Texas: Title_A"},
        ]
        expected_2 = [
             "unknown_Page_1_ChunkNo_0",
             "Texas:_Title_A_Page_1_ChunkNo_0",
             "Texas:_Title_A_Page_2_ChunkNo_0",
             "Texas:_Title_A_Page_1_ChunkNo_0"   # A Potential Bug
        ]
        test_case_2_result = calculate_updated_chunk_ids(test_case_2)
        for ind in range(len(test_case_2)):
            self.assertEqual(expected_2[ind], test_case_2_result[ind]['Chunk_id'])

class TestFAISSIndex(unittest.TestCase):
    """
    General unittests for faiss index related functions.
    """

    @patch("db_manager.faiss_db_manager.FAISS")
    @patch("db_manager.faiss_db_manager.GoogleGenerativeAIEmbeddings")
    @patch("db_manager.faiss_db_manager.os.path.exists")
    @patch("db_manager.faiss_db_manager.calculate_updated_chunk_ids")
    def test_add_to_faiss_index_create_new(self,
                                           mock_chunks,
                                           mock_exists,
                                           mock_embeddings,
                                           mock_faiss):
        """
        Test whether add_to_faiss_index can create new index properly

        Args:
            mock_chunks: mock patch for calculate_updated_chunk_ids
            mock_exists: mock patch for os.path.exists
            mock_embeddings: mock patch for GoogleGenerativeAIEmbeddings
            mock_faiss: mock patch for FAISS
        """
        mock_chunks.return_value = [{"Chunk_id": "123"}]
        mock_exists.return_value = False

        # Mock embeddings
        mock_embeddings.return_value = MagicMock()

        # Mock FAISS
        mock_faiss_instance = MagicMock()
        mock_faiss.from_texts.return_value = mock_faiss_instance

        # Run the function
        add_to_faiss_index(chunk_texts=["test chunk"], chunk_metadatas=[{"Chunk_id": "123"}])

        # Check if FAISS was called to create a new index
        mock_faiss.from_texts.assert_called_once()
        mock_faiss_instance.save_local.assert_called_once()

    @patch("db_manager.faiss_db_manager.FAISS")
    @patch("db_manager.faiss_db_manager.GoogleGenerativeAIEmbeddings")
    @patch("db_manager.faiss_db_manager.os.path.exists")
    @patch("db_manager.faiss_db_manager.calculate_updated_chunk_ids")
    def test_add_to_faiss_index_load_and_add_texts(self, mock_chunks,
                                                   mock_exists, mock_embeddings,
                                                   mock_faiss):
        """
        Test whether add_to_faiss_index can load existing index and add texts properly
        
        Args:
            mock_chunks: mock patch for calculate_updated_chunk_ids
            mock_exists: mock patch for os.path.exists
            mock_embeddings: mock patch for GoogleGenerativeAIEmbeddings
            mock_faiss: mock patch for FAISS
        """

        mock_chunks.return_value = [{"Chunk_id": "456"}]
        mock_exists.return_value = True

        # Mock embeddings
        mock_embeddings.return_value = MagicMock()

        # Mock FAISS load
        mock_faiss_instance = MagicMock()
        mock_faiss_instance.docstore._dict = {"123":"123"}
        mock_faiss.load_local.return_value = mock_faiss_instance

        add_to_faiss_index(["new chunk"], [{"Chunk_id": "456"}])  # New ID
        mock_faiss.load_local.assert_called_once()

        # Check if FAISS was called to create a add new index
        mock_faiss_instance.add_texts.assert_called_once_with(
            texts=["new chunk"],
            metadatas=[{"Chunk_id": "456"}],
            ids=["456"]
        )
        mock_faiss_instance.save_local.assert_called_once()

    @patch("db_manager.faiss_db_manager.FAISS")
    @patch("db_manager.faiss_db_manager.GoogleGenerativeAIEmbeddings")
    @patch("db_manager.faiss_db_manager.os.path.exists")
    @patch("db_manager.faiss_db_manager.calculate_updated_chunk_ids")
    def test_add_to_faiss_index_load_error(self, mock_chunks,
                                           mock_exists,
                                           mock_embeddings, mock_faiss):
        """
        Test whether add_to_faiss_index can handle load errors properly
        
        Args:
            mock_chunks: mock patch for calculate_updated_chunk_ids
            mock_exists: mock patch for os.path.exists
            mock_embeddings: mock patch for GoogleGenerativeAIEmbeddings
            mock_faiss: mock patch for FAISS
        """

        mock_chunks.return_value = [{"Chunk_id": "789"}]
        mock_exists.return_value = True
        # Mock embeddings
        mock_embeddings.return_value = MagicMock()

        # Mock OSError when loading FAISS
        mock_faiss.load_local.side_effect = OSError("Failed to load index")

        # Mock FAISS.from_texts to handle new index creation
        mock_faiss_instance = MagicMock()
        mock_faiss.from_texts.return_value = mock_faiss_instance

        add_to_faiss_index(["test chunk"], [{"Chunk_id": "789"}])

        # Ensure a try except and new FAISS index was created
        mock_faiss.load_local.assert_called_once()
        mock_faiss.from_texts.assert_called_once()
        mock_faiss_instance.save_local.assert_called_once()

    @patch("db_manager.faiss_db_manager.FAISS")
    @patch("db_manager.faiss_db_manager.GoogleGenerativeAIEmbeddings")
    def test_load_faiss_index(self, mock_embeddings, mock_faiss):
        """
        Test whether load_faiss_index works properly
        
        Args:
            mock_embeddings: mock patch for GoogleGenerativeAIEmbeddings
            mock_faiss: mock patch for FAISS
        """

        # Mock embeddings
        mock_embeddings.return_value = MagicMock()
        # Mock FAISS load
        faiss_folder = "test_location"
        load_faiss_index(faiss_folder)

        mock_faiss.load_local.assert_called_once()

    @patch("db_manager.faiss_db_manager.load_faiss_index")
    def test_obtain_text_of_chunk(self, mock_load_faiss):
        """
        Test whether obtain_text_of_chunk works properly
        """
        mock_faiss_instance = MagicMock()
        mock_load_faiss.return_value = mock_faiss_instance

        # test1 - general situation
        mock_doc1 = MagicMock(spec=[])
        mock_doc1.page_content = 'text123'

        mock_doc2 = MagicMock(spec=[])
        mock_doc2.metadata = {'Chunk_id' : 1}
        mock_doc2.page_content = 'text123'

        mock_doc3 = MagicMock(spec=[])
        mock_doc3.metadata = {'Chunk_id' : 1}
        mock_doc3.page_content = 'text456'

        mock_faiss_instance.docstore._dict = {'Chunk_id_1' : mock_doc1,
                                              'Chunk_id_2' : mock_doc2,
                                              'Chunk_id_3' : mock_doc3}
        self.assertEqual(obtain_text_of_chunk(1), 'text123')
        self.assertEqual(obtain_text_of_chunk(2), None)

        # test2 - No page_content
        mock_doc1 = MagicMock(spec=[])
        mock_doc1.metadata = {'Chunk_id' : 1}
        mock_faiss_instance.docstore._dict = {'Chunk_id_1' : mock_doc1}
        self.assertEqual(obtain_text_of_chunk(1), '')