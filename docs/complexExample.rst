Complex Example
=========================================

.. We have several possibilities to analyse our data.
.. We can scale the noise-bandwidth after the simulation to adapt to conditions of interest
.. Also we got several plot which can show us interesting relationships.


Here we have a more complex example


.. literalinclude:: code/example7.py
    :language: python
    :linenos:
    :lines: 3-157

With the **plot_total** function we can show the NoiseFigure and the Dynamic of the system.

.. plot:: code/example4.py

.. plot:: code/example5.py

We see steps in the noisefigure over the input power level.
We see that these steps are from the limiter attenuator called **lim / Limiter**.
The limiter is in front of the LNA which is not optimal.

We also see that the overall dynamic has losses exactly at the same input levels.
Which is not surprising.

.. plot:: code/example6.py

When we compare the SNR and the SFDR view in a **plot_total_simple** we see something interesting.
We see the sweet spot between SNR and the spurious free dynamic range.
To have an optimal system means we have to optimize the circuit in a way, so that SFDR and SNR are equal over the hole input power range.

SNR / SFDR optimisation
------------------------

To optimize the SNR / SFDR we have to keep the signal power of each component in the eye.

.. plot:: code/example8.py

Here in this plot we got an input power of -32dBm.
The Driver Amplifier is at an output power of approx -6dBm. And the ADC level is approx at -12dBm which leads to approx -13dBFS.
But already with the next higher input power level we have to adjust the ADC input level, otherwise the IM3 components will dominate the hole dynamic.
At -31dBm the limiter was activated and will attenuate approx 6.5dB. We see this in the other figures as the krack in the performance.
But it is necessary. Otherwise the spurious would dominate and our signal would have an overall worse dynamic.

The End
--------

| Thats it for now.
| Have fun with this python package!
