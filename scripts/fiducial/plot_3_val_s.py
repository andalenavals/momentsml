"""
Validation plot on training-like data structure, with one galaxy per case
"""

import momentsml

import momentsmlgreat3
import momentsml.plot
from momentsml.tools.feature import Feature
import matplotlib.pyplot as plt
import matplotlib.colors
import numpy as np

import config

import os
import logging
logging.basicConfig(format=config.loggerformat, level=logging.INFO)
logger = logging.getLogger(__name__)




def main():

	print "This is no longer a standalone script"



def plot(cat, component, mode="s", filepath=None, select=None, withweights=False):


	logger.info("Running on component {} with mode {}".format(component, mode))
	#cat["adamom_log_flux"] = np.log10(cat["adamom_flux"])
	#cat["adamom_frac"] = np.sum(cat["adamom_g1"].mask, axis=1)/float(cat["adamom_g1"].shape[1])
	
	prename = "pre_s{}".format(component)
	
	cat["pre_maskedfrac"] = np.sum(cat[prename].mask, axis=1) / float(cat[prename].shape[1])
	#cat["pre_frac"] = (float(cat[prename].shape[1]) - np.sum(cat[prename].mask, axis=1)) / float(cat[prename].shape[1])
	
	#b = cat["tru_s1", "pre_maskedfrac", "adamom_failfrac"]
	#b.show_in_browser()
	#exit()
	#assert np.allclose(["pre_maskedfrac"], cat["adamom_failfrac"])
	
	pre_maskedfrac = Feature("pre_maskedfrac")
	
	momentsml.tools.table.addstats(cat, "adamom_flux")
	momentsml.tools.table.addstats(cat, "adamom_sigma")
	momentsml.tools.table.addstats(cat, "snr")
	snr_mean = Feature("snr_mean")

	
	#print min(cat["adamom_frac"]), max(cat["adamom_frac"]), np.median(cat["adamom_frac"])

	if select is not None:
		cat = select.select(cat)

	#print min(cat["snr_mean"]), max(cat["snr_mean"]), np.median(cat["snr_mean"])
	
	
	momentsml.tools.table.addrmsd(cat, "pre_s{}".format(component), "tru_{}{}".format(mode, component))
	
	if withweights == False:
		momentsml.tools.table.addstats(cat, "pre_s{}".format(component))
		pre_sc_bias = Feature("pre_s{}_bias".format(component))
		pre_sc_mean = Feature("pre_s{}_mean".format(component))

	else: # Then we use weights if available)
		
		if not "pre_s{}w".format(component) in cat.colnames:
			# It doesn't make sense to fake them for this plot, just skip it!
			logger.warning("No weights available, skipping")
			return

		momentsml.tools.table.addstats(cat, "pre_s{}".format(component), wcol="pre_s{}w".format(component))
		cat["pre_s{}_wbias".format(component)] = cat["pre_s{}_wmean".format(component)] - cat["tru_{}{}".format(mode, component)]
		pre_sc_bias = Feature("pre_s{}_wbias".format(component))
		pre_sc_mean = Feature("pre_s{}_wmean".format(component))
	
	tru_sc = Feature("tru_{}{}".format(mode, component))
	

	ebarmode = "scatter"

	fig = plt.figure(figsize=(24, 12))

	ax = fig.add_subplot(3, 5, 1)
	momentsml.plot.scatter.scatter(ax, cat, tru_sc,  pre_sc_mean, featc=snr_mean, showidline=True, metrics=True)
	
	ax = fig.add_subplot(3, 5, 2)
	#momentsml.plot.scatter.scatter(ax, cat, tru_sc, Feature("snr_mean"), pre_sc_bias)
	momentsml.plot.scatter.scatter(ax, cat, tru_sc, Feature("snr", rea=1), pre_sc_bias)
	ax = fig.add_subplot(3, 5, 3)
	cnorm = matplotlib.colors.SymLogNorm(linthresh=0.01)
	momentsml.plot.scatter.scatter(ax, cat, tru_sc, Feature("tru_rad"), pre_sc_bias, norm=cnorm)
	ax = fig.add_subplot(3, 5, 4)
	momentsml.plot.scatter.scatter(ax, cat, tru_sc, Feature("tru_sersicn"), pre_sc_bias)
	ax = fig.add_subplot(3, 5, 5)
	momentsml.plot.scatter.scatter(ax, cat, tru_sc, Feature("tru_g"), pre_sc_bias)

	
	ax = fig.add_subplot(3, 5, 6)
	momentsml.plot.scatter.scatter(ax, cat, Feature("tru_flux"), pre_sc_bias, Feature("tru_rad"))
	ax = fig.add_subplot(3, 5, 7)
	#momentsml.plot.scatter.scatter(ax, cat, tru_sc,  Feature("adamom_frac"), pre_sc_bias)
	momentsml.plot.scatter.scatter(ax, cat, pre_maskedfrac, pre_sc_bias, sidehists=True)
	#ax.set_xscale("log", nonposy='clip')
	
	
	ax = fig.add_subplot(3, 5, 8)
	#momentsml.plot.scatter.scatter(ax, cat, tru_sc,  Feature("tru_flux"), pre_sc_bias, norm=cnorm)
	momentsml.plot.scatter.scatter(ax, cat, tru_sc,  Feature("tru_rad"), pre_sc_bias)
	ax = fig.add_subplot(3, 5, 9)
	#momentsml.plot.scatter.scatter(ax, cat, Feature("tru_flux"), pre_sc_bias, Feature("tru_rad"))
	#momentsml.plot.scatter.scatter(ax, cat, tru_sc,  Feature("adamom_flux_mean"), pre_gc_bias)
	momentsml.plot.scatter.scatter(ax, cat, tru_sc,  Feature("tru_flux"), pre_sc_bias)
	ax = fig.add_subplot(3, 5, 10)
	#momentsml.plot.scatter.scatter(ax, cat, tru_sc,  Feature("adamom_sigma", rea=1), pre_sc_bias)
	#momentsml.plot.scatter.scatter(ax, cat, tru_sc,  Feature("tru_sb"), pre_sc_bias)
	momentsml.plot.scatter.scatter(ax, cat, Feature("tru_flux"), Feature("pre_s{}".format(component), rea=1), Feature("tru_rad"))
	
	
	ax = fig.add_subplot(3, 5, 11)
	momentsml.plot.bin.res(ax, cat, tru_sc, pre_sc_mean, Feature("tru_sb"), ncbins=3, equalcount=True, ebarmode=ebarmode)
	ax = fig.add_subplot(3, 5, 12)
	momentsml.plot.bin.res(ax, cat, tru_sc, pre_sc_mean, Feature("tru_flux"), ncbins=3, equalcount=True, ebarmode=ebarmode)
	ax = fig.add_subplot(3, 5, 13)
	momentsml.plot.bin.res(ax, cat, tru_sc, pre_sc_mean, Feature("tru_rad"), ncbins=3, equalcount=True, ebarmode=ebarmode)
	ax = fig.add_subplot(3, 5, 14)
	momentsml.plot.bin.res(ax, cat, tru_sc, pre_sc_mean, Feature("tru_sersicn"), ncbins=3, equalcount=True, ebarmode=ebarmode)
	ax = fig.add_subplot(3, 5, 15)
	momentsml.plot.bin.res(ax, cat, tru_sc, pre_sc_mean, Feature("tru_g"), ncbins=3, equalcount=True, ebarmode=ebarmode)

	
	
	
	plt.tight_layout()

	if filepath:
		logger.info("Writing plot to '{}'...".format(filepath))
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.


if __name__ == "__main__":
    main()
	
