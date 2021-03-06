import matplotlib
matplotlib.use("AGG")

import momentsml.tools
import momentsml.learn
import momentsml

import config
import numpy as np
import os

import plot_3_valw

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)



for subfield in config.great3.subfields:

	logger.info("Working on subfield {}".format(subfield))

	valname = "pred_{}".format(config.datasets["valid-overall"]) # Too messy to add everything here.
	predcatpath = config.great3.subpath(subfield, "val", valname + ".pkl")
	figpredcatpath = config.great3.subpath(subfield, "val", valname + ".png")

	skip = False # Set to true to just make the plot without recomputing predictions
	if skip == False:
		catpath = config.great3.subpath(subfield, "simmeas", config.datasets["valid-overall"], "groupmeascat.pkl")
		cat = momentsml.tools.io.readpickle(catpath)
		#print momentsml.tools.table.info(cat)
	
	
		sheartraindir = config.great3.subpath(subfield, "ml", config.datasets["train-shear"])
		predcat = momentsml.learn.tenbilacrun.predict(cat, config.shearconflist , sheartraindir)
	
		if len(config.weightconflist) > 0:
		
			weighttraindir = config.great3.subpath(subfield, "ml", config.datasets["train-weight"])
			predcat = momentsml.learn.tenbilacrun.predict(predcat, config.weightconflist , weighttraindir)
		
		momentsml.tools.io.writepickle(predcat, predcatpath)
	else:
		predcat = momentsml.tools.io.readpickle(predcatpath)

	shearconfnames = momentsml.learn.tenbilacrun.confnames(config.shearconflist)
	for (confname, conf) in zip(shearconfnames, config.shearconflist):

		predcatcopy = predcat.copy() # As plots modifies it.
		if "s2" in conf[0] or "g2" in conf[0]:
			component = 2
		else:
			component = 1
		
		figpredcatpath = config.great3.subpath(subfield, "val", valname + "_" + str(component) + ".png")
		plot_3_valw.plot(predcatcopy, component, filepath=figpredcatpath)
		
