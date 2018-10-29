import config
import measfcts
import os
import numpy as np
import matplotlib.ticker as ticker
import matplotlib

import tenbilac
import momentsml.plot
from momentsml.tools.feature import Feature
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)


#momentsml.plot.figures.set_fancy(14)
from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
rc('text', usetex=True)


workbasedir = os.path.join(config.traindir, config.datasets["tp"])


for (dataconfpath, toolconfpath) in config.shearconflist:

	toolconfig = momentsml.learn.tenbilacrun.readconfig(toolconfpath)
	dataconfig = momentsml.learn.tenbilacrun.readconfig(dataconfpath)
	confname = dataconfig.get("setup", "name") + "_" + toolconfig.get("setup", "name")
	trainworkdir = os.path.join(workbasedir, confname) # We will pass this to Tenbilac
	
	
	tblconfiglist = [("setup", "workdir", trainworkdir)]
	ten = tenbilac.com.Tenbilac(toolconfpath, tblconfiglist)
       
	ten._readmembers()
	
	
	fig = plt.figure(figsize=(6, 3.5))

	ax = fig.add_subplot(1, 1, 1)

	tenbilac.plot.summaryerrevo(ten.committee, ax=ax)       
	
	ax.set_yscale('log')
	ax.set_xscale('log')
	ax.set_xlabel(r"Iteration")
	ax.set_ylim(1e-6, 1e-3)
	ax.set_xlim((5, 1e4))
	ax.set_ylabel(r"MSB cost function value")
	#ax.legend()

	plt.tight_layout()


	momentsml.plot.figures.savefig(os.path.join(config.valdir, config.datasets["ts"] + "_" + confname + "_msbevo"), fig, fancy=True, pdf_transparence=True)
	plt.show()
