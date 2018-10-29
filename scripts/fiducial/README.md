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

Set the workdir path in ``config.py`` to an empty directory.


### Simulations, with ``run_11_sim.py``

The first step is the generation of data. This involves the use of GalSim to create images, the feature measurement on these images, and the structuring of these features into an astropy Table. All these steps are done by one single script, ``run_11_sim.py``, on each individual data set. In other words, one call to ``run_11_sim.py`` will generate the data to train the point estimator, another call to ``run_11_sim.py`` the data to train the weights, and so on.

The final product of this ``run_11_sim.py`` scirpt is a pickle file containing an astropy Table. This table is structured so that each row corresponds to one _case_. Some columns are multi-dimensional, with the second index pointing at all the _realizations_ of a case. 

When running this script, the generated images will be organized inside ``workdir/sim`` (in a structure involving timestamps), while the final Table is written in ``workdir/simmeas/dataset_name/groupmeascat.pkl``.

Before describing the use of ``run_11_sim.py``, we introduce some abbreviations we use for dataset categories:

  * si : "simulation inspection" : a small set of galaxies drawn from the parameter distributions, to test feature measurements etc.
  * tp : "train point-estimator" : cases contain always the same galaxy, rotated on a ring
  * vp : "validate point-estimator" : same structure as ts, to probe (conditional) biases of the shear point estimate
  * tw : "train weights" : cases contain different galaxies
  * vo : "validate overall" : same as tw, cases contain different galaxies, for an overall validation.

Furthermore, we will use the code "varpsf" for datasets related to the variable psf experiements.


The contents contributing to the configuration of ``run_11_sim.py`` are distributed. They involve the distribution of galaxy parameters from ``simparams.py``, the definition of the features to measure provided via ``measfcts.py``, general settings in ``config.py``, as well as some settings hard-coded in ``run_11_sim.py``.

You will find inside ``run_11_sim.py`` definitions of datasets that group and organize all these configuration.
For instance, as default configuration for _tp_, there is "tp-1".
These "codes" are the only command-line arguments to ``run_11_sim.py``.

You could therefore now proceed by creating all the required datasets for the fiducial experiment (Section 6), by executing

  * ``python run_11_sim.py si-1`` (this is a fast one, while the others will take several hours)
  * ``python run_11_sim.py tp-1``
  * ``python run_11_sim.py vp-1`` (this one is particularly massive, with 50 million galaxies)
  * ``python run_11_sim.py tw-1``
  * ``python run_11_sim.py vo-1``

Note that for each set, the number of CPUs to use can be set in the corresponding drawconf variable.

The idea of these _code-named_ dataset definitions is that one can add alternative datasets to ``run_11_sim.py`` (all parameters can change: galaxy parameter distributions, dataset sizes and structures, etc) for experimentations.

For all further steps (e.g., training, validation, plots) only the _code_ in ``config.py`` has to be properly set to point to the right dataset to use.

As a first test, start by creating the simulation inspection set using ``python run_11_sim.py si-1``, and then check the results with ``python plot_1_siminspect.py``. This last script provides a simple first example for how data is plotted with MomentsML. All the other scripts generating checkplots or figures follow the same ideas and use the same tools.

If the dataset "vp-1" is available, the figure ``python paperfig_6_snr_failfrac.py`` can be generated, to reproduce Fig. 5 of the paper. Note that the numbering of these scripts is not related to the number of the paper Figures.

### Training the point estimates, with ``run_21_train.py``

First, set the config.shearconflist to have a single uncommented line, as for now we don't want the trainings to run one after the other automatically.
To give an example, the file ``mlconfig/ada5s1f.cfg`` describes the features to use for the training of the first component of the shear. In combination with the code of the tp-dataset (and the name of the tenbilac settings), this string "ada5s1f" will define a name for the training:

  * ada5 stands for 5 adamom (adaptive moments) features
  * s1 for the first component of the shear (s1w for the corresponding weight)
  * f for using the flux (and not the log(flux)) as input feature.
  
Other potential training settings are available in ``mlconfig/``.

The script ``run_21_train.py`` itself takes 2 command line arguments: the <S/N> cut, and a character "s" (use this when aiming at shear predictions) or "e" (use this when aiming at the ellipticity predictions).

To train the point estimates as described in Section 6, run this script twice (once for each shear component) using the line ``python run_21_train.py 10 s``.
The network-committees are saved in a structured way within the workdir, including some checkplots and snapshots.


### Validating the point estimates, with ``run_22_val.py``

Following the same logic of using the settings in config.shearconflist, this predicts the shear point estimates on the vp catalog, and saves them into a new catalog.
As we want both predictions of s1 and s2 in the same catalog, uncomment both lines in config.shearconflist, and run this script only once.

The script ``paperfig_1_condbias.py`` can now be used to generate Fig. 9 of the paper.


### Training the weights estimates, with ``run_31_pred_for_w.py`` and ``run_32_train_w.py``

Before training the weights, the shear point estimates must be computed on the tw set.
This is done with ``run_31_pred_for_w.py``. Keep both lines in config.shearconflist uncommented, to get both point estimates in one catalog.

The script ``run_32_train_w.py`` can then be used to train the weights, using only one line of config.weightconflist at a time.
The committees are saved following the same structure as for the point estimates, and using a directory name that combines the names of the training sets and the point estimates, so that several settings can be kept and compared.


### Overall validation, with ``run_33_val_w.py``

All the relavant lines in config.shearconflist and config.weightconflist can now be uncommented, so that  ``run_33_val_w.py`` creates a single catalog with all predictions. ``paperfig_2_overallbias.py`` can be used to generate Fig. 11 of the paper.


To make the condbias plot with weights (Fig. 12 of the paper), use again ``paperfig_1_condbias.py``. Note however that this plot is made using a "vp"-like data structure. Therefore, you'll have to:

  - set the config.dataset "vo" to the "vp" that you want to use
  - set the desired shearconflist and weightconflist
  - run val_w to get the predictions
  - make the condbias plot, with useweights=True





