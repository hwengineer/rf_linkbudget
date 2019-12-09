Analyse and Plotting
=========================================

.. We have several possibilities to analyse our data.
.. We can scale the noise-bandwidth after the simulation to adapt to conditions of interest
.. Also we got several plot which can show us interesting relationships.


We go back to our first example:

.. literalinclude:: code/example1.py
   :language: python
   :linenos:

We focus now on the last part after finalise()

.. code-block:: python
    :linenos:

    sim = cr.simulate(network=cr.net,
                  start=cr['Source'],
                  end=cr['Sink'],
                  freq=[100e6],
                  power=np.arange(-50, -10, 1.0))

    h = sim.plot_chain(['p'])

    plt.show()

We see the call to the Circuit.simulate() function.
With this we create a simulation-result type.
For the calculation we have our circuit **cr** and as first parameter we have to define a route or network through our circuit.
We have to explicit state with which node we start and where to end.
And then we can define the frequency and input power points we want to calculate our results.

The next command `h = sim.plot_chain(['p'])` is a plotting command and will be discussed later.
The `plt.show()` is a special plotting command which commands that the plotting windows are getting drawn.
But it blocks the current instance. Thats why we always set this command to the end of the script.

.. plot:: code/example1.py

Here we see a simple plot. a so called `sim.plot_chain()`.
"chained" because we see all the components in a signal chain, device after device.
We see on the right side also some text information:

- `p`
- 100.00MHz
- -50.0dBm

the p is the current viewed variable, the middle is the current active frequency and the last one the current input power level.
On some plots these items are clickable and will change when clicked or the mouseweel is used.

We will see more infos in a second.

.. contents:: :local:

Plotting
--------


plot_chain
^^^^^^^^^^

As we already saw, one of the plotting commands is called **plot_chain**.
With this plot we see all the data-chain at a specific input frequency and at a specific power.
This is a good view to analyse a system by scrolling through all the states and observe the hole component chain.

.. automethod:: rf_linkbudget.simResult.plot_chain

plot_total
^^^^^^^^^^

In contrast to plot_chain we have the **plot_total** function.
With this we see all the values at the end of the chain.
The *conclusion* in some kind.
We see a hole input power level sweep at a give frequency or a frequency sweep at a given input power.

With this kind of plot we can easily see the performance over the hole input range for a system.

.. automethod:: rf_linkbudget.simResult.plot_total

plot_total_simple
^^^^^^^^^^^^^^^^^

Whereas the plot_total is an interactive window with clickable buttons, this **plot_total_simple** is static, more simplistic but gives the possibility to compare two different systems with each other.

For many RF application this plot together with the values 'SNR' and 'SFDR' resp. 'Dynamic' is a very informative plot to see where we loose SNR or Dynamic and vice versa where we got a sweetspot for both parameters.

.. automethod:: rf_linkbudget.simResult.plot_total_simple

plot_surface
^^^^^^^^^^^^

The **plot_surface** is used as a hole view to see the system at all input frequencies versus all input power levels at the same time.

.. automethod:: rf_linkbudget.simResult.plot_surface


setNoiseBandwidth
-----------------

We can adjust the noise-bandwidth of our system to adapt to our simulation needs.
The script calculates internally in **1Hz** resolution but shall be adjusted with this function.

.. automethod:: rf_linkbudget.simResult.setNoiseBandwidth


extract measurement data
------------------------

extractValues
^^^^^^^^^^^^^

.. automethod:: rf_linkbudget.simResult.extractValues

extractLastValues
^^^^^^^^^^^^^^^^^

.. automethod:: rf_linkbudget.simResult.extractLastValues
