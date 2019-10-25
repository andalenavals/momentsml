"""
Shape measurement with GalSim's adaptive moments (from its "hsm" module).
"""

import numpy as np
import sys, os
import copy
from datetime import datetime

import logging
logger = logging.getLogger(__name__)

import astropy.table
import galsim

from astropy.modeling import models, fitting
from astropy.stats import sigma_clip
from astropy.modeling import Fittable2DModel, Parameter
from scipy.special import gamma, gammaincinv

import utils
from .. import tools



def measfct(catalog, runon="img", stampsize=None, **kwargs):
		
	# We get the stamp size to use:
	stampsize = catalog.meta[runon].get_stampsize(stampsize)
	
	# We load the image:
	img = catalog.meta[runon].load()

	# And we pass it, with all required kwargs, to the lower-level function:
	return measure(img, catalog, xname=catalog.meta[runon].xname, yname=catalog.meta[runon].yname, stampsize=stampsize, **kwargs)



class EllipSersic2D(Fittable2DModel):
	"""Custom Sersic Model, with ellipticity defined using (g1, g2), and total flux instead of amplitude
	
	This is based on astropy's Sersic2D from here:
	http://docs.astropy.org/en/stable/api/astropy.modeling.functional_models.Sersic2D.html#astropy.modeling.functional_models.Sersic2D
    
    Relations for the total flux:
    http://ned.ipac.caltech.edu/level5/March05/Graham/Graham2.html
    
    Instructions on how to build new models:
    http://docs.astropy.org/en/stable/modeling/new.html
	
	"""
	
	flux = Parameter(default=1.0, min=0.0)
	r_eff = Parameter(default=1.0, min=0.0001, max=100.0)
	n = Parameter(default=4.0, min=0.1, max=6.0)
	x_0 = Parameter(default=0.0)
	y_0 = Parameter(default=0.0)
	g1 = Parameter(default=0.0, min=-1.0, max=1.0)
	g2 = Parameter(default=0.0, min=-1.0, max=1.0)
   
	@staticmethod
	def evaluate(x_array, y_array, flux, r_eff, n, x_0, y_0, g1, g2):
		
		theta = 0.5 * np.arctan2(g2, g1)
		g = np.hypot(g1, g2)
		a, b = r_eff, r_eff*(1-g)/(1+g)
		
		bn = gammaincinv(2.0*n, 0.5)
		flux_n_factor =  n * np.exp(bn) * bn**(-2.0*n) * gamma(2.0*n)
		amplitude = flux / (2.0 * np.pi * flux_n_factor * a * b) # The amplitude from astropy's Sersic2D
		
		cos_theta, sin_theta = np.cos(theta), np.sin(theta)
		x_maj = (x_array - x_0) * cos_theta + (y_array - y_0) * sin_theta
		x_min = -(x_array - x_0) * sin_theta + (y_array - y_0) * cos_theta
		z = np.hypot(x_maj/a, x_min/b)
		
		return amplitude * np.exp(-bn * (z ** (1 / n) - 1))


