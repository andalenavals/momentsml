import matplotlib
matplotlib.use("AGG")

import os
import momentsml
import config
import argparse

import simparams
import measfcts
import numpy as np

import galsim

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)


def define_parser():
	"""Defines the command line arguments
	"""
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('code', type=str, help='what dataset should be simulated?')
	
	return parser


def configure(args):
	"""Configures settings for the different datasets
	"""
	
	code = args.code

	if code == "si-1-test": # 400 gals
		sp = simparams.EuclidLike(
			name = code,
			snc_type = 0,
			shear = 0,
			dist_type="gems"
		)
		drawconf = {
			"n":40,
			"nc":20,
			"nrea":1,
			"ncat":1,
			"ncpu":1,
			"groupmode":None,
			"skipdone":False	
		}
	
	elif code == "si-1-gems": # 10'000 gals
		sp = simparams.EuclidLike(
			name = code,
			snc_type = 0,
			shear = 0,
			dist_type="gems"
		)
		drawconf = {
			"n":500,
			"nc":5,
			"nrea":1,
			"ncat":20,
			"ncpu":20,
			"groupmode":None,
			"skipdone":False	
		}

	elif code == "si-1-gems-20rea": # 1'000 gals with 20 rea
		sp = simparams.EuclidLike(
			name = code,
			snc_type = 0,
			shear = 0,
			dist_type="gems"
		)
		drawconf = {
			"n":1000,
			"nc":10,
			"nrea":20,
			"ncat":1,
			"ncpu":20,
			"groupmode":None,
			"skipdone":False	
		}


	elif code == "si-1-uni": # 10'000 gals
		sp = simparams.EuclidLike(
			name = code,
			snc_type = 0,
			shear = 0,
			dist_type="uni"
		)
		drawconf = {
			"n":500,
			"nc":5,
			"nrea":1,
			"ncat":20,
			"ncpu":20,
			"groupmode":None,
			"skipdone":False	
		}


	elif code == "si-1-uni-100rea": # 1'000 gals with 100 rea
		sp = simparams.EuclidLike(
			name = code,
			snc_type = 0,
			shear = 0,
			dist_type="uni"
		)
		drawconf = {
			"n":1000,
			"nc":10,
			"nrea":100,
			"ncat":1,
			"ncpu":50,
			"groupmode":None,
			"skipdone":False	
		}





	elif code == "tp-1": # (8 M)
		sp = simparams.EuclidLike_statshear(
			name = code,
			snc_type = 2000,
			shear = 0.1,
			dist_type="uni"
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":4000,
			"ncpu":40,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "tp-05": # (8 M)
		sp = simparams.EuclidLike_statshear(
			name = code,
			snc_type = 2000,
			shear = 0.1,
			dist_type="uni05"
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":4000,
			"ncpu":40,
			"groupmode":"shear",
			"skipdone":False	
		}


	elif code == "tp-1-e": # ellipticity pre-training (1M)
		sp = simparams.EuclidLike(
			name = code,
			snc_type = 0,
			shear = -1, # no shear
			dist_type="uni"
		)
		drawconf = {
			"n":10000,
			"nc":100,
			"nrea":100,
			"ncat":1,
			"ncpu":50,
			"groupmode":"ellipticity",
			"skipdone":False	
		}

	elif code == "tp-05-e": # ellipticity pre-training (1M)
		sp = simparams.EuclidLike(
			name = code,
			snc_type = 0,
			shear = -1, # no shear
			dist_type="uni05"
		)
		drawconf = {
			"n":10000,
			"nc":100,
			"nrea":100,
			"ncat":1,
			"ncpu":100,
			"groupmode":"ellipticity",
			"skipdone":False	
		}


	elif code == "vp-1": # (40 M, huge!)
		sp = simparams.EuclidLike_statshear(
			name = code,
			snc_type = 10000,
			shear = 0.1,
			dist_type="uni"
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":4000,
			"ncpu":40,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "vp-1s": # (1 M, for plot tests)
		sp = simparams.EuclidLike_statshear(
			name = code,
			snc_type = 10000,
			shear = 0.1,
			dist_type="uni"
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":100,
			"ncpu":50,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "vp-1-gems": # (40 M, huge!)
		sp = simparams.EuclidLike_statshear(
			name = code,
			snc_type = 10000,
			shear = 0.1,
			dist_type="gems"
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":4000,
			"ncpu":40,
			"groupmode":"shear",
			"skipdone":False	
		}
		
	elif code == "tw-1": # (no SNC) (20 M)
		sp = simparams.EuclidLike_statshear(
			name = code,
			snc_type = 0,
			shear = 0.1,
			dist_type="gems"
		)
		drawconf = {
			"n":100000,
			"nc":1000,
			"nrea":1,
			"ncat":200,
			"ncpu":50,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "tw-2": # (no SNC) (40 M)
		sp = simparams.EuclidLike_statshear(
			name = code,
			snc_type = 0,
			shear = 0.1,
			dist_type="gems"
		)
		drawconf = {
			"n":200000,
			"nc":1000,
			"nrea":1,
			"ncat":200,
			"ncpu":50,
			"groupmode":"shear",
			"skipdone":False	
		}





	elif code == "tw-1-snc": # (2 M)
		sp = simparams.EuclidLike_statshear(
			name = code,
			snc_type = 2,
			shear = 0.1,
			dist_type="gems"
		)
		drawconf = {
			"n":10000,
			"nc":1000,
			"nrea":1,
			"ncat":200,
			"ncpu":50,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "tw-2-snc": # SNC with 10M
		sp = simparams.EuclidLike_statshear(
			name = code,
			snc_type = 2,
			shear = 0.1,
			dist_type="gems"
		)
		drawconf = {
			"n":20000,
			"nc":1000,
			"nrea":1,
			"ncat":500,
			"ncpu":100,
			"groupmode":"shear",
			"skipdone":False	
		}


	elif code == "vo-1": # (no SNC) (20 M)
		sp = simparams.EuclidLike_statshear(
			name = code,
			snc_type = 0,
			shear = 0.1,
			dist_type="gems"
		)
		drawconf = {
			"n":100000,
			"nc":1000,
			"nrea":1,
			"ncat":200,
			"ncpu":50,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "vo-2": # (no SNC) (40 M)
		sp = simparams.EuclidLike_statshear(
			name = code,
			snc_type = 0,
			shear = 0.1,
			dist_type="gems"
		)
		drawconf = {
			"n":200000,
			"nc":1000,
			"nrea":1,
			"ncat":200,
			"ncpu":50,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "vo-3": # (no SNC) (80 M)
		sp = simparams.EuclidLike_statshear(
			name = code,
			snc_type = 0,
			shear = 0.1,
			dist_type="gems"
		)
		drawconf = {
			"n":400000,
			"nc":2000,
			"nrea":1,
			"ncat":59,
			"ncpu":20,
			"groupmode":"shear",
			"skipdone":True	
		}



	else:
		
		logger.info("Unknown code '{}'".format(code))
		exit()
		
	
	return (sp, drawconf)








def run(configuration):
	"""Draws the simulations and measures them
	"""
	sp, drawconf = configuration
	
	simdir = config.simdir
	measdir = config.simmeasdir

	psfcat = momentsml.tools.io.readpickle(os.path.join(config.workdir, "psfcat.pkl"))

	gsparams = galsim.GSParams(maximum_fft_size=20320)

	# Simulating images
	momentsml.sim.run.multi(
		simdir=simdir,
		simparams=sp,
		drawcatkwargs={"n":drawconf["n"], "nc":drawconf["nc"], "stampsize":config.drawstampsize},
		drawimgkwargs={"gsparams":gsparams, "sersiccut":5.0}, 
		psfcat=psfcat, psfselect="random",
		ncat=drawconf["ncat"], nrea=drawconf["nrea"], ncpu=drawconf["ncpu"],
		savepsfimg=False, savetrugalimg=False
	)


	# Measuring the newly drawn images
	momentsml.meas.run.onsims(
		simdir=simdir,
		simparams=sp,
		measdir=measdir,
		measfct=measfcts.default,
		measfctkwargs={"stampsize":config.stampsize, "gain":simparams.gain},
		ncpu=drawconf["ncpu"],
		skipdone=drawconf["skipdone"]
	)
	

	cat = momentsml.meas.avg.onsims(
		measdir=measdir, 
		simparams=sp,
		task="group",
		groupcols=measfcts.default_groupcols, 
		removecols=measfcts.default_removecols
	)

	momentsml.tools.table.keepunique(cat)
	momentsml.tools.io.writepickle(cat, os.path.join(measdir, sp.name, "groupmeascat.pkl"))
	
	
	# Now we perform some additional computations on this catalog.
	cat = momentsml.tools.io.readpickle(os.path.join(measdir, sp.name, "groupmeascat.pkl"))
	
	if drawconf["groupmode"] == "shear":
	
		#cat = momentsml.tools.table.groupreshape(cat, groupcolnames=["tru_s1", "tru_s2"])
		cat = momentsml.tools.table.fastgroupreshape(cat, groupcolnames=["tru_s1", "tru_s2"])	
	
		momentsml.tools.table.keepunique(cat)
	
	if drawconf["groupmode"] in ["shear", "ellipticity"]:
	
		# For each case, we add the fraction of failed measurements
		nrea = cat["adamom_g1"].shape[1]
		logger.info("We have {} realizations".format(nrea))
		cat["adamom_failfrac"] = np.sum(cat["adamom_g1"].mask, axis=1) / float(nrea)		
	
		#print momentsml.tools.table.info(cat)
		momentsml.tools.io.writepickle(cat, os.path.join(measdir, sp.name, "groupmeascat.pkl"))



if __name__ == '__main__':
	parser = define_parser()
	args = parser.parse_args()
	status = run(configure(args))
	exit(status)

