import sys
sys.path.append(".")
import rf_linkbudget as rf
import matplotlib.pyplot as plt
import numpy as np

cr = rf.Circuit('Mixer')

lna = rf.Amplifier("LNA TQL9066",
                   Gain=[(0, 18.2)],
                   NF=0.7,
                   OP1dB=21.5,
                   OIP3=40)

mix = rf.Mixer("MIY SYM-18+",
               Gain=[(0, -8.61), (100, -8.41), (200, -8.64)],
               OP1dB=14,
               OIP3=30)

src = rf.Source("Source")
sink = rf.Sink("Sink")

src['out'] >> lna['in']
lna['out'] >> mix['in']
mix['out'] >> sink['in']


# create callback function
def cb_src(self, f, p):
    return {'f': f, 'p': p, 'Tn': rf.RFMath.T0}


src['out'].regCallback(cb_src)  # connect callback to Port


# create callback function
def cbI_mix(self, data, f, p):
    # upconverter with flo = 100MHz
    data.update({'f': f + 100e6})
    # add 3dB noise Figure due to sideband noise
    data.update({'Tn': data['Tn'] + (10**(3/10) * rf.RFMath.T0 - rf.RFMath.T0)})
    return data


mix['in'].regCallback_preIteration(cbI_mix)  # connect callback to Port

cr.finalise()


sim = cr.simulate(network=cr.net,
                  start=cr['Source'],
                  end=cr['Sink'],
                  freq=[100e6],
                  power=np.arange(-50, -10, 1.0))

h = sim.plot_chain(['p'])

plt.show()