def measure(img, catalog, xname="x", yname="y", stampsize=None, prefix="fit_"):
	"""
	
	"""
	
	if type(img) is str:
		logger.debug("You gave me a filepath, and I'm now loading the image...")
		img = tools.image.loadimg(img)
	
	if int(stampsize)%2 != 0:
		raise RuntimeError("The stampsize should be even!")

	starttime = datetime.now()
	logger.info("Starting fit on %ix%i stamps" % (stampsize, stampsize))
	
	# We prepare an output table with all the required columns
	output = astropy.table.Table(copy.deepcopy(catalog), masked=True) # Convert the table to a masked table
	# A bit strange: reading the doc I feel that this conversion is not needed.
	# But without it, it just doesn't result in a masked table once the masked columns are appended.

	output.add_columns([
		astropy.table.Column(name=prefix+"flag", data=np.zeros(len(output), dtype=int)), # We will always have a flag
		astropy.table.MaskedColumn(name=prefix+"flux", dtype=float, length=len(output)),
		astropy.table.MaskedColumn(name=prefix+"x", dtype=float, length=len(output)),
		astropy.table.MaskedColumn(name=prefix+"y", dtype=float, length=len(output)),
		astropy.table.MaskedColumn(name=prefix+"g1", dtype=float, length=len(output)),
		astropy.table.MaskedColumn(name=prefix+"g2", dtype=float, length=len(output)),
		astropy.table.MaskedColumn(name=prefix+"r_eff", dtype=float, length=len(output)),
		astropy.table.MaskedColumn(name=prefix+"n", dtype=float, length=len(output)),
		astropy.table.MaskedColumn(name=prefix+"info_nfev", dtype=int, length=len(output)),
		astropy.table.MaskedColumn(name=prefix+"info_ier", dtype=int, length=len(output))
	])
	
	# We want to mask all these entries. They will get unmasked when values will be attributed.
	for col in ["flux", "x", "y", "g1", "g2", "r_eff", "n", "info_nfev", "info_ier"]:
		output[prefix+col].mask = [True] * len(output) # "True" means masked !
		
	n = len(output)
	
	# And loop
	for gal in output:
		
		# Some simplistic progress indication:
		if gal.index%5000 == 0:
			logger.info("%6.2f%% done (%i/%i) " % (100.0*float(gal.index)/float(n), gal.index, n))
		
		(x, y) = (gal[xname], gal[yname])
		(gps, flag) = tools.image.getstamp(x, y, img, stampsize)
		
		# Ugly copy of the code from getstamp to get the "offset" right:
		x_offset = int(np.round(x - 0.5)) - int(stampsize)/2
		y_offset = int(np.round(y - 0.5)) - int(stampsize)/2
		
		
		if flag != 0:
			logger.debug("Galaxy not fully within image:\n %s" % (str(gal)))
			gal[prefix+"flag"] = flag
			# We can't do anything, and we just skip this galaxy.
			continue
				
		# Do the fit
		
		stamp = gps.array
		weights = np.ones(stamp.shape)
		x_array, y_array = np.meshgrid(np.arange(stampsize), np.arange(stampsize))
		
		
		#ini_flux = np.sum(stamp)
		#ini_r_eff = gal["adamom_sigma"]
		ini_flux = 1000.0
		ini_r_eff = 10.0
		
		
		
		ini_mod = EllipSersic2D(flux=ini_flux, r_eff=ini_r_eff, n=2.0, x_0=stampsize/2.0, y_0=stampsize/2.0, g1=0.0, g2=0.0)

		#fitter = fitting.SLSQPLSQFitter() # Does not work well, it seems
		fitter = fitting.LevMarLSQFitter()
	
		#fit_mod = fitter(ini_mod, x_array, y_array, stamp, weights=weights)
		fit_mod = fitter(ini_mod, x_array, y_array, stamp, weights=weights, maxiter = 1000, acc=1.0e-7, epsilon=1.0e-6, estimate_jacobian=False)

		#fitter.fit_info["nfev"] = 0
		#fitter.fit_info["ierr"] = 0
		

		#logger.debug("Fit results: {}".format(fitter.fit_info["message"]))
		#print fitter.fit_info
		#if fitter.fit_info["ierr"] != 0:
		#print fitter.fit_info["ierr"], fitter.fit_info["message"]
	
	
		gal[prefix+"flux"] = fit_mod.flux.value
		gal[prefix+"x"] = fit_mod.x_0.value + x_offset
		gal[prefix+"y"] = fit_mod.y_0.value + y_offset
		gal[prefix+"g1"] = fit_mod.g1.value
		gal[prefix+"g2"] = fit_mod.g2.value
		gal[prefix+"r_eff"] = fit_mod.r_eff.value
		gal[prefix+"n"] = fit_mod.n.value
		
		gal[prefix+"info_nfev"] = fitter.fit_info["nfev"]
		gal[prefix+"info_ier"] = fitter.fit_info["ierr"]


		# If we made it to this point, we check that the centroid is roughly ok:
		#if np.hypot(x - gal[prefix+"x"], y - gal[prefix+"y"]) > 10.0:
		#	gal[prefix + "flag"] = 2
			
		#if gal[prefix+"flux"] < 0 and gal[prefix + "flag"] > 0:
		#	# The centroid checking is rough
		#	gal[prefix + "flag"] = 4
		

	endtime = datetime.now()	
	logger.info("All done")

	nfailed = np.sum(output[prefix+"flag"] > 0)
	
	logger.info("I failed on %i out of %i sources (%.1f percent)" % (nfailed, n, 100.0*float(nfailed)/float(n)))
	logger.info("This measurement took %.3f ms per galaxy" % (1e3*(endtime - starttime).total_seconds() / float(n)))

	return output
