"""
Adds further predictions to an existing predicted validation catalog (to avoid running long preds again and again)
"""
import momentsml.tools
import momentsml.learn
import momentsml

import config
import numpy as np
import os


import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Select the
#predname = "ada4_sum55_valid"
predname = "ada4_sum55"



for subfield in config.great3.subfields:

	logger.info("Working on subfield {}".format(subfield))

	catpath = config.great3.path("ml", "%03i" % subfield, "predcat_{}.pkl".format(predname))
	cat = momentsml.tools.io.readpickle(catpath)
	#print momentsml.tools.table.info(cat)
	
	removes = ["pre_g1w", "pre_g2w"]
	for remove in removes:
		if remove in cat.colnames:
			cat.remove_column(remove)
	
	conflist = [
		("mlconfig/ada2g1w.cfg", config.great3.path("ml", "%03i" % subfield, "ada2g1w_sum33w")),
	]
	
	predcat = momentsml.learn.tenbilacrun.predict(cat, conflist)

	momentsml.tools.io.writepickle(predcat, catpath)
	
	
