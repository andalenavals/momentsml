Application to the fiducial simulations
=======================================

These scripts implement the application on the "fiducial" simulations, as discussed in Section 6 of the paper.
They all rely on high-level functions of MomentsML, so that rather complicated tasks can be accomplished by little code: most of the content of these scripts is about adjusting settings. 

The general idea is to run the processing scripts (``run_X_blabla.py``) in the order given by their numbers, and to generate test plots with the plotting scripts (``plot_*.py``) or acutal paper figures (``paperfig_*.py``).
While some of these scripts take command line arguments, they are in general meant to be "edited": especially for the plots, some settings need to be changed directly in the scripts to produce the desired figures.

Before describing these scripts and the workflow in more detail, its good to get a first...


Overview of the configuration
-----------------------------

The following files contain most of the configurable aspects (everything else is hard-coded). We suggest that you have a look a them, to get a first idea of what's in there.

  - ``config.py``:
  	This is the top-level configuration file. It defines
  	- path to a workdir in which all the produced files will be organized
	- names of the various datasets (for training and validation) on which the scripts should run
	- which configuration-files to use for the machine learning


  - ``measfcts.py`` :
    - defines the feature measurement function that will be run on the datasets. 
	
  - ``simparams.py`` :
    - description of the simulation parameters, in particular of the galaxy parameter distributions.
	 
  - ``mlconfig/``
  	Files in here are configurations for the machine learning with tenbilac.
	There are two kinds of files:
	- ``ada*.cfg`` tell MomentsML what features and inputs should be fed into tenbilac, and how the predicted output data should be named.
	- ``sum*.cfg`` are actual Tenbilac configuration files, with all the tenbilac settings (network architecture, cost functions, committees, etc).
	
	Open ``ada5s1f.cfg`` and ``sum55.cfg`` to see two relevant examples.


Workflow
--------

### Simulations

Dataset categories:

  * si : "simulation inspection" : a small set of galaxies drawn from the parameter distributions, to test feature measurements etc.
  * ts : "train shear" : cases contain always the same galaxy, rotated on a ring
  * vs : "validate shear" : same structure as ts, to probe (conditional) biases of the shear point estimate
  * tw : "train weights" : cases contain different galaxies
  * vo : "validate overall" : same as tw, cases contain different galaxies, for an overall validation.





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




### Trainings


To train:
- uncomment a single 


To make the condbias plot with weights:
This plot is made on a "vs"-like data structure.

- set the config.dataset "vo" to the "vs" that you want to use
- set the desired shearconflist and weightconflist
- run valw
- make the condbias plot, with useweights=True




To experiment with other training parameters for the shear point estimates (but the same training data), make a simlink of the groupmeascat.pkl in another directory within simmeas.


ts-2 sum55 : 12 hours for 1000 iterations
ts-2 sum5



ts-e-1 sum55 : 3:44 for 1000 iterations 


tw-1 sum55w : 100 its on 1Mgal take 30 min
tw-1 sum55w : 1000 its take 4:40


### Validation and plots





