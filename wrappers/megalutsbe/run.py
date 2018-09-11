"""
This defines classes useful for step-by-step / manual use of MomentsML on SBE data.
"""

import momentsml
import momentsml.meas

import numpy as np
import os
import sys
import astropy
import glob
import random

import logging
logger = logging.getLogger(__name__)

from . import io
from . import analysis

import subprocess

class Run():


	def __init__(self, sbedatadir, workdir, ncpu=4):
		"""
		:param sbedatadir: where the SBE data is
		:param workdir: where momentsml can write any intermediary files
		:param ncpu: max number of CPU to use
		"""
		self.sbedatadir = sbedatadir
		self.workdir = workdir
		self.ncpu = ncpu
		
		self.workobsdir = os.path.join(self.workdir, "obs")
		self.worksimdir = os.path.join(self.workdir, "sim")
		self.workmldir = os.path.join(self.workdir, "ml")
		
		
		if not os.path.exists(self.workdir):
			os.makedirs(self.workdir)
		if not os.path.exists(self.workobsdir):
			os.makedirs(self.workobsdir)
		if not os.path.exists(self.worksimdir):
			os.makedirs(self.worksimdir)
		if not os.path.exists(self.workmldir):
			os.makedirs(self.workmldir)

		self.groupobspath = os.path.join(self.workobsdir, "groupobs.pkl")


	
	def makecats(self, onlyn = None, sbe_sample_scale=0.05):
		"""
		Read the SBE data files and prepare MomentsML "observations" catalogs.
		For each SBE image, an input catalog is written into the workdir.
		"""

		filenames = io.get_filenames(self.sbedatadir)
		if onlyn != None:
			filenames = filenames[:onlyn]
		
		
		# Hardcoded for now:
		stampsize = 200
		n = 32
		
		logger.info("Will make %i cats..." % len(filenames))
		
		for filename in filenames:
			
			datafilepath = io.datafile(filename)
			imagefilepath = io.imagefile(filename)
			workname = io.workname(filename)
			catfilepath = os.path.join(self.workobsdir, workname + "-inputcat.pkl")
			imageworkdirfilepath = os.path.join(self.workobsdir, workname + "-imageworkdir")
			
			if os.path.exists(catfilepath):
				logger.info("Skipping '%s', catalog already exists" % (workname))
				continue
			
			# We read the data file and turn it into an astropy table
			cat = astropy.io.ascii.read(datafilepath)
			
			# Let's keep the file identification also in the meta dict:
			cat.meta["sbefilename"] = filename # very weird SBE thing, without extension...
			cat.meta["workname"] = workname
			
			# Let's convert the true shape parameters into more convenient forms:
			
			cat["PSF_e1"] = cat["PSF_shape_1"] * np.cos(2.0*cat["PSF_shape_2"]*np.pi/180)
			cat["PSF_e2"] = cat["PSF_shape_1"] * np.sin(2.0*cat["PSF_shape_2"]*np.pi/180)
			cat["Galaxy_e1"] = cat["Galaxy_shape_1"] * np.cos(2.0*cat["Galaxy_shape_2"]*np.pi/180)
			cat["Galaxy_e2"] = cat["Galaxy_shape_1"] * np.sin(2.0*cat["Galaxy_shape_2"]*np.pi/180)
			cat["Galaxy_g1"] = cat["Galaxy_shear_1"] * np.cos(2.0*cat["Galaxy_shear_2"]*np.pi/180)
 			cat["Galaxy_g2"] = cat["Galaxy_shear_1"] * np.sin(2.0*cat["Galaxy_shear_2"]*np.pi/180)

			# And for convenience, include some standard MomentsML names for the PSFs
			cat["tru_psf_g1"] = cat["PSF_e1"]
			cat["tru_psf_g2"] = cat["PSF_e2"]
			cat["tru_psf_sigma"] = cat["PSF_sigma_arcsec"] / sbe_sample_scale
   
			# We add the xid, yid, x and y columns, following an explanation by Bryan
			# on how the data/fits files should be interpreted ("like english text").
			#cat["xid"] = np.concatenate([np.arange(n) for i in range(n)])
			#cat["yid"] = np.concatenate([np.ones(n, dtype=np.int)*(n - i -1) for i in range(n)])
			# Well, not exactly. One should start y at the bottom, it seems:
			cat["xid"] = np.concatenate([np.arange(n) for i in range(n)])
			cat["yid"] = np.concatenate([np.ones(n, dtype=np.int)*i for i in range(n)])		
			cat["x"] = stampsize/2.0 + cat["xid"]*(stampsize + 1) + 0.5
			cat["y"] = stampsize/2.0 + cat["yid"]*(stampsize + 1) + 0.5
					
			# We create the ImageInfo object
			img = momentsml.tools.imageinfo.ImageInfo(
				filepath = imagefilepath,
				xname = "x", yname = "y",
				stampsize = stampsize,
				workdir = imageworkdirfilepath
				)
			cat.meta["img"] = img
			
			# And save the catalog
			momentsml.tools.io.writepickle(cat, catfilepath)
		

	def measobs(self, measfct, stampsize=200, skipdone=True):
		"""
		Runs the measfct on the observations
		"""
		
		incatfilepaths = glob.glob(os.path.join(self.workobsdir, "*-inputcat.pkl"))
		outcatfilepaths = [incat.replace("inputcat", "meascat") for incat in incatfilepaths]
		
		logger.info("Measuring %i cats..." % len(incatfilepaths))
	
		measfctkwargs = {"stampsize":stampsize}
	
		momentsml.meas.run.general(incatfilepaths, outcatfilepaths, measfct, measfctkwargs, ncpu=self.ncpu, skipdone=skipdone)
		
		
		

