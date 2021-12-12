import unittest
import numpy as np
import rf_linkbudget as rf


class TestCircuit(unittest.TestCase):


    def test_SourceN0(self):

        cr = rf.Circuit('Example')
        src = rf.Source("Source")
        sink = rf.Sink("Sink")

        src['out'] >> sink['in']

        # create callback function
        def cb_src(self, f, p):
            return {'f': f, 'p': p, 'Tn': rf.RFMath.T0}

        src['out'].regCallback(cb_src)

        cr.finalise()

        sim = cr.simulate(network=cr.net,
                        start=cr['Source'],
                        end=cr['Sink'],
                        freq=[0],
                        power=[0])

        sim.setNoiseBandwidth(1)

        assert sim.extractValues('Tn', freq=0, power=0)[1][0] == rf.RFMath.T0
        assert sim.extractValues('Tn', freq=0, power=0)[1][1] == rf.RFMath.T0

        assert sim.extractValues('n', freq=0, power=0)[1][0] == rf.RFMath.N0
        assert sim.extractValues('n', freq=0, power=0)[1][1] == rf.RFMath.N0

        assert sim.extractValues('NF', freq=0, power=0)[1][0] == 0
        assert sim.extractValues('NF', freq=0, power=0)[1][1] == 0

    def test_Lna1dB(self):

        cr = rf.Circuit('Example')
        src = rf.Source("Source")
        lna = rf.Amplifier("LNA",
                       Gain=20,
                       NF=1,
                       OP1dB=20,
                       OIP3=40)
        sink = rf.Sink("Sink")

        src['out'] >> lna['in']
        lna['out'] >> sink['in']

        # create callback function
        def cb_src(self, f, p):
            return {'f': f, 'p': p, 'Tn': rf.RFMath.T0}

        src['out'].regCallback(cb_src)

        cr.finalise()

        sim = cr.simulate(network=cr.net,
                        start=cr['Source'],
                        end=cr['Sink'],
                        freq=[0],
                        power=[0])

        sim.setNoiseBandwidth(1)

        assert sim.extractLastValues('n', freq=0, power=0) == (rf.RFMath.N0 +20 +1)
        assert np.round(sim.extractLastValues('NF', freq=0, power=0),decimals=4) == 1

    def test_Attenuator10dB(self):

        cr = rf.Circuit('Example')
        src = rf.Source("Source")
        att = rf.Attenuator("Attenuator",
                        Att=np.array([10])
                        )
        sink = rf.Sink("Sink")

        src['out'] >> att['in']
        att['out'] >> sink['in']

        # create callback function
        def cb_src(self, f, p):
            return {'f': f, 'p': p, 'Tn': rf.RFMath.T0}

        src['out'].regCallback(cb_src)

        cr.finalise()

        sim = cr.simulate(network=cr.net,
                        start=cr['Source'],
                        end=cr['Sink'],
                        freq=[0],
                        power=[0])

        sim.setNoiseBandwidth(1)

        assert sim.extractLastValues('n', freq=0, power=0) == rf.RFMath.N0
        assert np.round(sim.extractLastValues('NF', freq=0, power=0),decimals=4) == 10

if __name__ == '__main__':
    unittest.main()
