"""
Validation plot
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



#trainspname = "G3CGCSersics_train_nn_20rea"
#trainspname = "G3CGCSersics_train_nn_2rea"
#trainspname = "G3CGCSersics_train_shear_snc10000"
#trainspname = "G3CGCSersics_train_shear_snc100_nn"
trainspname = "G3CGCSersics_train_shear_snc100_nn_G3"



#predname = "ada4_sum55_statshear_20000its"
predname = "ada4_sum55_statshear"


component = 1 # which shear component


def main():


	for subfield in config.great3.subfields:
		
		catpath = config.great3.path("ml", "%03i" % subfield, trainspname, "predcat_{}.pkl".format(predname))
		cat = momentsml.tools.io.readpickle(catpath)
		
		cat["pre_s1w"] = np.ones(cat["pre_s1"].shape) * cat["snr"] > 3
		
		print momentsml.tools.table.info(cat)
		
			
		plotpath = None
		#plotpath = config.great3.path("ml","%03i" % subfield, "valplot_{}_comp{}.png".format(predname, component))
		
		plot(cat, component, filepath=plotpath)
		logger.info("Plotted to {}".format(plotpath))




def plot(cat, component, filepath=None):
	
	rea = "all"
	#rea = -20
	#ebarmode = "scatter"
	
	if component == 1:
	
		if "pre_s1w" in cat.colnames:
		
			cat["pre_s1w_norm"] = cat["pre_s1w"] / np.max(cat["pre_s1w"])
			momentsml.tools.table.addstats(cat, "pre_s1", "pre_s1w")
			pre_sc_wmean = Feature("pre_s1_wmean", -0.13, 0.13)		
			pre_scw = Feature("pre_s1w", rea=rea)
			pre_scw_norm = Feature("pre_s1w_norm", rea=rea)
		
		else:
			momentsml.tools.table.addstats(cat, "pre_s1")
	
		momentsml.tools.table.addrmsd(cat, "pre_s1", "tru_s1")
		
		pre_sc = Feature("pre_s1", rea=rea)
		pre_sc_bias = Feature("pre_s1_bias", -0.05, 0.05)
		pre_sc_mean = Feature("pre_s1_mean", -0.13, 0.13)
		tru_sc = Feature("tru_s1", -0.13, 0.13)
		tru_sc2 = Feature("tru_s2", -0.13, 0.13)
		
	elif component == 2:
		pass
		
		
	print momentsml.tools.table.info(cat)

	fig = plt.figure(figsize=(24, 12))

	ax = fig.add_subplot(3, 5, 1)
	momentsml.plot.bin.bin(ax, cat, tru_sc, pre_sc_bias,  metrics=True)
	ax.set_title(trainspname)
		
	ax = fig.add_subplot(3, 5, 2)
	momentsml.plot.scatter.scatter(ax, cat, tru_sc, pre_sc_bias, showidline=True, metrics=True, yisres=True)
	ax.set_title(predname)

	ax = fig.add_subplot(3, 5, 3)
	momentsml.plot.scatter.scatter(ax, cat, tru_sc, Feature("pre_s1_wmean"), tru_sc2, showidline=True, metrics=True, yisres=False)
	ax.set_title(predname)

	ax = fig.add_subplot(3, 5, 4)
	momentsml.plot.hist.hist(ax, cat, pre_scw)
	ax.set_title(predname)

	rea=-400
	ax = fig.add_subplot(3, 5, 6)
	momentsml.plot.scatter.scatter(ax, cat[0:1], Feature("tru_sb", rea=rea), Feature("tru_sersicn", rea=rea))
	ax.set_title("First case")

	ax = fig.add_subplot(3, 5, 7)
	momentsml.plot.scatter.scatter(ax, cat[0:1], Feature("tru_g1", rea=rea), Feature("tru_g2", rea=rea))
	ax.set_title("First case")

	ax = fig.add_subplot(3, 5, 8)
	momentsml.plot.scatter.scatter(ax, cat[0:1], Feature("tru_flux", rea=rea), Feature("tru_rad", rea=rea))
	ax.set_title("First case")

	ax = fig.add_subplot(3, 5, 9)
	momentsml.plot.scatter.scatter(ax, cat[0:1], Feature("tru_s1", rea=rea), Feature("tru_s2", rea=rea))
	ax.set_title("First case")

	#print cat[0:1]

	"""
	ax = fig.add_subplot(3, 5, 7)
	momentsml.plot.scatter.scatter(ax, cat, tru_sc, pre_sc_wmean, showidline=True, metrics=True)
	ax.set_title("With weights")
	
	ax = fig.add_subplot(3, 5, 8)
	momentsml.plot.hist.hist(ax, cat, pre_scw)
	
	
	
	#ax = fig.add_subplot(3, 5, 3)
	#momentsml.plot.scatter.scatter(ax, cat, Feature("tru_rad", rea=rea), Feature("tru_flux", rea=rea), featc=Feature("pre_g1w", rea=rea))

	"""
	"""
	ax = fig.add_subplot(3, 5, 1)
	momentsml.plot.scatter.scatter(ax, cat, tru_sc,  pre_gc_mean, featc=snr_mean, showidline=True, metrics=True)
	
	ax = fig.add_subplot(3, 5, 2)
	momentsml.plot.scatter.scatter(ax, cat, tru_sc, Feature("snr_mean"), pre_gc_bias)
	ax = fig.add_subplot(3, 5, 3)
	momentsml.plot.scatter.scatter(ax, cat, tru_sc, Feature("tru_rad"), pre_gc_bias)
	ax = fig.add_subplot(3, 5, 4)
	momentsml.plot.scatter.scatter(ax, cat, tru_sc, Feature("tru_sersicn"), pre_gc_bias)
	ax = fig.add_subplot(3, 5, 5)
	momentsml.plot.scatter.scatter(ax, cat, tru_sc, Feature("tru_g"), pre_gc_bias)

	
	ax = fig.add_subplot(3, 5, 6)
	momentsml.plot.scatter.scatter(ax, cat, tru_sc,  Feature("tru_sb"), pre_gc_bias)
	ax = fig.add_subplot(3, 5, 7)
	momentsml.plot.scatter.scatter(ax, cat, tru_sc,  Feature("adamom_frac"), pre_gc_bias)
	ax = fig.add_subplot(3, 5, 8)
	momentsml.plot.scatter.scatter(ax, cat, tru_sc,  Feature("tru_flux"), pre_gc_bias)
	ax = fig.add_subplot(3, 5, 9)
	momentsml.plot.scatter.scatter(ax, cat, tru_sc,  Feature("adamom_flux", rea=1), pre_gc_bias)
	#momentsml.plot.scatter.scatter(ax, cat, tru_sc,  Feature("adamom_flux_mean"), pre_gc_bias)
	ax = fig.add_subplot(3, 5, 10)
	momentsml.plot.scatter.scatter(ax, cat, tru_sc,  Feature("adamom_sigma", rea=1), pre_gc_bias)

	
	ax = fig.add_subplot(3, 5, 11)
	momentsml.plot.bin.res(ax, cat, tru_sc, pre_gc_mean, Feature("tru_sb"), ncbins=3, equalcount=True, ebarmode=ebarmode)
	ax = fig.add_subplot(3, 5, 12)
	momentsml.plot.bin.res(ax, cat, tru_sc, pre_gc_mean, Feature("tru_flux"), ncbins=3, equalcount=True, ebarmode=ebarmode)
	ax = fig.add_subplot(3, 5, 13)
	momentsml.plot.bin.res(ax, cat, tru_sc, pre_gc_mean, Feature("tru_rad"), ncbins=3, equalcount=True, ebarmode=ebarmode)
	ax = fig.add_subplot(3, 5, 14)
	momentsml.plot.bin.res(ax, cat, tru_sc, pre_gc_mean, Feature("tru_sersicn"), ncbins=3, equalcount=True, ebarmode=ebarmode)
	ax = fig.add_subplot(3, 5, 15)
	momentsml.plot.bin.res(ax, cat, tru_sc, pre_gc_mean, Feature("tru_g"), ncbins=3, equalcount=True, ebarmode=ebarmode)

	"""
	
	
	plt.tight_layout()

	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.


if __name__ == "__main__":
    main()
	