#	def plotobscheck(self, prefix="adamom_", g12_low=None, g12_high=None):
#		"""
#		One checkplot for every SBE "file"
#		"""
#		
#		catfilepaths = glob.glob(os.path.join(self.workobsdir, "*-meascat.pkl"))
#	
#		for catfilepath in catfilepaths:#[:1]:
#			
#			
#			cat = momentsml.tools.io.readpickle(catfilepath)
#			
#			plotfilepath = os.path.join(self.workobsdir, cat.meta["workname"] + "-measobscheckplot.png")
#			
#			plot.meascheck(cat, plotfilepath, prefix, g12_low, g12_high)
	

	def groupobs(self, nfiles="all"):
		"""
		Groups either all or some tractable sample of the obs measurements into a single catalog, handy for testing distributions.
		"""
		
		catfilepaths = glob.glob(os.path.join(self.workobsdir, "*-meascat.pkl"))
		
		if nfiles == "all":
			somefiles = catfilepaths
		else:
			somefiles = random.sample(catfilepaths, nfiles)
		
		somecats = [momentsml.tools.io.readpickle(f) for f in somefiles]
		for cat in somecats:
			cat.meta = {} # To avoid conflicts when stacking
		
		groupcat = astropy.table.vstack(somecats, join_type="exact", metadata_conflicts="error")
		
		momentsml.tools.io.writepickle(groupcat, self.groupobspath)
		
	
	def showmeasobsfrac(self, fields = ["skystd", "adamom_flux"]):
		"""
		For testing purposes, computes measurement success fractions.
		"""
		
		cat = momentsml.tools.io.readpickle(self.groupobspath)
		#print cat.colnames
				
		for field in fields:
			nbad = np.sum(cat[field].mask)
			ntot = len(cat)
			print "%20s: %.3f%% ( %i / %i are masked)" % (field, 100.0*float(ntot - nbad)/float(ntot), nbad, ntot)
			
		#import matplotlib.pyplot as plt
		#plt.plot(cat["sewpy_FLUX_AUTO"], cat["adamom_flux"], "b.")
		#plt.show()


#	def plotmixobscheck(self, prefix='adamom_', filepath=None):
#		"""
#		One checkplot mixing several SBE files.
#		"""
#		
#		cat = momentsml.tools.io.readpickle(self.groupobspath)
#		plot.meascheck(cat, prefix=prefix, filepath=filepath)
	
	
	
	def drawsims(self, simparams, n=100, nc=10, ncat=1, nrea=1, stampsize=200):
		"""
		Draws many sims on several cpus, in the standard MomentsML style.
		
		n is number of galaxies
		nc is number of columns
		"""
		
		drawcatkwargs = {"n":n, "nc":nc, "stampsize":stampsize}
		drawimgkwargs = {}
		
		momentsml.sim.run.multi(self.worksimdir, simparams, drawcatkwargs, drawimgkwargs, 
			psfcat = None, ncat=ncat, nrea=nrea, ncpu=self.ncpu,
			savepsfimg=False, savetrugalimg=False)


	def meassims(self, simparams, measfct, stampsize=200):
		"""
		Idem
		"""
		measfctkwargs = {"stampsize":stampsize}
		momentsml.meas.run.onsims(self.worksimdir, simparams, self.worksimdir, measfct, measfctkwargs, ncpu=self.ncpu, skipdone=True)
		
		


#	def avgsimmeas(self, simparams, groupcols, removecols):
#		"""
#		Averages the measurements on the sims accross the different realizations, and writes
#		a single training catalog for the ML.
#		"""	
#	
#		avgmeascat = momentsml.meas.avg.onsims(self.worksimdir, simparams,
#			groupcols=groupcols,
#			removecols=removecols,
#			removereas=False,
#			keepfirstrea=True
#		)
#
#		momentsml.tools.io.writepickle(avgmeascat, os.path.join(self.worksimdir, simparams.name, "avgmeascat.pkl"))

	def groupsimmeas(self, simparams, groupcols, removecols):
		"""
		New alternative to avgsimmeas: we just group the catalogs, without computing any stats.
		Writes a single training catalog for the ML.
		"""	
	
		groupmeascat = momentsml.meas.avg.onsims(self.worksimdir, simparams, task="group",
			groupcols=groupcols,
			removecols=removecols
		)

		momentsml.tools.io.writepickle(groupmeascat, os.path.join(self.worksimdir, simparams.name, "groupmeascat.pkl"))

		
		
	
#
#	def traintenbilac(self, simparams, trainparamslist):
#		"""
#		
#		"""
#		
#		# We load the training catalog
#		simcat = momentsml.tools.io.readpickle(os.path.join(self.worksimdir, simparams.name, "groupmeascat.pkl"))
#		
#		#print simcat.colnames
#		#print simcat
#		#print simcat.meta
#		
#		name = "with_" + simparams.name
#		traindir = os.path.join(self.workmldir, name)
#		#exit()
#		
#		# We reject crap ones
#		simcat["goodfortrain"] = np.ma.count(simcat["adamom_flux"], axis=1) # How many hsm sucesses per case
#		simcat = simcat[simcat["goodfortrain"] > float(simcat.meta["ngroup"])/2.0] # keeping only if half of the reas could be measured
#		logger.info("Keeping %i galaxies for training" % (len(simcat)))
#		
#		
#		#simcat = simcat[:100]
#		#print "only training on 1000 gals hack"
#		
#		#momentsml.tools.io.writepickle(simcat, os.path.join(traindir, simparams.name, "traincat.pkl"))
#		
#		momentsml.learn.run.train(simcat, traindir, trainparamslist, ncpu=self.ncpu)
#


#	def selfpredict(self, simparams, trainparamslist):
#		
#		
#		name = "with_" + simparams.name
#		traindir = os.path.join(self.workmldir, name)
#	
#		cat = momentsml.tools.io.readpickle(os.path.join(self.worksimdir, simparams.name, "groupmeascat.pkl"))
#		
#		cat = momentsml.learn.run.predict(cat, traindir, trainparamslist)		
#		
#		momentsml.tools.io.writepickle(cat, os.path.join(traindir, "selfprecat.pkl"))
#


#	def othersimpredict(self, othersimparams, simparams, trainparamslist):
#		"""
#		simparams and triainparamslist have been used for the training.
#		othersimpredict is another simparams for which you want the preds.	
#		"""
#		
#		name = "with_" + simparams.name
#		traindir = os.path.join(self.workmldir, name)
#
#		cat = momentsml.tools.io.readpickle(os.path.join(self.worksimdir, othersimparams.name, "groupmeascat.pkl"))		
#		cat = momentsml.learn.run.predict(cat, traindir, trainparamslist)
#
#		momentsml.tools.io.writepickle(cat, os.path.join(self.worksimdir, othersimparams.name, "groupmeascat_predshapes.pkl"))
#


	def inspect(self, simparams=None):
		
		
		cat = momentsml.tools.io.readpickle(os.path.join(self.worksimdir, simparams.name, "groupmeascat_cases.pkl"))
		#cat = momentsml.tools.io.readpickle(os.path.join(self.worksimdir, simparams.name, "groupmeascat_predshapes.pkl"))
		
		out = momentsml.learn.ml.get3Ddata(cat, ["adamom_g1", "adamom_g2", "adamom_sigma", "adamom_flux", "tru_psf_g1", "tru_psf_g2", "tru_psf_sigma"])
		print out.shape
		
		
		
		
		#print cat.colnames
		#print cat["tru_flux", "tru_g1", "tru_psf_g1", "tru_s1", "adamom_flux"]
		#print cat.meta
		


	def prepcases(self, simparams, groupcolnames):
		"""
		Reshapes the simmeas data in rows of different cases, ready for tenbilac shear-style training.
		
		"""
		
		#cat = momentsml.tools.io.readpickle(os.path.join(self.worksimdir, simparams.name, "groupmeascat_predshapes.pkl"))
		cat = momentsml.tools.io.readpickle(os.path.join(self.worksimdir, simparams.name, "groupmeascat.pkl"))
		
		logger.info("Preparing cases for catalog of length {}".format(len(cat)))
		
		""" # This code was usefull to "split" catalogs into even more batches
		# To make nice batches, we will add a temporary helper column to the catalog.
		n = 5000
		nsnc = 8
		
		batchsize = 1000*nsnc
		
		assert n*nsnc % batchsize == 0
		assert len(cat) % batchsize == 0
		
		inds = np.arange(0, len(cat)/batchsize)
		tmpcolvals = np.repeat(inds, batchsize)
		
		cat["prepbatchtmp"] = tmpcolvals
		
		logger.warning("If your sersic indices are not random, what I do here needs to be improved!")
		
		cat = momentsml.tools.table.groupreshape(cat, groupcolnames = bincolnames + ["prepbatchtmp"])
		
		cat.remove_column("prepbatchtmp")
		"""
		
		cat = momentsml.tools.table.groupreshape(cat, groupcolnames = groupcolnames)
		
		
		momentsml.tools.io.writepickle(cat, os.path.join(self.worksimdir, simparams.name, "groupmeascat_cases.pkl"))


	def addpreweights(self, simparams):
		"""
		
		"""
		cat = momentsml.tools.io.readpickle(os.path.join(self.worksimdir, simparams.name, "groupmeascat_cases.pkl"))
		
		cat["pw"] = cat["snr"]**2
		#cat["pw"] = np.clip(cat["snr"], 8.0, 10000.0) - 8.0
		
		momentsml.tools.io.writepickle(cat, os.path.join(self.worksimdir, simparams.name, "groupmeascat_cases_pw.pkl"))

		



	def traintenbilacshear(self, simparams, trainparamslist):
		"""
		Trains for predicting shear
		"""
		
		# We load the training catalog
		#simcat = momentsml.tools.io.readpickle(os.path.join(self.worksimdir, simparams.name, "groupmeascat_cases.pkl"))
		simcat = momentsml.tools.io.readpickle(os.path.join(self.worksimdir, simparams.name, "groupmeascat_cases_pw.pkl"))
		
		name = "with_" + simparams.name
		traindir = os.path.join(self.workmldir, name)
		
		momentsml.learn.run.train(simcat, traindir, trainparamslist, ncpu=self.ncpu)


	def selfpredictshear(self, simparams, trainparamslist):
	
		
		name = "with_" + simparams.name
		traindir = os.path.join(self.workmldir, name)
		
		#cat = momentsml.tools.io.readpickle(os.path.join(self.worksimdir, simparams.name, "groupmeascat_predshapes.pkl"))
		#cat = momentsml.tools.io.readpickle(os.path.join(self.worksimdir, simparams.name, "groupmeascat_cases.pkl"))
		#cat = momentsml.tools.io.readpickle(os.path.join(self.worksimdir, simparams.name, "groupmeascat.pkl"))
		
		cat = momentsml.tools.io.readpickle(os.path.join(self.worksimdir, simparams.name, "groupmeascat_cases_pw.pkl"))
		
		
		cat = momentsml.learn.run.predict(cat, traindir, trainparamslist)
		
		#print cat.colnames
		
		momentsml.tools.io.writepickle(cat, os.path.join(traindir, "selfprecat_shear.pkl"))
		#momentsml.tools.io.writepickle(cat, os.path.join(traindir, "selfprecat_shear_nocases.pkl"))
	
	
	
	def otherpredictshear(self, othersimname, simparams, trainparamslist):
		"""
		
		"""
		
		cat = momentsml.tools.io.readpickle(os.path.join(self.worksimdir, othersimname, "groupmeascat_cases.pkl"))		
		
		name = "with_" + simparams.name
		traindir = os.path.join(self.workmldir, name)
		cat = momentsml.learn.run.predict(cat, traindir, trainparamslist)

		momentsml.tools.io.writepickle(cat, os.path.join(traindir, "otherprecat_shear.pkl"))
	
		
	def traintenbilacweight(self, simparams, trainparamslist):
		"""
		Trains for predicting weights
		"""
		
		# We load the shear-predicted catalog
		
		traindir = os.path.join(self.workmldir, "with_" + simparams.name)
		#simcat = momentsml.tools.io.readpickle(os.path.join(traindir, "selfprecat_shear.pkl"))
		simcat = momentsml.tools.io.readpickle(os.path.join(traindir, "otherprecat_shear.pkl"))
		
		
		momentsml.learn.run.train(simcat, traindir, trainparamslist, ncpu=self.ncpu)

		
		
	
	def inspectshear(self, simparams, trainparamslist):
	
		
		name = "with_" + simparams.name
		traindir = os.path.join(self.workmldir, name)
	
		cat = momentsml.tools.io.readpickle(os.path.join(traindir, "selfprecat_shear.pkl"))
	
		
		#data = momentsml.learn.ml.get3Ddata(cat, ["pre_g1", "pre_g1_w3"])
		
		tru_s = cat["tru_s1"]
		pre_g = cat["pre_g1"]
		pre_w = cat["pre_g1_w3"]
		
		print tru_s.shape, pre_g.shape, pre_w.shape
		
		wgs = np.mean(pre_g * pre_w, axis=1) * 0.95
		biases = wgs - tru_s
		
		print np.mean(np.square(biases))
			
		ret = momentsml.tools.calc.linreg(tru_s, wgs)
		print ret
		
		#exit()
		
		#import matplotlib.pyplot as plt
		
		#plt.plot(tru_s, bias, "r.")
		#plt.show()
		
		
	
		"""
		import matplotlib.pyplot as plt
		
		dat = cat["pre_g1_w1"][0]#.filled(-0.1)
		
		print dat
		
		print np.clip(dat, 1, 5)
		
		#print dat.shape
		
		#plt.hist(dat, bins=100)
		#plt.show()
		"""
	
	def predictsbe_v5(self, simparams, mlparams):
	
		cat = momentsml.tools.io.readpickle(self.groupobspath)
		#print cat.colnames
		#print len(cat)
		#exit()
		
		cat["pw"] = cat["snr"]**2 # does not harm for non-pw trainings...
		
		traindir = os.path.join(self.workmldir, "with_" + simparams.name)
		
		cat = momentsml.learn.run.predict(cat, traindir, mlparams)
			
		momentsml.tools.io.writepickle(cat, os.path.join(self.workobsdir, "predgroupobs.pkl"))
	
	
	
#	def predictsbe(self, shapesimparams, shapeml, shearsimparams, shearml):
#	
#		cat = momentsml.tools.io.readpickle(self.groupobspath)
#		#print cat.colnames
#		#print len(cat)
#		
#		
#		shapetraindir = os.path.join(self.workmldir, "with_" + shapesimparams.name)
#		sheartraindir = os.path.join(self.workmldir, "with_" + shearsimparams.name)
#		
#		
#		cat = momentsml.learn.run.predict(cat, shapetraindir, shapeml)
#		cat = momentsml.learn.run.predict(cat, sheartraindir, shearml)
#		
#		#print cat.colnames
#		#exit()
#		
#		momentsml.tools.io.writepickle(cat, os.path.join(self.workobsdir, "predgroupobs.pkl"))

	
	def analysepredsbe(self):
		"""
		Measures m and c directly from the catalog, without having to write the ascii output files.
		"""
		
		cat = momentsml.tools.io.readpickle(os.path.join(self.workobsdir, "predgroupobs.pkl"))
		
		#cat["pre_s1"] = cat["pre_g1"] * 1.0*cat["pre_g1_w3"]
		#cat["pre_s2"] = cat["pre_g2"] * 1.0*cat["pre_g2_w3"]
		
		
		print cat.colnames
		
		#exit()
		
		analysis.analyse(cat, 
			colname_PSF_ellipticity_angles_degrees="PSF_shape_2",
			colname_e1_guesses="pre_s1",
			colname_e2_guesses="pre_s2",
			colname_gal_g1s="Galaxy_g1",
			colname_gal_g2s="Galaxy_g2",
		)


	
	def writepredsbe(self):
		"""
		
		From Bryan's mail:
		
		FITS format table (empty primary header, binary table in first	extension)
		-Keyword SHE_FMT in header describing specific format (which will be
		incremented/changed when the required output columns are changed).
		Present value to be '0.1'
		-The following columns, with each row representing one galaxy:
		--GAL_ID (64-bit integer, format code 'K' - unique ID for each galaxy)
		--GAL_G1 (32-bit float, format code 'E' - "shear" component 1 estimate)
		--GAL_G2 (32-bit float, format code 'E' - "shear" component 2 estimate)
		--GAL_G1_ERR (32-bit float, format code 'E' - "shear" component 1 error)
		--GAL_G2_ERR (32-bit float, format code 'E' - "shear" component 2 error)
		
		
		"""
	
		cat =  momentsml.tools.io.readpickle(os.path.join(self.workobsdir, "predgroupobs.pkl"))
		
		print cat.colnames
		
		cat["GAL_ID"] = cat["ID"]
		cat["GAL_G1"] = cat["pre_s1"]
		cat["GAL_G2"] = cat["pre_s2"]
		cat["GAL_G1_ERR"] = 0.0*cat["pre_s1"] + 1.0 # this way we get masked values if no shear was estimated.
		cat["GAL_G2_ERR"] = 0.0*cat["pre_s1"] + 1.0
		
		cat.keep_columns(["GAL_ID", "GAL_G1", "GAL_G2", "GAL_G1_ERR", "GAL_G2_ERR"])
		
		
		# Now we have to deal with masked entries. Three options, either fill, or remove.
		
		#cat = cat.filled(999.0) # this might not be ok for the latest script
		
		# Second attemps, putting high errors on masked points...
		#mask = cat["GAL_G1"].mask
		#print np.sum(mask), np.size(mask)
		#cat["GAL_G1"][mask] = 0.0
		#cat["GAL_G2"][mask] = 0.0
		#cat["GAL_G1_ERR"][mask] = 1.0e15
		#cat["GAL_G2_ERR"][mask] = 1.0e15
		
		# In fact, we need negative values for the errors:
		mask = cat["GAL_G1"].mask
		print np.sum(mask), np.size(mask)
		cat["GAL_G1"][mask] = 0.0
		cat["GAL_G2"][mask] = 0.0
		cat["GAL_G1_ERR"][mask] = -1e120
		cat["GAL_G2_ERR"][mask] = -1e120
		
		
		#maskremover = momentsml.tools.table.Selector("maskremover", [("nomask", "GAL_G1"), ("nomask", "GAL_G2")])
		#cat = maskremover.select(cat)
		
		cat.meta = {"SHE_FMT":"0.1"}
		
		cat.sort("GAL_ID") # Testing if this has an influence (of course it should not...)
		
		print "For testing, here are a few rows of your catalog:"
		print cat
		
		print cat.meta
		
		fitspath = os.path.join(self.workmldir, "obsprecat.fits")
		if os.path.exists(fitspath):
			os.remove(fitspath)
		
		cat.write(fitspath, format='fits')
		
		logger.info("Wrote '{}'.".format(fitspath))
		


	def writepredsbe_pw(self):
		"""
		
		"""
	
		cat =  momentsml.tools.io.readpickle(os.path.join(self.workobsdir, "predgroupobs.pkl"))
		
		print cat.colnames
		
		cat["GAL_ID"] = cat["ID"]
		cat["GAL_G1"] = cat["pre_s1pw"]
		cat["GAL_G2"] = cat["pre_s2pw"]
		
		cat["GAL_G1_ERR"] = np.sqrt(((10000.0/cat["pw"]) - 0.25**2) / 2.0)
		cat["GAL_G2_ERR"] = cat["GAL_G1_ERR"]
		
		cat.keep_columns(["GAL_ID", "GAL_G1", "GAL_G2", "GAL_G1_ERR", "GAL_G2_ERR"])
				
		# In fact, we need negative values for the errors:
		mask = cat["GAL_G1"].mask
		print np.sum(mask), np.size(mask)
		cat["GAL_G1"][mask] = 0.0
		cat["GAL_G2"][mask] = 0.0
		cat["GAL_G1_ERR"][mask] = -1e120
		cat["GAL_G2_ERR"][mask] = -1e120
		
			
		cat.meta = {"SHE_FMT":"0.1"}
		
		cat.sort("GAL_ID") # Testing if this has an influence (of course it should not...)
		
		print "For testing, here are a few rows of your catalog:"
		print cat
		
		print cat.meta
		
		fitspath = os.path.join(self.workmldir, "obsprecat.fits")
		if os.path.exists(fitspath):
			os.remove(fitspath)
		
		cat.write(fitspath, format='fits')
		
		logger.info("Wrote '{}'.".format(fitspath))
	
	
	def runsbeana(self):
		"""
		Just to avoid messing up on the last meter, we script this step as well.

		--> Not done here, but in the script.
		"""
		
		
	


