'''Implementating a environment test.
'''
import sys

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

if __name__ == '__main__':
    unittest.main()
