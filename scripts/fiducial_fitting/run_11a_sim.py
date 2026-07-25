import matplotlib
matplotlib.use("AGG")

import os
import momentsml
import config
import argparse

import simparams
import measfcts
import numpy as np

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
	
	#####
	#####  Datasets for the fixed-PSF experiement (Section 6)
	#####
	
	if code == "si-1": # Just to quickly draw 1000 galaxies probing the distributions.
		sp = simparams.Fiducial(
			name = code,
			snc_type = 0,
			shear = 0,
			min_tru_sb = 1.0,
			noise_level = 1.0
		)
		drawconf = {
			"n":1000,
			"nc":10,
			"nrea":1,
			"ncat":1,
			"ncpu":1,
			"groupmode":None,
			"skipdone":False	
		}

	elif code == "tp-1": # 8 M
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 2000,
			shear = 0.1,
			noise_level = 1.0,
			min_tru_sb = 1.0,
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":4000,
			"ncpu":10,
			"groupmode":"shear",
			"skipdone":False	
		}


	elif code == "vp-1": # 5000 cases, 10'000 SNC rotations each (50 M)
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 10000,
			shear = 0.1,
			noise_level = 1.0,
			min_tru_sb = 1.0,
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":5000,
			"ncpu":10,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "tw-1": # 20 M
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 0,
			shear = 0.1,
			noise_level = 1.0,
			min_tru_sb = 1.0
		)
		drawconf = {
			"n":100000,
			"nc":1000,
			"nrea":1,
			"ncat":200,
			"ncpu":10,
			"groupmode":"shear",
			"skipdone":False	
		}
	


	elif code == "vo-1": # 20 M
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 0,
			shear = 0.1,
			noise_level = 1.0,
			min_tru_sb = 1.0
		)
		drawconf = {
			"n":100000,
			"nc":100,
			"nrea":1,
			"ncat":200,
			"ncpu":10,
			"groupmode":"shear",
			"skipdone":False	
		}

	
	#####
	#####  Datasets for the variable-PSF experiement (Section 7)
	#####



	elif code == "si-varpsf-1": # Just to quickly draw 1000 galaxies probing the distributions.
		sp = simparams.Fiducial(
			name = code,
			snc_type = 0,
			shear = 0,
			noise_level = 1.0,
			varpsf_type = 1
		)
		drawconf = {
			"n":1000,
			"nc":10,
			"nrea":1,
			"ncat":1,
			"ncpu":1,
			"groupmode":None,
			"skipdone":False	
		}
	

	elif code == "tp-varpsf-1": # similar to tp-2-faint, but with variable psf (10 M)
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 2000,
			shear = 0.1,
			noise_level = 1.0,
			min_tru_sb = 1.0,
			varpsf_type = 1,
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":5000,
			"ncpu":25,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "tp-varpsf-1-pretrain": # ellipticity and low-noise pretraining (1M)
		sp = simparams.Fiducial(
			name = code,
			snc_type = 0, # No SNC
			shear = -1, # No shear here
			noise_level = 0.1,
			min_tru_sb = 1.0,
			varpsf_type = 1,
		)
		drawconf = {
			"n":10000,
			"nc":100,
			"nrea":100,
			"ncat":1,
			"ncpu":25,
			"groupmode":"ellipticity",
			"skipdone":False	
		}


	elif code == "vp-varpsf-1": # 50 M, with variable PSF
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 10000,
			shear = 0.1,
			noise_level = 1.0,
			min_tru_sb = 1.0,
			varpsf_type = 1,
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":5000,
			"ncpu":50,
			"groupmode":"shear",
			"skipdone":False	
		}


	elif code == "tw-varpsf-1": # 1000 cases, 10'000 gals (with 2 fold SNC) (10 M)
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 2,
			shear = 0.1,
			noise_level = 1.0,
			min_tru_sb = 1.0,
			varpsf_type = 1,
		)
		drawconf = {
			"n":5000,
			"nc":100,
			"nrea":1,
			"ncat":1000,
			"ncpu":50,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "vo-varpsf-1":
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 2,
			shear = 0.1,
			noise_level = 1.0,
			min_tru_sb = 1.0,
			varpsf_type = 1,
		)
		drawconf = {
			"n":5000,
			"nc":100,
			"nrea":1,
			"ncat":2000,
			"ncpu":20,
			"groupmode":"shear",
			"skipdone":False	
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


	# Simulating images
	momentsml.sim.run.multi(
		simdir=simdir,
		simparams=sp,
		drawcatkwargs={"n":drawconf["n"], "nc":drawconf["nc"], "stampsize":config.drawstampsize},
		drawimgkwargs={}, 
		psfcat=None, psfselect="random",
		ncat=drawconf["ncat"], nrea=drawconf["nrea"], ncpu=drawconf["ncpu"],
		savepsfimg=False, savetrugalimg=False
	)


if __name__ == '__main__':
	parser = define_parser()
	args = parser.parse_args()
	status = run(configure(args))
	exit(status)

