Introduction
=========================================

This tool is used in three phases.

1. | First we define a circuit containing multiple devices.
   | we connect those and maybe define some callback functions.
2. | In the second phase we simulate the circuit, define plots of interest.
3. | And in the third phase we optimize the circuit.

A simple example
----------------

| First we define a simple circuit
| We use two amplifiers in series
| A Low Noise Amp and a Driver


.. literalinclude:: code/example1.py
  :language: python
  :lines: 1-20
  :linenos:


| Now we have to define connections between the devices

.. literalinclude:: code/example1.py
 :language: python
 :lines: 23-25
 :linenos:


| that we can simulate the circuit correctly, we have to define where the signal is applied to.
| A Port as example.
| We do this by using a callback function.
| First we define it with an inline function, then connect this function to the Port by using the memberfunction called **regCallback**.

.. literalinclude:: code/example1.py
    :language: python
    :lines: 28-33
    :linenos:


| after defining all the callbacks we can finalize the circuit

.. code-block:: python
    :linenos:

    cr.finalise()

| and simulate the circuit


.. literalinclude:: code/example1.py
    :language: python
    :lines: 38-46
    :linenos:

| We see that we have to define a start port and an end port.
| In this case its intelligent enough to choose the cr['Source']['out'] port and the cr['Sink']['in'] port.
| Also we have to define the frequency and input power range of the simulation


.. plot:: code/example1.py

| And here we see our output!
| In this case we see the signal power **p** from the source to the sink.
| We can also show other parameters like noisefigure, signal-to-noise ratio, spurious-free-dynamic-range and others.

..   :include-source:
.. https://matplotlib.org/sampledoc/extensions.html


.. literalinclude:: code/example1.py
 :language: python
 :linenos:
