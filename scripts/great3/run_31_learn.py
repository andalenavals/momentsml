import matplotlib
matplotlib.use("AGG")


import momentsml.tools
import momentsml.learn
import momentsml
import tenbilac

import config
import numpy as np
import os

from momentsml.tools.feature import Feature
import matplotlib.pyplot as plt

import plot_2_val

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)


select = True


for subfield in config.great3.subfields:
	
	
	logger.info("Working on subfield {}".format(subfield))
	
	# Getting the path to the correct directories
	measdir = config.great3.subpath(subfield, "simmeas", config.datasets["train-shear"])
	traindir = config.great3.subpath(subfield, "ml", config.datasets["train-shear"])
	
	# And to the catalogue
	traincatpath = os.path.join(measdir, "groupmeascat.pkl")
	cat = momentsml.tools.io.readpickle(traincatpath)
	#print momentsml.tools.table.info(cat)
	
	if select:
		s = momentsml.tools.table.Selector("fortrain", [
			("max", "adamom_failfrac", 0.1),
		])
		cat = s.select(cat)
	
	#exit()	
	#print momentsml.tools.table.info(cat)
	
	
	# Running the training
	dirnames = momentsml.learn.tenbilacrun.train(cat, config.shearconflist, traindir)
	
	# And saving a summary plot next to the tenbilac working directories
	for dirname in dirnames:
		tenbilacdirpath = os.path.join(traindir, dirname)
		ten = tenbilac.com.Tenbilac(tenbilacdirpath)
		ten._readmembers()
		tenbilac.plot.summaryerrevo(ten.committee, filepath=os.path.join(traindir, "{}_summary.png".format(dirname)))
	
	
	#dirnames = ["ada4s1_sum55"]
	#dirnames = momentsml.learn.tenbilacrun.confnames(conflist)
	# Self-predicting
	
	cat = momentsml.tools.io.readpickle(traincatpath) # To get the full catalog with all cases, not just the selected ones
	for (dirname, conf) in zip(dirnames, config.shearconflist):

		predcat = momentsml.learn.tenbilacrun.predict(cat, [conf], traindir)
		predcatpath = os.path.join(traindir, "{}_selfpred.pkl".format(dirname))
		momentsml.tools.io.writepickle(predcat, predcatpath)
		figpredcatpath = os.path.join(traindir, "{}_selfpred.png".format(dirname))
		
		if "s2" in conf[0] or "g2" in conf[0]:
			component = 2
		else:
			component = 1
		plot_2_val.plot(predcat, component, mode=config.trainmode, filepath=figpredcatpath)
	
	
	
