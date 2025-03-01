'''Implementating a environment test.
'''
import sys
import os

import unittest
import numpy as np
import pandas as pd

class TestEnvironment(unittest.TestCase):
    ''' Test the environment for the project.
    '''
    def test_pandas(self):
        ''' Test the pandas library.
        '''
        df = pd.DataFrame(np.random.randn(10,5))
        self.assertEqual(df.shape, (10,5))

    def test_numpy(self):
        ''' Test the numpy library.
        '''
        a = np.array([1,2,3,4,5])
        self.assertEqual(a.shape, (5,))

    def test_python_version(self):
        ''' Test the python version.
        '''
        self.assertGreater(sys.version_info, (3, 12))

    def test_env_vars_google_api_key(self):
        ''' Test the google_api_key.
        '''
        GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
        length_of_the_key = len(GOOGLE_API_KEY)
        self.assertGreater(length_of_the_key, 0)

    def test_env_vars_langchain_api_key(self):
        ''' Test the langchain_api_key.
        '''
        LANGCHAIN_API_KEY = os.environ.get("LANGCHAIN_API_KEY")
        length_of_the_key = len(LANGCHAIN_API_KEY)
        self.assertGreater(length_of_the_key, 0)
    
    def test_env_vars_langchain_tracing(self):
        ''' Test the langchain_tracing.
        '''
        LANGSMITH_TRACING = os.environ.get("LANGSMITH_TRACING")
        length_of_tracing = len(LANGSMITH_TRACING)
        self.assertGreater(length_of_tracing, 0)
    
    def test_env_vars_google_api_key(self):
        ''' Test the google_api_key.
        '''
        LANGSMITH_ENDPOINT = os.environ.get("LANGSMITH_ENDPOINT")
        length_of_endpoint = len(LANGSMITH_ENDPOINT)
        self.assertGreater(length_of_endpoint, 0)

if __name__ == '__main__':
    unittest.main()
