import config
import measfcts
import os
import numpy as np
import matplotlib.ticker as ticker
import matplotlib.colors
import matplotlib

import momentsml.plot
from momentsml.tools.feature import Feature
import matplotlib.pyplot as plt
plt.rc('text', usetex=True)

import logging
logger = logging.getLogger(__name__)


#momentsml.plot.figures.set_fancy(14)
from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
rc('text', usetex=True)

rasterized=True

valcat = os.path.join(config.simmeasdir, config.datasets["vs"], "groupmeascat.pkl")
cat = momentsml.tools.io.readpickle(valcat)

#print momentsml.tools.table.info(cat)

momentsml.tools.table.addstats(cat, "snr")

cat["adamom_goodfrac"] = 1.0 - cat["adamom_failfrac"]


tru_sb = Feature("tru_sb", 0, 16, nicename=r"Surface brightness $S$ [pix$^{-2}$]")
tru_rad = Feature("tru_rad", 1.5, 8.5, nicename=r"Half-light radius $R$ [pix]")

snr_mean = Feature("snr_mean", nicename="$\\langle \mathrm{S}/\mathrm{N}\\rangle$")

successfrac = Feature("adamom_goodfrac", nicename="Measurement success fraction")

for comp in ["1"]:

	
	fig = plt.figure(figsize=(3.5, 6))

	ax = fig.add_subplot(2, 1, 1)
	cb = momentsml.plot.scatter.scatter(ax, cat, tru_sb, tru_rad, featc=snr_mean, cmap="plasma_r", norm=matplotlib.colors.PowerNorm(gamma=1./2.), rasterized=rasterized)
	
	cb.set_ticks([2, 5, 10, 20, 30, 40, 50, 60])
	
	ax = fig.add_subplot(2, 1, 2)
	momentsml.plot.scatter.scatter(ax, cat, tru_sb,  tru_rad, featc=successfrac, cmap="plasma_r", rasterized=rasterized)
	ax.axhline()
	

	
	plt.tight_layout()


	momentsml.plot.figures.savefig(os.path.join(config.valdir, config.datasets["vs"] + "_snr"), fig, fancy=True, pdf_transparence=True)
	plt.show()

