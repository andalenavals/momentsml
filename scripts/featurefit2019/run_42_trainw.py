import matplotlib
matplotlib.use("AGG")

import argparse

import momentsml.tools
import momentsml.learn
import momentsml
import tenbilac

import config
import numpy as np
import os
import glob
import shutil



import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)



wtraindir = os.path.join(config.traindir, config.datasets["tw"] + "_with_" + config.datasets["tp"] + "_" + config.sconfname)
catpath = os.path.join(wtraindir, "groupmeascat_predforw.pkl")

cat = momentsml.tools.io.readpickle(catpath)


	
# Running the training	
dirnames = momentsml.learn.tenbilacrun.train(cat, config.weightconflist, wtraindir)

print dirnames

#dirnames = ["ada4s1w_sum33wmassshort", "ada4s2w_sum33wmassshort"]