#
#	def train(self, simparams, trainparamslist, prefix='adamom_'):
#		"""
#		
#		"""
#		
#		# We load the training catalog
#		simcat = momentsml.tools.io.readpickle(os.path.join(self.worksimdir, simparams.name, "avgmeascat.pkl"))
#		
#		# We reject crap ones
#		ngroupstats = simcat.meta["ngroupstats"]
#		simcat = simcat[simcat[prefix+"flux_n"] > float(ngroupstats)/2.0]
#		logger.info("Keeping %i galaxies for training" % (len(simcat)))
#		
#		momentsml.tools.io.writepickle(simcat, os.path.join(self.workmldir, "traincat.pkl"))
#		#plot.simcheck(simcat)
#		
#		#print simcat.colnames
#		#exit()
#		
#		momentsml.learn.run.train(simcat, self.workmldir, trainparamslist, ncpu=self.ncpu)
			
		
	
#	def predictsims(self, simparams, trainparamslist):
#		
#		#cat = momentsml.tools.io.readpickle(os.path.join(self.worksimdir, simparams.name, "avgmeascat.pkl"))
#		cat = momentsml.tools.io.readpickle(os.path.join(self.worksimdir, simparams.name, "groupmeascat.pkl"))
#		#cat = momentsml.tools.io.readpickle(os.path.join(self.worksimdir, simparams.name, "groupmeascat_binreshape.pkl"))
#		
#		#print cat.colnames
#		#exit()
#		
#		
#		#cat = momentsml.learn.run.predict(cat, self.workmldir, trainparamslist, tweakmode="all")
#		#cat = momentsml.learn.run.predict(cat, self.workmldir, trainparamslist, tweakmode="_rea0")
#		cat = momentsml.learn.run.predict(cat, self.workmldir, trainparamslist)
#		
#		#print cat.colnames
#		#print cat["pre_sigma"]
#		
#		#momentsml.tools.io.writepickle(cat, os.path.join(self.workmldir, "selfprecat_binreshape.pkl"))
#		momentsml.tools.io.writepickle(cat, os.path.join(self.workmldir, "selfprecat.pkl"))
#	
#
#
#		
#	def analysepredsims(self):
#		"""
#		Measures m and c on the sims.
#		Does not fully work as PSF_shape_2 is not present in the sims catalog. Easy to add, but do we need this ?
#		"""
#		
#		cat =  momentsml.tools.io.readpickle(os.path.join(self.workmldir, "selfprecat.pkl"))
#		
#		"""
#		print len(cat)
#		
#		cat["tru_s"] = np.hypot(cat["tru_s1"], cat["tru_s2"])
#		
#		sel = momentsml.tools.table.Selector("test",[
#		("in", "tru_s", 0.01, 0.02)
#		]) 
#	
#		selcat = sel.select(cat)
#		"""
#			
#		analysis.analyse(cat, 
#			colname_PSF_ellipticity_angles_degrees="tru_g1",
#			colname_e1_guesses="pre_s1",
#			colname_e2_guesses="pre_s2",
#			colname_gal_g1s="tru_s1",
#			colname_gal_g2s="tru_s2",
#		)
#		


