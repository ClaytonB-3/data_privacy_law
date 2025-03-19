"""
Unittest for the functions in llm_mamager.py
"""

import os

import unittest
from unittest.mock import patch, MagicMock

import google.generativeai as genai

from llm_manager.llm_manager import (
    get_conversational_chain,
    get_confirmation_result_chain,
    get_document_specific_summary,
    generate_page_summary,
    )


class TestLLMResponse(unittest.TestCase):
    """
    Test whether LLM Model related funcitons work properly
    """

    @patch("llm_manager.llm_manager.create_stuff_documents_chain")
    @patch("llm_manager.llm_manager.ChatGoogleGenerativeAI")
    @patch("llm_manager.llm_manager.PromptTemplate")
    def test_get_conversational_chain(self, mock_prompt, mock_genai, mock_chain):
        """
        Test get_confirmation_result_chai runs properly

        Args:
            mock_prompt: mock patch for PromptTemplate
            mock_genai: mock genai for ChatGoogleGenerativeAI
            mock_chain: mock chain for create_stuff_documents_chain
        """
        _ = mock_prompt, mock_genai
        get_confirmation_result_chain()
        mock_chain.assert_called_once()


    @patch("llm_manager.llm_manager.create_stuff_documents_chain")
    @patch("llm_manager.llm_manager.ChatGoogleGenerativeAI")
    @patch("llm_manager.llm_manager.PromptTemplate")
    def test_get_confirmation_result_chain(self, mock_prompt, mock_genai, mock_chain):
        """
        Test get_confirmation_result_chai runs properly

        Args:
            mock_prompt: mock patch for PromptTemplate
            mock_genai: mock genai for ChatGoogleGenerativeAI
            mock_chain: mock chain for create_stuff_documents_chain
        """
        _ = mock_prompt, mock_genai
        get_confirmation_result_chain()
        mock_chain.assert_called_once()


    @patch("llm_manager.llm_manager.create_stuff_documents_chain")
    @patch("llm_manager.llm_manager.ChatGoogleGenerativeAI")
    @patch("llm_manager.llm_manager.PromptTemplate")
    def test_get_document_specific_summary(self, mock_prompt, mock_genai, mock_chain):
        """
        Test get_document_specific_summary runs properly

        Args:
            mock_prompt: mock patch for PromptTemplate
            mock_genai: mock genai for ChatGoogleGenerativeAI
            mock_chain: mock chain for create_stuff_documents_chain
        """
        _ = mock_prompt, mock_genai
        get_document_specific_summary()
        mock_chain.assert_called_once()


    @patch("llm_manager.llm_manager.Document")
    @patch("llm_manager.llm_manager.extract_text_from_pdf")
    @patch("llm_manager.llm_manager.get_document_specific_summary")
    def test_generate_page_summary(self, mock_get_doc, mock_extract, mock_doc):
        """
        Test generate_page_summary calls correct times and generates the proper results. 
        """
        test_question = "test question"
        chunk_ids_with_metadata = [
            ("path1", "title1", "1"),
            ("path1", "title1", "2"),
            ("path1", "title1", "3"),
            ("path2", "title2", "1"),
            ("path3", "title3", "1"),
            ("path3", "title3", "2")
        ]
        mock_extract.side_effect = [
            ["path_1_page1_text", "path_1_page2_text", "path_1_page3_text", "path_1_page4_text"],
            ["path_2_page1_text", "path_2_page2_text", "path_2_page3_text"],
            ["path_3_page1_text", "path_3_page2_text", "path_3_page3_text"]
        ]
        records = generate_page_summary(chunk_ids_with_metadata, test_question)
        self.assertEqual(mock_extract.call_count, 3)
        self.assertEqual(mock_get_doc.call_count, len(chunk_ids_with_metadata))
        self.assertEqual(mock_doc.call_count, len(chunk_ids_with_metadata))
        self.assertEqual(len(records), len(chunk_ids_with_metadata))
        for record in records:
            self.assertListEqual(
                list(record.keys()), ["Document", "Page", "Relevant Information", "File Path"]
            )


    def test_llm_response_str(self):
        """
        Test sample inputs and confirm whether the LLM responses are as expected.
        """
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
        mock_doc1 = MagicMock()
        mock_doc1.page_content = """A BILL TO BE ENTITLED\n
AN ACT\n
relating to prohibiting use of social media platforms by children.\n \
BE IT ENACTED BY THE LEGISLATURE OF THE STATE OF TEXAS:\n \
SECTION 1. Chapter 120, Business & Commerce Code, is\n \
amended by adding Subchapter C-1 to read as follows:\n \
SUBCHAPTER C-1. USER AGE LIMITATION\n \
Sec. 120.111. DEFINITIONS. In this subchapter:"""
        mock_doc2 = MagicMock()
        mock_doc2.page_content = """(1) "Account holder" means a resident of this state\n \
who opens an account or creates a profile or is identified by the\n \
social media platform by a unique identifier while using or\n \
accessing a social media platform.\n \
(2) "Child" means an individual who is younger than 18\n \
years of age.\n \
Sec. 120.112. USE BY CHILDREN PROHIBITED. To the extent\n \
permitted by federal law, including the Children's Online Privacy\n \
Protection Act (15 U.S.C. Section 6501 et seq.), a child may not use\n \
a social media platform.\n \
Sec. 120.113. ACCOUNT AND VERIFICATION REQUIREMENTS. (a)\n \
A social media platform shall:"""
        mock_doc3 = MagicMock()
        mock_doc3.page_content = """(1) prohibit a child from entering into a contract\n \
with the social media platform to become an account holder; and\n \
(2) verify that a person seeking to become an account\n \
holder is 18 years of age or older before accepting the person as an\n \
account holder.\n \
(b) A social media platform must use a commercially\n \
reasonable method that relies on public or private transactional\n \
data to verify the age of an individual as required under Subsection\n \
(a).\n \
(c) Personal information obtained under Subsection (b) may\n \
only be used for age verification purposes and may not be retained,\n \
used, transmitted, or otherwise conveyed, regardless of whether\n \
consideration is given for the information. The social media\n \
company must delete personal information immediately upon\n \
completion of the age verification process."""
        docs_for_chain = [mock_doc1, mock_doc2, mock_doc3]

        user_question1 = "Tell me about social media data"
        chain1 = get_conversational_chain()
        firstresult1 = chain1.invoke(
            {"context": docs_for_chain, "question": user_question1}
        )

        chain2 = get_confirmation_result_chain()
        result1 = chain2.invoke(
            {
                "context": docs_for_chain,
                "question": user_question1,
                "answer": firstresult1,
            }
        )
        self.assertGreater(len(firstresult1), 0)
        self.assertGreater(len(result1), 0)
        self.assertTrue(
            """The document database has an answer to your \
question. Here is the structured response based \
on TPLC's database"""
            in result1,
            msg=(result1),
        )

        user_question2 = "Who is the president of USA?"
        chain1 = get_conversational_chain()
        firstresult2 = chain1.invoke(
            {"context": docs_for_chain, "question": user_question2}
        )

        chain2 = get_confirmation_result_chain()
        result2 = chain2.invoke(
            {
                "context": docs_for_chain,
                "question": user_question2,
                "answer": firstresult2,
            }
        )
        self.assertTrue(
            """Sorry, the database does not have specific information about your question"""
            in result2,
            msg=result2,
        )


if __name__ == "__main__":
    unittest.main()
