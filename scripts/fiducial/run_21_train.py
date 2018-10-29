import matplotlib
matplotlib.use("AGG")

import os

import momentsml.learn

import config

import logging
logger = logging.getLogger(__name__)

import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("snrcut", type=int, help="<S/N>-cut to apply to the training cases")
parser.add_argument("target", type=str, help="Target shear (s) or ellipticity (e)")
args = parser.parse_args()

logger.info("Recieved arguments snrcut:{} and target:{}".format(args.snrcut, args.target))
	

# Getting the path to the correct directories
measdir = os.path.join(config.simmeasdir, config.datasets["tp"])
traindir = os.path.join(config.traindir, config.datasets["tp"])
	
# And to the catalogue
traincatpath = os.path.join(measdir, "groupmeascat.pkl")
cat = momentsml.tools.io.readpickle(traincatpath)
#print momentsml.tools.table.info(cat)


if args.target is "e":
	cat["tru_s1"] = cat["tru_g1"]
	cat["tru_s2"] = cat["tru_g2"]
elif args.target is "s":
	pass
else:
	raise ValueError("Unknown type")


select=True
if select:
	logger.warning("Selection of cases is activated!")
	momentsml.tools.table.addstats(cat, "snr")
	s = momentsml.tools.table.Selector("snrcut", [
		#("max", "adamom_failfrac", 0.01),
		("min", "snr_mean", args.snrcut),
	])
	cat = s.select(cat)



# Running the training
dirnames = momentsml.learn.tenbilacrun.train(cat, config.shearconflist, traindir)




"""
#momentsml.tools.table.addstats(cat, "snr")
#cat.sort("adamom_failfrac")
#cat.sort("magnitude")
#print cat["magnitude", "adamom_failfrac", "snr_mean"][:]
#exit()	
#print momentsml.tools.table.info(cat)
"""


"""	
# Self-predicting

cat = momentsml.tools.io.readpickle(traincatpath) # To get the full catalog with all cases, not just the selected ones
for (dirname, conf) in zip(dirnames, config.shearconflist):

	predcat = momentsml.learn.tenbilacrun.predict(cat, [conf], traindir)
	predcatpath = os.path.join(traindir, "{}_selfpred.pkl".format(dirname))
	momentsml.tools.io.writepickle(predcat, predcatpath)
	figpredcatpath = os.path.join(traindir, "{}_selfpred.png".format(dirname))
		
	if "s2" in conf[0] or "g2" in conf[0]:
		component = 2
	else:
		component = 1
	plot_2_val.plot(predcat, component, mode=config.trainmode, filepath=figpredcatpath)
	
"""
