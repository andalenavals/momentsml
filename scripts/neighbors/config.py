import momentsml
import momentsml.learn
import os
import numpy as np

import logging


# A simple logger format:
loggerformat='PID %(process)06d | %(asctime)s | %(levelname)s: %(name)s(%(funcName)s): %(message)s'
# Try this one, it's colorful:
#loggerformat='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m'

#logging.basicConfig(format=loggerformat,level=logging.INFO)


# Give a path to an existing directory in which everything can be written (will get large!)

#workdir = "/vol/fohlen11/fohlen11_1/mtewes/MomentsML/fiducial"
workdir = "/data/git_repositories/momentsml/out/fiducial"

simdir = os.path.join(workdir, "sim")
simmeasdir = os.path.join(workdir, "simmeas")
traindir = os.path.join(workdir, "train")
valdir = os.path.join(workdir, "val")


stampsize = 64 # used for measuring
drawstampsize = stampsize # Used for drawing


datasets = {

	# Fot the fixed-PSF experiment (Section 6)
	"si":"si-1",
	"tp":"tp-1-small",
	"vp":"vp-1-small",
	"tw":"tw-1-small",
	"vo":"vo-1-small",


	# For the variable-PSF experiments (Section 7)
	#"si":"si-varpsf-1",
	#"tp":"tp-varpsf-1", # To speed up, use this one only after a pretraining on "tp-varpsf-1-pretrain", as described in the paper.
	#"tp":"tp-varpsf-1-pretrain", # Special dataset for the pre-training of the point-estimator, without shear, and structured for ellipticity
	#"vp":"vp-varpsf-1",
	#"tw":"tw-varpsf-1",
	#"vo":"vo-varpsf-1",	
	#"si":"si-varpsf-1",
}

# Configuration of the point-estimates

shearconflist = [
	# Typically uncomment a single line at a time to train a component,
	# and then uncomment the 2 lines of both components for the predictions.
	
	# For constant PSF experiements:
	("mlconfig/ada5s1f.cfg", "mlconfig/sum55.cfg"), # <--- We use those
	("mlconfig/ada5s2f.cfg", "mlconfig/sum55.cfg")
	
	# For the variable-PSF experiments:
	
	#    Using the field position as features:
	#("mlconfig/ada7s1f-varpsf-pos.cfg", "mlconfig/sum1010pos.cfg"),
	#("mlconfig/ada7s2f-varpsf-pos.cfg", "mlconfig/sum1010pos.cfg")
	
	#    Using size and ellipticity of the PSF as features:
	#("mlconfig/ada8s1f-varpsf-mom.cfg", "mlconfig/sum1010mom.cfg"),
	#("mlconfig/ada8s2f-varpsf-mom.cfg", "mlconfig/sum1010mom.cfg")
	
]

# Similar configuration for the weight estimator:

weightconflist = [
	("mlconfig/ada5s1wf.cfg", "mlconfig/sum5w.cfg"),
	("mlconfig/ada5s2wf.cfg", "mlconfig/sum5w.cfg")
	
	#("mlconfig/ada7s1wf-varpsf-pos.cfg", "mlconfig/sum10w.cfg"),
	#("mlconfig/ada7s2wf-varpsf-pos.cfg", "mlconfig/sum10w.cfg")
	
	#("mlconfig/ada8s1wf-varpsf-mom.cfg", "mlconfig/sum10w.cfg"),
	#("mlconfig/ada8s2wf-varpsf-mom.cfg", "mlconfig/sum10w.cfg")

]


#######################################################################################################################################

# Some automatically generated names, used for saving figures etc depending on your above settings.
# Not meant to be changed.

sconfname = os.path.splitext(os.path.basename(shearconflist[0][1]))[0] # extracts e.g. "sum55"
valname = "{}_with_{}_on_{}".format(datasets["tp"], sconfname, datasets["vp"])
wconfname = os.path.splitext(os.path.basename(weightconflist[0][1]))[0] # extracts e.g. "sum55w"
wvalname = "{}_and_{}_with_{}_{}_on_{}".format(datasets["tp"], datasets["tw"], sconfname, wconfname, datasets["vo"])

for d in [simdir, traindir, valdir]:
	if not os.path.exists(d):
		os.makedirs(d)
