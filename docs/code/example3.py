import sys
sys.path.append(".")
import rf_linkbudget as rf
import matplotlib.pyplot as plt
import numpy as np

cr = rf.Circuit('SimpleEx')

lna = rf.Amplifier("LNA TQL9066",
                   Gain=[(0, 18.2)],
                   NF=0.7,
                   OP1dB=21.5,
                   OIP3=40)

drv = rf.Amplifier("Driver TQP3M9028",
                   Gain=[(0, 14.9)],
                   NF=1.7,
                   OP1dB=21.4,
                   OIP3=40)

src = rf.Source("Source")
sink = rf.Sink("Sink")


src['out'] >> lna['in']
lna['out'] >> drv['in']
drv['out'] >> sink['in']


# create callback function
def cb_src(self, f, p):
    return {'f': f, 'p': p}


src['out'].regCallback(cb_src)  # connect callback to Port

cr.finalise()


sim = cr.simulate(network=cr.net,
                  start=cr['Source'],
                  end=cr['Sink'],
                  freq=[100e6],
                  power=np.arange(-50, -10, 1.0))

h = sim.plot_total(['SFDR'])

plt.show()
