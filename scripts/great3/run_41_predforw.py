import matplotlib
matplotlib.use("AGG")

import momentsml.tools
import momentsml.learn
import momentsml

import config
import numpy as np
import os


import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)



for subfield in config.great3.subfields:

	logger.info("Working on subfield {}".format(subfield))

	catpath = config.great3.subpath(subfield, "simmeas", config.datasets["train-weight"], "groupmeascat.pkl")
	cat = momentsml.tools.io.readpickle(catpath)
	#print momentsml.tools.table.info(cat)
	#exit()
	
	traindir = config.great3.subpath(subfield, "ml", config.datasets["train-shear"])
	predcat = momentsml.learn.tenbilacrun.predict(cat, config.shearconflist, traindir)

	predcatpath = config.great3.subpath(subfield, "simmeas", config.datasets["train-weight"], "groupmeascat_predforw.pkl")
	momentsml.tools.io.writepickle(predcat, predcatpath)
	
	
