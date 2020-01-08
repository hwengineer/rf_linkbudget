import sys
sys.path.append(".")
import rf_linkbudget as rf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def example():

    cr = rf.Circuit('Example')

    dup = rf.Attenuator("Duplexer",
                        Att=[1.5])

    lim = rf.Attenuator("Limiter",
                        Att=np.array([0.5, 6.5, 12.5, 18.5]),
                        IIP3=60,
                        OP1dB=30)

    sw1 = rf.SPDT("SW 1",
                  Att=0.3)

    lna = rf.Amplifier("LNA",
                       Gain=[(0, 18.2)],
                       NF=0.7,
                       OP1dB=21.5,
                       OIP3=40)

    sw2 = rf.SPDT("SW 2",
                  Att=0.3)

    att_fix = rf.Attenuator("Att Fix1",
                            Att=[1.5])

    rxfilt = rf.Attenuator("Rx Filter",
                           Att=[2.0])

    att_fix2 = rf.Attenuator("Att Fix2",
                             Att=[1.5])

    driver = rf.Amplifier("Driver",
                          Gain=[(0, 14.9)],
                          NF=1.7,
                          OP1dB=21.4,
                          OIP3=40)

    dsa = rf.Attenuator("DSA",
                        Att=np.arange(1.0, 29, 1.0))

    adc = rf.Amplifier("ADC",
                       Gain=[(0, 0)],
                       OP1dB=-1,
                       OIP3=34,
                       NF=19)

    src = rf.Source("Source")
    sink = rf.Sink("Sink")

    src['out'] >> dup['in']
    dup['out'] >> lim['in']
    lim['out'] >> sw1['S']

    sw1['S-1'] >> lna['in']
    lna['out'] >> sw2['S-1']
    sw1['S-2'] >> sw2['S-2']

    sw2['S'] >> att_fix['in']
    att_fix['out'] >> rxfilt['in']
    rxfilt['out'] >> att_fix2['in']
    att_fix2['out'] >> driver['in']
    driver['out'] >> dsa['in']
    dsa['out'] >> adc['in']
    adc['out'] >> sink['in']

    # create callback function
    def cb_src(self, f, p):
        return {'f': f, 'p': p}

    src['out'].regCallback(cb_src)

    # create callback function
    def cb_lim(self, f, p):
        tb = {-31: 6, -30: 6, -29: 6, -28: 6, -27: 6, -26: 6, -25: 12, -24: 12, -23: 12, -22: 12, -21: 12, -20: 12, -19: 18, -18: 18, -17: 18, -16: 18, -15: 18, -14: 18, -13: 18, -12: 18, -11: 18, -10: 18,}
        if(p in tb):
            self.setAttenuation(tb[p])
        else:
            self.setAttenuation(0.0)
        return {}

    lim['in'].regCallback(cb_lim)

    # create callback function
    def cb_dsa(self, f, p):
        tb = {-37: 0, -36: 1, -35: 2, -34: 3, -33: 4, -32: 5, -31: 0, -30: 1, -29: 2, -28: 3, -27: 4, -26: 5, -25: 0, -24: 1, -23: 2, -22: 3, -21: 4, -20: 5, -19: 0, -18: 1, -17: 2, -16: 3, -15: 4, -14: 5, -13: 6, -12: 7, -11: 8, -10: 9,}
        if(p in tb):
            self.setAttenuation(tb[p])
        else:
            self.setAttenuation(0)
        return {}

    dsa['in'].regCallback(cb_dsa)

    # create callback function
    def cb_sw1(self, f, p):
        if(p > -11):
            self.setDirection('S-2')
        else:
            self.setDirection('S-1')
        return {}

    sw1['S'].regCallback(cb_sw1)
    sw2['S'].regCallback(cb_sw1)

    cr.finalise()

    return cr


if __name__ == "__main__":

    # define circuit
    cr1 = example()

    # simualte
    sim1 = cr1.simulate(network=cr1.net,
                        start=cr1['Source'],
                        end=cr1['Sink'],
                        freq=[0],
                        power=np.arange(-50, -10, 1.0))

    # key's of interest
    keys1 = [cr1['Source']['out'],
             cr1['Duplexer']['out'],
             cr1['Limiter']['out'],
             cr1['SW 1']['S'],
             cr1['SW 1']['S-1'],
             cr1['LNA']['out'],
             cr1['SW 2']['S'],
             cr1['Att Fix1']['out'],
             cr1['Rx Filter']['out'],
             cr1['Att Fix2']['out'],
             cr1['Driver']['out'],
             cr1['DSA']['out'],
             cr1['ADC']['out'],
             cr1['Sink']['in']]

    # set noise bandwidth to smallest subband
    sim1.setNoiseBandwidth(15e3)

    # plot system parameter
    k = sim1.plot_total(['DYN'])
    # h = sim1.plot_chain(keys=keys1)
    #
    # h = sim1.plot_chain(['p'], keys=keys1)
    # t = sim1.plot_total_simple(['SFDR', 'SNR', 'DYN'], freq=0)
    # y = sim1.plot_total_simple(['NF'], freq=0)
    # y = sim1.plot_total_simple(['p'], freq=0)

    # l = sim1.plot_surface(keys=keys1)

    plt.show()
