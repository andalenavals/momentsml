"""
Validation plot on mixed-galaxies data, with optional weights
"""

import momentsml
import momentsmlgreat3
import momentsml.plot
from momentsml.tools.feature import Feature
import matplotlib.pyplot as plt
import numpy as np

import config

import os
import logging
logging.basicConfig(format=config.loggerformat, level=logging.INFO)
logger = logging.getLogger(__name__)



def main():

	print "This is no longer a standalone script"

	


def plot(cat, component, filepath=None, title=None):
	
	#rea = "all"
	rea = -20
	ebarmode = "scatter"
	
	# Adding weights if absent:
	if not "pre_s{}w".format(component) in cat.colnames:
		
		# First putting all weights to 1.0:
		cat["pre_s{}w".format(component)] = np.ones(cat["adamom_g1"].shape)
		
		"""
		# Keeping only the best half of SNR
		momentsml.tools.table.addstats(cat, "snr")
		for row in cat:
			row["pre_s{}w".format(component)] = np.array(row["snr"] > row["snr_med"], dtype=np.float)
		"""
		
		# Keeping the best half of sigma
		momentsml.tools.table.addstats(cat, "adamom_sigma")
		for row in cat:
			row["pre_s{}w".format(component)] = np.array(row["adamom_sigma"] > row["adamom_sigma_med"], dtype=np.float)
		
		
		
		#print momentsml.tools.table.info(cat)
		
		cat["pre_s{}w_norm".format(component)] = cat["pre_s{}w".format(component)] / np.max(cat["pre_s{}w".format(component)])
	
	momentsml.tools.table.addrmsd(cat, "pre_s{}".format(component), "tru_s{}".format(component))

	momentsml.tools.table.addstats(cat, "pre_s{}".format(component), "pre_s{}w".format(component))
	cat["pre_s{}_wbias".format(component)] = cat["pre_s{}_wmean".format(component)] - cat["tru_s{}".format(component)]
	
	pre_scw = Feature("pre_s{}w".format(component), rea=rea)
	pre_scw_norm = Feature("pre_s{}w_norm".format(component), rea=rea)
	
	pre_sc = Feature("pre_s{}".format(component), rea=rea)
	
	pre_sc_bias = Feature("pre_s{}_bias".format(component))
	pre_sc_wbias = Feature("pre_s{}_wbias".format(component))
	
	pre_sc_mean = Feature("pre_s{}_mean".format(component), -0.13, 0.13)
	pre_sc_wmean = Feature("pre_s{}_wmean".format(component), -0.13, 0.13)
	
	tru_sc = Feature("tru_s{}".format(component), -0.13, 0.13)
		


	fig = plt.figure(figsize=(20, 12))
	if title is not None:
		fig.suptitle(title)

	ax = fig.add_subplot(3, 4, 1)
	momentsml.plot.scatter.scatter(ax, cat, tru_sc, pre_sc, pre_scw)
	
	ax = fig.add_subplot(3, 4, 5)
	if component ==1:
		theother=Feature("tru_g2", rea=rea)
	else:
		theother=Feature("tru_g1", rea=rea)
	momentsml.plot.scatter.scatter(ax, cat, Feature("snr", rea=rea), pre_scw, theother)
	
	ax = fig.add_subplot(3, 4, 6)
	momentsml.plot.hist.hist(ax, cat, pre_scw)

	ax = fig.add_subplot(3, 4, 7)
	momentsml.plot.scatter.scatter(ax, cat, Feature("adamom_sigma", rea=rea), Feature("adamom_flux", rea=rea), featc=pre_scw)
	
	ax = fig.add_subplot(3, 4, 8)
	momentsml.plot.scatter.scatter(ax, cat, Feature("tru_rad", rea=rea), Feature("tru_flux", rea=rea), featc=pre_scw)



	ax = fig.add_subplot(3, 4, 9)
	momentsml.plot.bin.bin(ax, cat, tru_sc, pre_sc_bias, showidline=True,  metrics=True, yisres=True)
	ax.set_title("Without weights")

	ax = fig.add_subplot(3, 4, 10)
	momentsml.plot.scatter.scatter(ax, cat, tru_sc, pre_sc_bias, showidline=True, metrics=True, yisres=True)
	ax.set_title("Without weights")
	
	ax = fig.add_subplot(3, 4, 11)
	momentsml.plot.bin.bin(ax, cat, tru_sc, pre_sc_wbias, showidline=True, metrics=True, yisres=True)
	ax.set_title("With weights")

	ax = fig.add_subplot(3, 4, 12)
	momentsml.plot.scatter.scatter(ax, cat, tru_sc, pre_sc_wbias, showidline=True, metrics=True, yisres=True)
	ax.set_title("With weights")

	
	plt.tight_layout()

	if filepath:
		logger.info("Writing plot to '{}'...".format(filepath))
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.


if __name__ == "__main__":
    main()
	
