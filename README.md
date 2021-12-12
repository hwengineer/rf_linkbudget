# rf-linkbudget

<!-- https://packaging.python.org/tutorials/packaging-projects/ -->

The current Documentation is found under this link : <https://rf-linkbudget.readthedocs.io/en/latest/index.html>

## Abstract
RF-LinkBudget is a software package to aid RF Hardware Developer in defining and comparing LinkBudget’s of RF Ciruits.
It calculates key parameter’s like cumulative Noise Figure, cumulates Gain, Intermodulation Signal Amplitudes and so on.

## Changelog

### 1.1.5
fixed calculation of Noisefigure value.  
Also added noise term in signal source in the examples to clearify how to configure them properly 

### 1.1.4
added feature to use current simulation parameters in a callback function for a switch or attenuator 

### 1.1.3
fixed typo in the `setDirection` function of the SPDT switch

### 1.1.2
added more unit tests  
added more parameter verification  
`SPDT` Switches now have an Iso parameter for an isolation value

### 1.1.1
Updated examples with `Filter` component  
added first bunch of unittests

### 1.1.0
Changed Attenuator OIP3 to IIP3 value.  
This change breaks old scripts!

### 1.0.2
Added `Filter` Component
