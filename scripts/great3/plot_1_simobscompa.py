"""
Classic simobscompa plot
"""
import matplotlib
matplotlib.use("AGG")

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

	
	for subfield in config.great3.subfields:
		
		spname = config.datasets["simobscompa"]
		plotpath = config.great3.subpath(subfield, "simmeas", "{}.png".format(spname))
		#plotpath = None
		if config.great3.skipdone and os.path.exists(plotpath):
			logger.info("Subfield {} is already done".format(subfield))
			continue
		
		measdir = config.great3.subpath(subfield, "simmeas")

		simcat = momentsml.tools.io.readpickle(os.path.join(measdir, spname, "groupmeascat.pkl"))
		#print momentsml.tools.table.info(simcat)


		obscat = momentsml.tools.io.readpickle(config.great3.subpath(subfield, "obs", "img_meascat.pkl"))
		#print momentsml.tools.table.info(obscat)
		#obscat = obscat[:1000]
			
		plot(simcat, obscat, filepath=plotpath)
		logger.info("Plotted to {}".format(plotpath))




def plot(simcat, obscat, filepath=None):

	# Some computations
	simcat["aperphot_sbr1"] = simcat["aperphot_sb2"] / simcat["aperphot_sb5"]
	obscat["aperphot_sbr1"] = obscat["aperphot_sb2"] / obscat["aperphot_sb5"]

	simcat["aperphot_sbr2"] = simcat["aperphot_sb3"] / simcat["aperphot_sb8"]
	obscat["aperphot_sbr2"] = obscat["aperphot_sb3"] / obscat["aperphot_sb8"]

	simcat["aperphot_log_sb2"] = np.log10(simcat["aperphot_sb2"])
	simcat["aperphot_log_sb5"] = np.log10(simcat["aperphot_sb5"])
	obscat["aperphot_log_sb2"] = np.log10(obscat["aperphot_sb2"])
	obscat["aperphot_log_sb5"] = np.log10(obscat["aperphot_sb5"])


	simcat["adamom_log_flux"] = np.log10(simcat["adamom_flux"])
	obscat["adamom_log_flux"] = np.log10(obscat["adamom_flux"])

	
	rea = None

	adamom_flux = Feature("adamom_flux", rea=rea)
	adamom_sigma = Feature("adamom_sigma", 0, 10, rea=rea)
	adamom_rho4 = Feature("adamom_rho4", 1.3, 3.0, rea=rea)
	adamom_g1 = Feature("adamom_g1", -0.7, 0.7, rea=rea)
	adamom_g2 = Feature("adamom_g2", -0.7, 0.7, rea=rea)
	adamom_log_flux = Feature("adamom_log_flux", rea=rea)
	aperphot_sbr1 = Feature("aperphot_sbr1", rea=rea)
	aperphot_sbr2 = Feature("aperphot_sbr2", rea=rea)
	snr = Feature("snr", -3, 30, rea=rea)
	aperphot_sb2 = Feature("aperphot_sb2", 0, 5, rea=rea)
	aperphot_sb3 = Feature("aperphot_sb3", 0, 5, rea=rea)
	aperphot_sb5 = Feature("aperphot_sb5", 0, 5, rea=rea)
	aperphot_sb8 = Feature("aperphot_sb8", 0, 5, rea=rea)
	aperphot_log_sb5 = Feature("aperphot_log_sb5", rea=rea)
	aperphot_log_sb2 = Feature("aperphot_log_sb2", rea=rea)
	skymad = Feature("skymad", rea=rea)
	skystd = Feature("skystd", rea=rea)
	skymed = Feature("skymed", rea=rea)
	skymean = Feature("skymean", rea=rea)

	#psf_adamom_g1 = Feature("psf_adamom_g1", -0.06, 0.06, rea=rea)
	#psf_adamom_g2 = Feature("psf_adamom_g2", -0.06, 0.06, rea=rea)
	#psf_adamom_sigma = Feature("psf_adamom_sigma", rea=rea)





	fig = plt.figure(figsize=(24, 14))
	#fig = plt.figure(figsize=(8, 8))

	ax = fig.add_subplot(3, 5, 1)

	momentsml.plot.contour.simobs(ax, simcat, obscat, adamom_g1, adamom_g2, plotpoints=False, nlines=2)
	#momentsml.plot.hist.hist(ax, simcat, snr, color="red", label="Training", normed=True)
	#momentsml.plot.hist.hist(ax, obscat, snr, color="blue", label="GREAT3", normed=True)

	ax = fig.add_subplot(3, 5, 2)
	momentsml.plot.scatter.simobs(ax, simcat, obscat, adamom_g1, adamom_g2)
	
	ax = fig.add_subplot(3, 5, 3)
	momentsml.plot.scatter.simobs(ax, simcat, obscat, snr, adamom_sigma, legend=True)

	ax = fig.add_subplot(3, 5, 4)
	momentsml.plot.scatter.simobs(ax, simcat, obscat, adamom_flux, adamom_sigma)

	ax = fig.add_subplot(3, 5, 5)
	momentsml.plot.scatter.simobs(ax, simcat, obscat, Feature("adamom_flux", 0, 80, rea=rea), Feature("adamom_sigma", 0.5, 3.5, rea=rea))
	

	ax = fig.add_subplot(3, 5, 6)
	momentsml.plot.scatter.simobs(ax, simcat, obscat, aperphot_sb2, aperphot_sb3)

	ax = fig.add_subplot(3, 5, 7)
	momentsml.plot.scatter.simobs(ax, simcat, obscat, aperphot_sb5, aperphot_sb8)

	ax = fig.add_subplot(3, 5, 8)
	momentsml.plot.scatter.simobs(ax, simcat, obscat, aperphot_sbr1, aperphot_sbr2)

	ax = fig.add_subplot(3, 5, 9)
	momentsml.plot.scatter.simobs(ax, simcat, obscat, adamom_log_flux, adamom_sigma)




	ax = fig.add_subplot(3, 5, 11)
	momentsml.plot.contour.simobs(ax, simcat, obscat, skymad, skymean, plotpoints=False)

	ax = fig.add_subplot(3, 5, 12)
	momentsml.plot.scatter.simobs(ax, simcat, obscat, aperphot_log_sb2, aperphot_log_sb5)

	ax = fig.add_subplot(3, 5, 13)
	momentsml.plot.scatter.simobs(ax, simcat, obscat, adamom_rho4, adamom_sigma)

	ax = fig.add_subplot(3, 5, 14)
	momentsml.plot.scatter.simobs(ax, simcat, obscat, adamom_log_flux, adamom_rho4)
	#ax.set_xscale("log", nonposx='clip')

	
	#ax = fig.add_subplot(3, 4, 12)
	#momentsml.plot.scatter.simobs(ax, simcat, obscat, psf_adamom_g1, psf_adamom_g2)

	#ax = fig.add_subplot(3, 4, 2)
	#momentsml.plot.scatter.scatter(ax, cat, Feature("tru_s1"), Feature("tru_s2"))

	
	
	plt.tight_layout()

	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.


if __name__ == "__main__":
    main()
	
