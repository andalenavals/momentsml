MomentsML
=========

This repository contains a python shear measurement toolbox and scripts accompanying the paper "Weak-lensing shear measurement with machine learning: Teaching artificial neural networks about feature noise" (https://arxiv.org/abs/1807.02120).

Note that this code is provided for demonstration and prototyping purposes. It is not designed to be integrated into any shear measurement pipeline.

Dependencies
------------

The code depends on:

 * python 2.7, with the usual numpy, scipy, and matplotlib
 * [GalSim](https://github.com/GalSim-developers/GalSim)
 * [Astropy](http://www.astropy.org)
 * [tenbilac](https://github.com/mtewes/tenbilac) (for the Machine Learning part)


Installation
------------

We recommend to simply add the location of your clone of this directory to your PYTHONPATH.

To do so, if you use bash, add this line to your ``.bash_profile`` or ``.profile`` or equivalent file:

	export PYTHONPATH=${PYTHONPATH}:/path/to/momentsml/



Directory structure
-------------------

- **momentsml**: the python package
- **scripts**: scripts and configurations to reproduce the results from our paper
- **wrappers**: standalone packages providing interfaces to specific datasets
- **other**: additional figures and demonstration scripts
