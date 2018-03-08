import matplotlib
matplotlib.use("AGG")

import os

import megalut.learn

import config

import logging
logger = logging.getLogger(__name__)




select = True

	
# Getting the path to the correct directories
measdir = os.path.join(config.simmeasdir, config.datasets["ts"])
traindir = os.path.join(config.traindir, config.datasets["ts"])
	
# And to the catalogue
traincatpath = os.path.join(measdir, "groupmeascat.pkl")
cat = megalut.tools.io.readpickle(traincatpath)

# This is a special script for targetting ellipticity, we copy true ellipticity into shear so that 
# we can keep pretidcign the same field.

cat["tru_s1"] = cat["tru_g1"]
cat["tru_s2"] = cat["tru_g2"]

print megalut.tools.table.info(cat)

#exit()

#nrea = cat["adamom_g1"].shape[1]
#logger.info("We have {} realizations".format(nrea))
#cat["adamom_failfrac"] = np.sum(cat["adamom_g1"].mask, axis=1) / float(nrea)


exit()
if select:
	s = megalut.tools.table.Selector("fortrain", [
		("max", "adamom_failfrac", 0.01),
	])
	cat = s.select(cat)


# Running the training
dirnames = megalut.learn.tenbilacrun.train(cat, config.shearconflist, traindir)




"""
#megalut.tools.table.addstats(cat, "snr")
#cat.sort("adamom_failfrac")
#cat.sort("magnitude")
#print cat["magnitude", "adamom_failfrac", "snr_mean"][:]
#exit()	
#print megalut.tools.table.info(cat)
"""


"""	
# Self-predicting

cat = megalut.tools.io.readpickle(traincatpath) # To get the full catalog with all cases, not just the selected ones
for (dirname, conf) in zip(dirnames, config.shearconflist):

	predcat = megalut.learn.tenbilacrun.predict(cat, [conf], traindir)
	predcatpath = os.path.join(traindir, "{}_selfpred.pkl".format(dirname))
	megalut.tools.io.writepickle(predcat, predcatpath)
	figpredcatpath = os.path.join(traindir, "{}_selfpred.png".format(dirname))
		
	if "s2" in conf[0] or "g2" in conf[0]:
		component = 2
	else:
		component = 1
	plot_2_val.plot(predcat, component, mode=config.trainmode, filepath=figpredcatpath)
	
"""