#	def predictobs(self, trainparamslist):
#	
#		cat = momentsml.tools.io.readpickle(self.groupobspath)
#		
#		#cat = momentsml.learn.run.predict(cat, self.workmldir, trainparamslist, tweakmode="") # Drop the "_mean" which does not exists for obs
#		cat = momentsml.learn.run.predict(cat, self.workmldir, trainparamslist)
#		
#		momentsml.tools.io.writepickle(cat, os.path.join(self.workmldir, "obsprecat.pkl"))
#
#
#
#	def writepredsbe(self):
#		"""
#		
#		From Bryan's mail:
#		
#		FITS format table (empty primary header, binary table in first	extension)
#		-Keyword SHE_FMT in header describing specific format (which will be
#		incremented/changed when the required output columns are changed).
#		Present value to be '0.1'
#		-The following columns, with each row representing one galaxy:
#		--GAL_ID (64-bit integer, format code 'K' - unique ID for each galaxy)
#		--GAL_G1 (32-bit float, format code 'E' - "shear" component 1 estimate)
#		--GAL_G2 (32-bit float, format code 'E' - "shear" component 2 estimate)
#		--GAL_G1_ERR (32-bit float, format code 'E' - "shear" component 1 error)
#		--GAL_G2_ERR (32-bit float, format code 'E' - "shear" component 2 error)
#		
#		
#		"""
#	
#	
#		
#		cat =  momentsml.tools.io.readpickle(os.path.join(self.workmldir, "obsprecat.pkl"))
#		
#		print cat.colnames
#		
#		cat["GAL_ID"] = cat["ID"]
#		cat["GAL_G1"] = cat["pre_s1"]
#		cat["GAL_G2"] = cat["pre_s2"]
#		cat["GAL_G1_ERR"] = 0.0*cat["pre_s1"] + 1.0
#		cat["GAL_G2_ERR"] = 0.0*cat["pre_s1"] + 1.0
#		
#		cat.keep_columns(["GAL_ID", "GAL_G1", "GAL_G2", "GAL_G1_ERR", "GAL_G2_ERR"])
#		cat = cat.filled(999.0)
#		cat.meta = {"SHE_FMT":"0.1"}
#		
#		print "For testing, here are a few rows of your catalog:"
#		print cat
#		
#		
#		print cat.meta
#		
#		
#		#cat.write("test.fits", format='fits')
#		
#
#
#
#	def fakepredictobs(self):
#		"""
#		cat = momentsml.tools.io.readpickle(self.groupobspath)
#		
#		cat["pre_g1"] = cat["Galaxy_g1"] + cat["Galaxy_e1"] + 0.01*np.random.randn(len(cat))
#		cat["pre_g2"] = cat["Galaxy_g2"] + cat["Galaxy_e2"] + 0.01*np.random.randn(len(cat))
#		
#		momentsml.tools.io.writepickle(cat, os.path.join(self.workmldir, "obsprecat.pkl"))
#		"""
#		
#		
#
#	
#	def analysepredobs(self):
#		"""
#		Measures m and c directly from the catalog, without having to write the ascii output files.
#		"""
#		
#		cat =  momentsml.tools.io.readpickle(os.path.join(self.workmldir, "obsprecat.pkl"))
#		
#		print cat.colnames
#		
#		
#		analysis.analyse(cat, 
#			colname_PSF_ellipticity_angles_degrees="PSF_shape_2",
#			colname_e1_guesses="pre_s1",
#			colname_e2_guesses="pre_s2",
#			colname_gal_g1s="Galaxy_g1",
#			colname_gal_g2s="Galaxy_g2",
#		)


