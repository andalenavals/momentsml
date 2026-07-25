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

	
# Getting the path to the correct directories
traindir = os.path.join(config.traindir, config.datasets["tp"])
	
# And to the validation catalogue
valcatpath = os.path.join(config.simmeasdir, config.datasets["vp"], "groupmeascat.pkl")
predcatpath = os.path.join(config.valdir, config.valname + ".pkl")


# The prediction:

cat = momentsml.tools.io.readpickle(valcatpath)


predcat = momentsml.learn.tenbilacrun.predict(cat, config.shearconflist, traindir)

momentsml.tools.io.writepickle(predcat, predcatpath)


