# Implementating a pattern test. Use functions in the test.
import unittest
import numpy as np
import pandas as pd
import sys

class TestEnvironment(unittest.TestCase):
    def test_pandas(self):
        df = pd.DataFrame(np.random.randn(10,5))
        self.assertEqual(df.shape, (10,5))
    
    def test_numpy(self):
        a = np.array([1,2,3,4,5])
        self.assertEqual(a.shape, (5,))
    
    def test_python_version(self):
        self.assertGreater(sys.version_info, (3, 12))
        

if __name__ == '__main__':
    unittest.main()