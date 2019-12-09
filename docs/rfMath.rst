Math Models
=========================================


.. contents:: :local:


Constants
---------------------

In our RF-Math Module there are some constants defined:

.. code-block:: python
    :linenos:

    T0 = np.float(290)
    N0 = np.float(10*np.log10(constants.k * 290 * 1 * 1000))

Parameter
-------------------

Gain
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The gain gets calculated from the given parameter from each device.
The values are linear interpolated between the given frequency points.

Noise Temperature / Noise Figure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The noise parameter are internally calculated as noise-temperature.
All other noise parameter are converter from the noise-temperature to their scale.

.. automethod:: rf_linkbudget.RFMath.convert_T_n

.. automethod:: rf_linkbudget.RFMath.convert_T_NF


Output Power
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The output power is simply the input power multiplied by the gain

P1dB
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The output P1 parameter is simplistic modeled. It's just a saturating upper bound.

OIP3
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The OIP3 resp. IP3 in general is calculated by the famous equation:

.. code-block:: python
    :linenos:

    IP3 = P - (2*(IP3) - P + 6)

It is assumed a single CW signal (thus the +6dB)

SNR
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The signal-to-noise ratio is exactly the signal - noise in dB.

SFDR
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The spurious-dynamic range uses a simple approach and is the distance between output power and intermodulation 3 product.

Dynamic Range
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The dynamic range is defined as the smaller of the SNR or SFDR.