#	def writepredsbe_single(self):
#		
#		cat =  momentsml.tools.io.readpickle(os.path.join(self.workmldir, "obsprecat.pkl"))
#		
#		cat["PSF_shape_angle_degrees"] = cat["PSF_shape_2"]
#		cat["e1_guess"] = cat["pre_g1"]
#		cat["e2_guess"] = cat["pre_g2"]
#		cat["gal_g1"] = cat["Galaxy_g1"]
#		cat["gal_g2"] = cat["Galaxy_g2"]
#		cat["weight"] = np.logical_not(cat["pre_g1"].mask).astype("float")
#		
#		cat.keep_columns(["PSF_shape_angle_degrees", "e1_guess", "e2_guess", "gal_g1", "gal_g2", "weight"])
#		cat = cat.filled(999.0)
#		
#		print "For testing, here are a few rows of your catalog:"
#		print cat
#		
#		exportpath = os.path.join(self.workdir, "results.txt")
#		
#		cat.write(exportpath, format='ascii.commented_header', delimiter="\t")
#			
#		logger.info("Wrote %s" % exportpath)
#

#
#	def writepredsbe(self, outdir=None):
#		"""
#		
#		Warning, this writes results into the sbedatadir, as does the example script
#		"""
#		
#		# When merging the catalogs, we lost the info about filenames.
#		# It might be that in the following we mix up file names with respect to the original drawing.
#		# But given that each file is equivalent (params randomly drawn from the same distribs)
#		# this will produce exactly the same results.
#		
#		filenames = io.get_filenames(self.sbedatadir)
#		#print "\n".join(filenames)
#		
#		cat = momentsml.tools.io.readpickle(os.path.join(self.workmldir, "obsprecat.pkl"))
#		
#		# As the SBE scripts are fully self-inconsistent, we have to rename even their own columns here...
#		
#		cat["PSF_shape_angle_degrees"] = cat["PSF_shape_2"]
#		cat["e1_guess"] = cat["pre_g1"]
#		cat["e2_guess"] = cat["pre_g2"]
#		cat["gal_g1"] = cat["Galaxy_g1"]
#		cat["gal_g2"] = cat["Galaxy_g2"]
#		cat["weight"] = np.logical_not(cat["pre_g1"].mask).astype("float")
#		
#		cat.keep_columns(["PSF_shape_angle_degrees", "e1_guess", "e2_guess", "gal_g1", "gal_g2", "weight"])
#		
#		print "For testing, here are a few rows of your catalog:"
#		print cat[:20]
#		
#		
#		
#		for (i, filename) in enumerate(filenames):
#			
#			subcat = cat[i*1024:(i+1)*1024].filled(999.0)
#			assert len(subcat) == 1024
#			
#			#print filename
#			exportpath = filename + "_res.dat"
#			#exportpath = "test.txt"
#			
#			subcat.write(exportpath, format='ascii.commented_header', delimiter="\t")
#			
#			logger.info("Wrote %s" % exportpath)
#
#
#			#exit()
#	
#	
#
#
#	def predictobs_indiv(self, trainparamslist):
#		"""
#		Predicts each SBE file separately DO WE NEED THIS
#		"""
#		"""
#		incatfilepaths = glob.glob(os.path.join(self.workobsdir, "*-meascat.pkl"))
#		
#		logger.info("Predicting %i cats..." % len(incatfilepaths))
#	
#		for incatfilepath in incatfilepaths:
#
#			
#			cat = momentsml.tools.io.readpickle(incatfilepath)
#			outcatfilepath = os.path.join(self.workmldir, cat.meta["workname"] + "-precat.pkl")
#
#			cat = momentsml.learn.run.predict(cat, self.workmldir, trainparamslist, totweak="_mean", tweakmode="")
#		
#			# The uncertainties:
#			#cat = momentsml.learn.run.predict(cat, self.mlworkdir, errtrainparamslist, totweak="_rea0", tweakmode="")
#		
#			momentsml.tools.io.writepickle(cat, outcatfilepath)
#		"""
#		
#
#
#	
#	def writeresults(self):
#		
#		"""
#		catfilepaths = glob.glob(os.path.join(self.workmldir, "*-precat.pkl"))
#		
#		
#		# Output the result data table
#		
#		for catfilepath in catfilepaths:
#			
#			cat = momentsml.tools.io.readpickle(catfilepath)
#			
#			resfilepath = cat.meta["workprefix"] + "-measobscheckplot.png"
#			cat = 
#			result_filename = filename_root + mv.result_tail + mv.datafile_extension
#		
#		
#    ascii.write([PSF_e_angles,
#                 e1_guesses,
#                 e2_guesses,
#                 g1s,
#                 g2s,
#                 weights],
#                result_filename,
#                names=[mv.result_PSF_e_angle_colname,
#                       mv.result_e1_guess_colname,
#                       mv.result_e2_guess_colname,
#                       mv.result_gal_g1_colname,
#                       mv.result_gal_g2_colname,
#                       mv.result_weight_colname],
#                delimiter="\t",
#                Writer=CommentedHeader)
#        
#		"""
#	
#	
	
		
	
