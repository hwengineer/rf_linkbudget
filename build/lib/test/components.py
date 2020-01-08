import unittest
import numpy as np
import rf_linkbudget as rf


class TestComponents(unittest.TestCase):

    def setUp(self):
        rf.Circuit("CircuitName")

    def test_createAmplifier(self):
        rf.Amplifier("name",
                     Gain=[(0, 10)],
                     NF=0.5, OP1dB=25, OIP3=35)

    def test_createAttenuator_1(self):
        rf.Attenuator("name",
                      Att=[0])

    def test_createAttenuator_2(self):
        rf.Attenuator("name",
                      Att=np.arange(1, 6, 1))

    def test_createAttenuator_3(self):
        rf.Attenuator("name",
                      Att=np.arange(1, 6, 1),
                      OP1dB=25, IIP3=35)

    def test_Filter(self):
        rf.Filter("name",
                  Att=[(0, 2.0)])

    def test_SPDT(self):
        rf.SPDT("name",
                Att=0.3)

    def test_Source(self):
        rf.Source("Source")

    def test_Sink(self):
        rf.Sink("Sink")


if __name__ == '__main__':
    unittest.main()
