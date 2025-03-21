"""Implementating a environment test.
"""
import sys
import os

import unittest
from dotenv import load_dotenv

import numpy as np
import pandas as pd
import google.generativeai as genai


class TestEnvironment(unittest.TestCase):
    """ Test the environment for the project.
    """
    def test_pandas(self):
        """ Test the pandas library.
        """
        df = pd.DataFrame(np.random.randn(10,5))
        self.assertEqual(df.shape, (10,5))

    def test_numpy(self):
        """ Test the numpy library.
        """
        a = np.array([1,2,3,4,5])
        self.assertEqual(a.shape, (5,))

    def test_python_version(self):
        """ Test the python version.
        """
        self.assertGreater(sys.version_info, (3, 12))

    def test_env_vars_google_api_key(self):
        """ Test the google_api_key.
        """
        load_dotenv()
        google_api_key = os.environ.get("GOOGLE_API_KEY")
        length_of_the_key = len(google_api_key)
        self.assertEqual(length_of_the_key, 39)

    def test_env_vars_langchain_api_key(self):
        """ Test the langchain_api_key.
        """
        load_dotenv()
        langchain_api_key = os.environ.get("LANGCHAIN_API_KEY")
        length_of_the_key = len(langchain_api_key)
        self.assertGreater(length_of_the_key, 0)

    def test_env_vars_langsmith_tracing(self):
        """ Test the langsmith_tracing.
        """
        load_dotenv()
        langsmith_tracing = os.environ.get("LANGSMITH_TRACING")
        length_of_tracing = len(langsmith_tracing)
        self.assertGreater(length_of_tracing, 0)

    def test_env_vars_langsmith_endpoint(self):
        """ Test the google_api_key.
        """
        load_dotenv()
        langsmith_endpoint = os.environ.get("LANGSMITH_ENDPOINT")
        length_of_endpoint = len(langsmith_endpoint)
        self.assertGreater(length_of_endpoint, 0)

    def test_gen_ai_connection(self):
        """ Test whether we connect to the google genai
        """
        load_dotenv()
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

        models_list = genai.list_models()
        test_result = False
        for model in models_list:
            if model.name == "models/gemini-2.0-flash-001":
                test_result = True
        self.assertTrue(test_result)

if __name__ == "__main__":
    unittest.main()
