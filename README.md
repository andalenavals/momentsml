MomentsML
=========

This repository contains a python shear measurement toolbox and scripts accompanying the paper "Weak-lensing shear measurement with machine learning: Teaching artificial neural networks about feature noise" (https://arxiv.org/abs/1807.02120).

Note that this code is provided for demonstration and prototyping purposes. It is not designed to be integrated into any shear measurement pipeline.

Dependencies
------------

The code depends on:

 * python 2.7, with the usual numpy, scipy, and matplotlib
 * GalSim
 * Astropy


Installation
------------

We recommend to simply add the location of your clone of this directory to your PYTHONPATH.

If you use bash, you could for instance add the following line to your ``.bash_profile`` or ``.profile`` or equivalent::

	export PYTHONPATH=${PYTHONPATH}:/path/to/momentsml/



Directory structure
-------------------

- **momentsml**: the python package
- **scripts**: scripts and configurations to reproduce the results from our paper
- **wrappers**: standalone packages providing interfaces to specific datasets
- **tests**: additional test and demonstration scripts
