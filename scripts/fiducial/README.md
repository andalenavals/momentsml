Application to the fiducial simulations
=======================================

These scripts implement the application on the "fiducial" simulations, as discussed in Section 6 of the paper.
They all rely on high-level functions of MomentsML, so that rather complicated tasks can be accomplished by little code: most of the content of these scripts is about adjusting settings. 

The general idea is to run the processing scripts (``run_X_blabla.py``) in the order given by their numbers, and to generate test plots with the plotting scripts (``plot_*.py``) or acutal paper figures (``paperfig_*.py``).
While some of these scripts take command line arguments, they are in general meant to be "edited": especially for the plots, some settings need to be changed directly in the scripts to produce the desired figures.

Before describing these scripts and the workflow in more detail, we look at the configuration.


Overview of the configuration
-----------------------------

We suggest that you have a look at the following files, to get a feeling of what's in there:

  - config.py:
  	This is the top-level configuration file. It contains:
  	- paths to the GREAT3 data, what branch and what subfields to process
	- which datasets (defined by "simnames") to use for training and validation (those are defined in run_21_sim.py and simparams.py, described below)
	- which configuration-files to use for the machine learning

	The contents of this config.py will depend on your environment. To get startet, copy one of our configs (e.g., config_cgc.py) into
	config.py and edit the various paths as needed.

  - measfcts.py :
    - settings related to the feature measurements, in particular what should get measured

  - simparams.py :
    - description of the simulations, galaxy parameter distributions 

  - run_21_sim.py :
  	Hardcoded in this script are the descriptions of the structures and sizes of the datasets to be simulated, i.e.
	the definition of the names encountered in config.py.

  - mlconfig/
  	Files in here are configurations for the machine learning with Tenbilac.
	There are two kinds of files:
	- ada*.cfg tell MomentsML what features and inputs should be fed into Tenbilac, and how the predicted output data should be named.
	- sum*.cfg are actual Tenbilac configuration files, with all the Tenbilac settings.



Workflow
--------



Tutorial
--------





To train:
- uncomment a single 


To make the condbias plot with weights:
This plot is made on a "vs"-like data structure.

- set the config.dataset "vo" to the "vs" that you want to use
- set the desired shearconflist and weightconflist
- run valw
- make the condbias plot, with useweights=True






Nov 2017
========

Not a euclid-sized Gaussian PSF, but more a "ground-based" situation, to demonstrate PSF correction clearly.
Sky-limited observations with Gaussian noise
Mostly "uniform" distributions


Manual
------


To experiment with other training parameters for the shear point estimates (but the same training data), make a simlink of the groupmeascat.pkl in another directory within simmeas.


Simulations
-----------

Dataset categories:

  * si : "simulation inspection" : a simple set of galaxies drawn from the parameter distributions, to test feature measurements etc.
  * ts : "train shear" : cases contain always the same galaxy, rotated on a ring
  * vs : "validate shear" : same structure as ts, to probe (conditional) biases of the shear point estimate (without weights)
  * tw : "train weights" : cases contain different galaxies, no SNC.
  * vo : "validate overall" : cases contain different galaxies (potentially with SNC) 


We have several configurations for each category:


Key sets (constant PSF)


ts-2-faint-ln
ts-2-faint-p1 = sims "ts-2-faint-d1" + initial training on ts-2-faint-ln

vs-3-faint

tw-5-faint (with point estimates from ts-2-faint-p1)

vo-3-faint-nosnc



Key sets (variable PSF)

ts-vp-1-ln :
ts-vp-1 : to be done

vs-vp-1 (50 M)


Older sets

ts-1 : 0.25 Mgal
ts-2 : 4 Mgal, 126 GB

vs-1 : for testing plots only
vs-2 : 10 Mgal
vs-3 : 50 Mgal, 1.1 TB, == Thibault's size, less than a night with 50 cpu


tw-1 : 1 Mgal, 32 GB
tw-2 : 10 Mgal, == Thibaults size

vo-1 : 1 Mgal, no SNC
vo-2 : 20 Mgal, 383 GB



Trainings
---------




ts-2 sum55 : 12 hours for 1000 iterations
ts-2 sum5



ts-e-1 sum55 : 3:44 for 1000 iterations 


tw-1 sum55w : 100 its on 1Mgal take 30 min
tw-1 sum55w : 1000 its take 4:40




Plots
-----



Todo
----


vs figure with vs-3 selected by SN > 10 to see if that looks acceptable.

launch ts-3-faint-ln ? fast, can do later.

- decide if min_tru_rad 3 or 4, and then maybe run sims ts-2-large



We generate many realizations per case for the weight training, so that the cost function is dominated by errors made on small/faint galaxies, not by shape noise.
However only few cases are needed, 100 is already large. Maybe 10 would work better (stochastic)
-> running tw-2 to see if it works at all now. No, it didnt, and it takes ages / stops early.

New idea: add more crap galaxies to the training, by lowering the min_tru_sb.
Makes it easier to see/learn the effect of weights

-> see how the trainigs on tw-4-faint look



If everything fails: add SNC to weight training set ?


Running
-------

	
- sim ts-2-easy
	Try to get a decently low contidional bias with this
- sim ts-3-ln
	Meant to be a fast way to generate pre-trained nets
	
Use flux instead of logflux with these, to reduce the impact of differences in low flux values



What I've learnt
----------------

- training ts-2, starting from ts-e-1
	Yes, looks at least as good as starting directly.

Check training on ts-2
-  comparing sum5 and sum55
-> sum55 is better!

Check trainings ts-e-1
- ts-2 or ts-e1
-> ts-e-1 seems better, but maybe ts-2 can still improve ?


- comparing ada4 and ada5
Check (using fast ts-e-1 ?) that ada5s1 is not better than ada4s1.
-> does not seem to make a difference. using ada5 is more straightforward.


--> go for ada5_sum55



To be discussed with Thib
-------------------------

Check that even for ts-e-1, the bright galaxise sometimes make the feature meas fail.
-> yes, this is the case. A bit weird. Make a project to investigate?

Check (using fast ts-e-1 ?) that ada5s1 is not better than ada4s1.

Euclid-like:
  * fix bincenters in conditional bias plots to be the mean x value of the actual points in each bin
  * use plasma_r




