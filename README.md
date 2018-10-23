MomentsML
=========

This repository contains a python package and scripts accompanying the paper "Weak-lensing shear measurement with machine learning: Teaching artificial neural networks about feature noise" (Tewes et al. 2018, [arXiv:1807.02120](https://arxiv.org/abs/1807.02120), [paper website](https://astro.uni-bonn.de/~mtewes/ml-shear-meas/)). Together with the neural network package [tenbilac](https://github.com/mtewes/tenbilac) (and a decent computing server) this code allows to reproduce all results from the paper.

Dependencies
------------

The code depends on:

 * python 2.7, with numpy, scipy, and matplotlib
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
- **wrappers**: standalone packages providing interfaces to specific datasets (see tutorial)
- **other**: additional figures and demonstration scripts


Getting started
---------------

### Setup

The CPU and disk space requirements vary widely between the different applications described in the paper. For first experiments similar to what is shown in Section 6 of the paper, a server with at least 16 cores and a few hundred GB of disk space should be sufficient.

To begin, add the tenbilac and momentsml packages to your PYTHONPATH as described above (for momentsml) and [here](https://github.com/mtewes/tenbilac) (for tenbilac).
If you plan to process GREAT3 data, do the same with the momentsmlgreat3 wrapper, as described in [wrappers/](wrappers/).
