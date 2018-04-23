"""
Plots the figure of the paper 
"""

import config
import measfcts
import os
import numpy as np
import matplotlib.ticker as ticker
import matplotlib.colors
import matplotlib

import megalut.plot
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)



#megalut.plot.figures.set_fancy(14)
from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
rc('text', usetex=True)



valname = config.wvalname

selstr = "snr-above-10"

if selstr in config.datasets["vo"] and not selstr in config.datasets["tw"]:
	title=r"Retaining only galaxies with S/N $>$ 10.0 for the validation"

elif selstr in config.datasets["vo"] and selstr in config.datasets["tw"]:
	title=r"Retaining galaxies with S/N $>$ 10.0 for the training and the validation"

else:
	title=r"Without specific selection of training or validation galaxies"

valcatpath = os.path.join(config.valdir, valname + ".pkl")
cat = megalut.tools.io.readpickle(valcatpath)


cat["snr"].mask = cat["pre_s1"].mask

"""
newmask = cat["tru_rad"] < 1.0
logger.info("Fraction of gals with rad < 1")
logger.info(float(np.sum(newmask)) / np.size(newmask) )
origmask = cat["pre_s1"].mask
combimask = np.logical_or(newmask, origmask)
cat["pre_s1"].mask = combimask
cat["pre_s2"].mask = combimask
cat["pre_s1w"].mask = combimask
cat["pre_s2w"].mask = combimask
"""


#print megalut.tools.table.info(cat)

for comp in ["1","2"]:

	
	#cat["pre_s{}w_norm".format(comp)] = cat["pre_s{}w".format(comp)] / np.max(cat["pre_s{}w".format(comp)])
	#megalut.tools.table.addrmsd(cat, "pre_s{}".format(comp), "tru_s{}".format(comp))
	
	megalut.tools.table.addstats(cat, "pre_s{}".format(comp), "pre_s{}w".format(comp))
	cat["pre_s{}_wbias".format(comp)] = cat["pre_s{}_wmean".format(comp)] - cat["tru_s{}".format(comp)]


resr = 0.01
wplotrea = -10

snr = Feature("snr", 3.0, 150.0, nicename="S/N", rea=wplotrea)
tru_mag = Feature("tru_mag", 20, 25.7, nicename="Magnitude", rea=wplotrea)
tru_rad = Feature("tru_rad", 0.0, 13.0, nicename=r"Half-light radius $R$ [pix]", rea=wplotrea)



tru_s1 = Feature("tru_s1", nicename=r"$g_1^{\mathrm{true}}$")
tru_s2 = Feature("tru_s2", nicename=r"$g_2^{\mathrm{true}}$")

pre_s1_bias = Feature("pre_s1_bias", -resr, resr, nicename=r"$\langle \hat{g}_{1} \rangle - g_{1}^{\mathrm{true}} $")
pre_s2_bias = Feature("pre_s2_bias", -resr, resr, nicename=r"$\langle \hat{g}_{2} \rangle - g_{2}^{\mathrm{true}} $")
pre_s1_wbias = Feature("pre_s1_wbias", -resr, resr, nicename=r"$\left(\sum\hat{g}_1 w_1 / \sum w_1 \right) - g_{1}^{\mathrm{true}}$")
pre_s2_wbias = Feature("pre_s2_wbias", -resr, resr, nicename=r"$\left(\sum\hat{g}_2 w_2 / \sum w_2 \right) - g_{2}^{\mathrm{true}}$")



#pre_s1_bias = Feature("pre_s1_bias", -resr, resr, nicename=r"Bias on $\hat{g}_{1}$")
#pre_s2_bias = Feature("pre_s2_bias", -resr, resr, nicename=r"Bias on $\hat{g}_{2}$")
#pre_s1_wbias = Feature("pre_s1_wbias", -resr, resr)
#pre_s2_wbias = Feature("pre_s2_wbias", -resr, resr)


def addmetrics(ax, xfeat, yfeat):
	metrics = megalut.tools.metrics.metrics(cat, xfeat, yfeat, pre_is_res=True)
	line1 = r"$10^3 \mu=%.1f \pm %.1f $" % (metrics["m"]*1000.0, metrics["merr"]*1000.0)
	line2 = r"$10^3 c=%.1f \pm %.1f $" % (metrics["c"]*1000.0, metrics["cerr"]*1000.0)
	
	ax.annotate(line1, xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -9), textcoords='offset points', ha='left', va='top', fontsize=12)
	ax.annotate(line2, xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -22), textcoords='offset points', ha='left', va='top', fontsize=12)
	

fig = plt.figure(figsize=(11.5, 3.2))
plt.subplots_adjust(
	left  = 0.08,  # the left side of the subplots of the figure
	right = 0.93,    # the right side of the subplots of the figure
	bottom = 0.15,   # the bottom of the subplots of the figure
	top = 0.85,      # the top of the subplots of the figure
	wspace = 0.40,   # the amount of width reserved for blank space between subplots,
	                # expressed as a fraction of the average axis width
	hspace = 0.25,   # the amount of height reserved for white space between subplots,
					# expressed as a fraction of the average axis heightbottom=0.1, right=0.8, top=0.9)
	)

idlinekwargs = {"color":"black", "ls":"-"}

#==================================================================================================



ax = fig.add_subplot(1, 3, 1)
megalut.plot.scatter.scatter(ax, cat, tru_s1, pre_s1_wbias, showidline=True, idlinekwargs=idlinekwargs, yisres=True)
addmetrics(ax, tru_s1, pre_s1_wbias)

#ax.set_xlabel("")
#ax.set_xticklabels([])
#ax.set_ylabel("")
#ax.set_yticklabels([])


ax = fig.add_subplot(1, 3, 2)
megalut.plot.scatter.scatter(ax, cat, tru_s2, pre_s2_wbias, showidline=True, idlinekwargs=idlinekwargs, yisres=True)
addmetrics(ax, tru_s2, pre_s2_wbias)

#ax.set_ylabel("")
#ax.set_yticklabels([])


ax = fig.add_subplot(1, 3, 3)
cb = megalut.plot.scatter.scatter(ax, cat, tru_mag, tru_rad, snr, cmap="plasma_r", rasterized = True, norm=matplotlib.colors.LogNorm(vmin=5.0, vmax=150.0))
#cb.set_ticks([5, 10, 20, 40, 80, 160])

fig.text(.005, .94, title, fontdict={"fontsize":12})


megalut.plot.figures.savefig(os.path.join(config.valdir, valname + "_selbiaseffect"), fig, fancy=True, pdf_transparence=True)
plt.show()


