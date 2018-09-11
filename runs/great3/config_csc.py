"""
Configuration for the GREAT3 scripts.
"""

import momentsmlgreat3 as mg3

loggerformat='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m'


great3 = mg3.great3.GREAT3Run(
	experiment = "control",
	obstype = "space",
	sheartype = "constant",
	datadir = "/vol/fohlen11/fohlen11_1/mtewes/GREAT3",
	truthdir = "/vol/fohlen11/fohlen11_1/mtewes/GREAT3/truth", # Only needed for final analysis plots
	workdir = "/vol/fohlen11/fohlen11_1/mtewes/2017_MomentsML_GREAT3/csc_v2",
	g3publicdir = "/users/mtewes/code/great3-public",
	
	#subfields = [94],
	#subfields = [45],	# CSC best PSF subfields: [45, 75, 136],  worst : [143, 49, 150], 94 could not be measured!
	
	#subfields = [1045],
	#subfields = [0],
	
	subfields = range(0, 200),
	#subfields = range(0, 50),
	#subfields = range(50, 100),
	#subfields = range(100, 150),
	#subfields = range(150, 200),
	
	
	#subfields = range(84, 100),
	
	ncpu = 4,
	skipdone = False
	)



### Script configuration ###

datasets = {
	"train-shear":"ts-ell-nn-train-rea10",
	#"train-shear":"ts-ell-n-train-rea100",
	
		
	"valid-shear":"vs-shear-n-G3-snc1000",
	"train-weight":"tw-200c-1000r",
	#"train-weight":"tw-100c-10000r",
	
	"valid-overall":"vo-200c-8000r",
	#"simobscompa":"simobscompa-G3",
	"simobscompa":"simobscompa-train",
	
	"mimic-great3":"sersicG3subfield"
	#"mimic-great3":"sersicG3subfield_nosnc"
	
}


shearconflist = [
	("mlconfig/ada4g1.cfg", "mlconfig/sum55mass.cfg"), # Comment a line to run on only one component
	("mlconfig/ada4g2.cfg", "mlconfig/sum55mass.cfg")
	#("mlconfig/ada4g1.cfg", "mlconfig/sum55mab.cfg"), # Comment a line to run on only one component
	#("mlconfig/ada4g2.cfg", "mlconfig/sum55mab.cfg")


]

weightconflist = [
	# Used for mass:
	#("mlconfig/ada4s1w.cfg", "mlconfig/sum33wmassshort.cfg"),  ## predcode 1
	#("mlconfig/ada4s2w.cfg", "mlconfig/sum33wmassshort.cfg"),
	
	#("mlconfig/ada4s1w.cfg", "mlconfig/sum33wmab.cfg"),
	#("mlconfig/ada4s2w.cfg", "mlconfig/sum33wmab.cfg"),
	
	("mlconfig/ada5s1w.cfg", "mlconfig/sum55wmass500.cfg"),  ## predcode 2
	("mlconfig/ada5s2w.cfg", "mlconfig/sum55wmass500.cfg"),

	
]

#weightconflist = []

trainmode = "g" # When training for ellipticity, switch this to "g". It's for the plots.

predcode = "2" # String used in file names of GREAT3 predictions. Allows you to keep several predictions side by side.
