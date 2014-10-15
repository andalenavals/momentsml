"""
High-level functions to create a whole set of simulations.

These functions write their results to disk, and therefore **define a directory and
filename structure**, containing the different realizations, catalogs, etc.
This is very different from the lower-level functions such as those in stampgrid,
which do not relate to any file structure.
"""

import os
import sys
import glob
import datetime
import tempfile
import cPickle as pickle
import copy
import multiprocessing

import stampgrid

import logging
logger = logging.getLogger(__name__)


def multi(params, drawcatkwargs, drawimgkwargs, ncat=2, nrea=2, ncpu=1, simdir="sim"):
	"""
	
	I use stampgrid.drawcat and stampgrid.drawimg to draw several (ncat) catalogs
	and several (nrea) "image realizations" per catalog.
	
	I support multiprocessing (ncpu), and furthermore I add my simulations to any
	existing set generated previously.
	To do so,  I take care of generating unique filenames (avoiding "race hazard") using ``tempfile``.
	So you could perfectly have multiple processes running this function in parallel, writing
	simulations using the same params in the same directory. Note that I also put a timestamp
	in my filenames, but this is just to help humans. I don't rely on it for uniqueness.
	

	:param params: a sim.Params instance that defines the distributions of parameters
	:param drawcatkwargs: Keyword arguments which I will directly pass to stampgrid.drawcat
	:type drawcatkwargs: dict
	:param drawimgkwargs: Idem for stampgrid.drawimg. However I will not respect filenames that
		you set, as I will use my own ones.
	:type drawimgkwargs: dict
	:param ncat: The number of catalogs I should draw
	:type ncat: int
	:param nrea: The number of realizations per catalog I should draw.
	:type nrea: int
	:param ncpu: Maximum number of processes I should use.
	:type ncpu: int
	:param simdir: Path to a directory where I should write the simulations.
		This directory has **not** to be unique for every call of this function!
		I will make subdirectories reflecting the name of your params inside.
		If this directory already exists, even for the same params,
		I will **add** my simulations to it, instead of overwriting anything.
	
	As an illustration, this is the directory structure I produce (ncat=2, nrea = 2)::
	
		% ls * simdir/name_of_params/*
		
		simdir/name_of_params/20141014T195755_Ggqnz4_cat.pkl
		simdir/name_of_params/20141014T195755_Pw2mjp_cat.pkl

		simdir/name_of_params/20141014T195755_Ggqnz4_img:
		0.fits
		1.fits

		simdir/name_of_params/20141014T195755_Pw2mjp_img:
		0.fits
		1.fits

	
	
	"""
	starttime = datetime.datetime.now()
	workdir = os.path.join(simdir, params.name)
	if not os.path.exists(workdir):
		os.makedirs(workdir)
		logger.info("Creating a new set of simulations named '%s'" % (params.name))
	else:
		logger.info("I'm adding new simulations to the existing set '%s'" % (params.name))

	logger.info("I will draw %i catalogs, and %i image realizations per catalog" % (ncat, nrea))

	# We create the catalogs, there is probably no need to parallelize this: 
	catalogs = [stampgrid.drawcat(params, **drawcatkwargs) for i in range(ncat)]

	# Now we save them usign single filenames.
	# This is not done with a timestamp ! The timestamp is only here to help humans.
	# The module tempfile takes care of making the filename unique.
	
	prefix = datetime.datetime.now().strftime("%Y%m%dT%H%M%S_")
	
	for catalog in catalogs:
		catfile = tempfile.NamedTemporaryFile(mode='wb', prefix=prefix, suffix="_cat.pkl", dir=workdir, delete=False)
		catalog.meta["catfilename"] = str(catfile.name)
		catalog.meta["imgdirname"] = str(catfile.name)[:-8] + "_img"
		pickle.dump(catalog, catfile) # We directly use this open file object.
		catfile.close()
		logger.info("Wrote catalog into '%s'" % catalog.meta["catfilename"])
		os.mkdir(os.path.join(workdir, catalog.meta["imgdirname"]))
		
	
	# We simply overwrite any conflicting settings in drawimgkwargs:
	mydrawimgkwargs = copy.deepcopy(drawimgkwargs)
	
	# And now we draw the image realizations for those catalogs.
	# This is done with multiprocessing.
	# We have to make a multiprocessing loop over both catalogs and realizations,
	# as we want this to be efficient for both (1 cat, 20 rea), and (20 cat, 1 rea)
	
	catindexes = range(ncat)
	reaindexes = range(nrea)
	catreatuples = [(catalogs[catindex], reaindex,mydrawimgkwargs) for catindex in catindexes for reaindex in reaindexes]

	assert len(catreatuples) == ncat * nrea
	
	# The single-processing version works fine:
	#map(drawcatrea, catreatuples)

	# The naive multiprocessing does too :)
	pool = multiprocessing.Pool(processes=ncpu)
	pool.map(drawcatrea, catreatuples)

	endtime = datetime.datetime.now()
	logger.info("Done in %s" % (str(endtime - starttime)))

	
	
def drawcatrea(catreatuple):
	# The function that draws the image.
	# Do not put anything not multiprocessing-safe in here !		
	cat = catreatuple[0]#catalogs[catreatuple[0]]
	reaindex = catreatuple[1]
	mydrawimgkwargs = catreatuple[2]
	
	# We simply overwrite any conflicting settings in drawimgkwargs:
	mydrawimgkwargs["simgalimgfilepath"] = os.path.join(cat.meta["imgdirname"], "%i.fits" % (reaindex))
	mydrawimgkwargs["simtrugalimgfilepath"] = None # for now...
	mydrawimgkwargs["simpsfimgfilepath"] = None
	
	stampgrid.drawimg(galcat = cat, **mydrawimgkwargs)

