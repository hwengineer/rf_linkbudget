.. RF-LinkBudget documentation master file, created by
   sphinx-quickstart on Thu Sep 19 23:00:40 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

RF-LinkBudget
=========================================

Motivation
**********

RF-LinkBudget is a software package to aid RF Hardware Developer in defining
and comparing LinkBudget's of RF Ciruits.

It calculates key parameter's like cumulative Noise Figure, cumulates Gain, Intermodulation Signal Amplitudes
and so on.

Something I often saw was that RF Designer use excel tables for calculating the link budget.
For simple circuits without switches and configurable attenuators that works okay.
But when you have switches which will add or remove an LNA in a signal chain depending on the power level at the input of a specific device, it gets complicated.
You can add this to an excel table but you end up in "if-else" formula hell...
The excel tables itself have limitations: Try to compare two linkbudgets or show a plot with NF over input power (with switched LNA's).

This package will simplify the simulation with link-budgets where attenuators, switches and even mixers are present.

Limitations
***********

It does this with the (to RF Designers) well known approximation formulas.
RF-LinkBudget does **not** simulate a hole RF-Circuit with all S-Parameters and non-linearities.





.. toctree::
   :maxdepth: 2
   :caption: Contents:

   introduction
   rf_linkbudget_circuit
   rfMath
   rfResult
   complexExample


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
