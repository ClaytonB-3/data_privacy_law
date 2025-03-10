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
        google_api_key = os.environ.get("google_api_key")
        length_of_the_key = len(google_api_key)
        self.assertGreater(length_of_the_key, 0)

    def test_env_vars_langchain_api_key(self):
        ''' Test the langchain_api_key.
        '''
        langchain_api_key = os.environ.get("langchain_api_key")
        length_of_the_key = len(langchain_api_key)
        self.assertGreater(length_of_the_key, 0)

    def test_env_vars_langsmith_tracing(self):
        ''' Test the langsmith_tracing.
        '''
        langsmith_tracing = os.environ.get("langsmith_tracing")
        length_of_tracing = len(langsmith_tracing)
        self.assertGreater(length_of_tracing, 0)

    def test_env_vars_langsmith_endpoint(self):
        ''' Test the google_api_key.
        '''
        langsmith_endpoint = os.environ.get("langsmith_endpoint")
        length_of_endpoint = len(langsmith_endpoint)
        self.assertGreater(length_of_endpoint, 0)

if __name__ == '__main__':
    unittest.main()