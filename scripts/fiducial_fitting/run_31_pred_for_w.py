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




catpath = os.path.join(config.simmeasdir, config.datasets["tw"], "groupmeascat.pkl")
cat = momentsml.tools.io.readpickle(catpath)

#print momentsml.tools.table.info(cat)
#exit()

wtraindir = os.path.join(config.traindir, config.datasets["tw"] + "_with_" + config.datasets["tp"] + "_" + config.sconfname)
os.makedirs(wtraindir)

predcatpath = os.path.join(wtraindir, "groupmeascat_predforw.pkl")


traindir = os.path.join(config.traindir, config.datasets["tp"])

	
predcat = momentsml.learn.tenbilacrun.predict(cat, config.shearconflist, traindir)

momentsml.tools.io.writepickle(predcat, predcatpath)
	
	
