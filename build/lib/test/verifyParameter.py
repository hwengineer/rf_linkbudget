import unittest
import numpy as np
import rf_linkbudget as rf


class TestComponents(unittest.TestCase):

    def setUp(self):
        pass

    def test_VerifyParameterNumListOfTuples(self):
        cls = rf.VerifyParameterType().verify([(0, 0)])
        self.assertEqual(cls, rf.VerifyParameterNumListOfTuples)

    def test_VerifyParameterNumList(self):
        cls = rf.VerifyParameterType().verify([0, 0])
        self.assertEqual(cls, rf.VerifyParameterNumList)

    def test_VerifyParameterNumListSingleEntry(self):
        cls = rf.VerifyParameterType().verify([0])
        self.assertEqual(cls, rf.VerifyParameterNumListSingleEntry)

    def test_VerifyParameterNumSingleValue(self):
        cls = rf.VerifyParameterType().verify(0)
        self.assertEqual(cls, rf.VerifyParameterNumSingleValue)


if __name__ == '__main__':
    unittest.main()
