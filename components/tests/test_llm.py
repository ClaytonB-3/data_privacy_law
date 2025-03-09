'''Implementating a llm response test.
'''
import sys
import os

import unittest

from experimental_llm_manager import (
    load_faiss_index,
    get_conversational_chain,
    obtain_text_of_chunk,
    llm_simplify_chunk_text,
)

class TestLLM(unittest.TestCase):
    ''' Test the LLM response for the project.
    '''
    def test_faiss_store(self):
        self.faiss_store = load_faiss_index()
        self.assertEqual(df.shape, (10,5))
    def test_response_type(self):
        ''' Test the pandas library.
        '''
        self.faiss_store = load_faiss_index()
        
        self.assertEqual(df.shape, (10,5))
