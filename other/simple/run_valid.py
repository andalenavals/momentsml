import matplotlib
matplotlib.use("AGG")

execfile("config.py")

import simparams
import mlparams


cat = momentsml.tools.io.readpickle(os.path.join(workdir, "SimpleS1v", "groupmeascat_cases.pkl"))
#print momentsml.tools.table.info(cat)


cat = momentsml.learn.run.predict(cat,
	os.path.join(workdir, "train1_SimpleS1")
	, mlparams.trainparamslist)

#print momentsml.tools.table.info(cat)

momentsml.tools.io.writepickle(cat, os.path.join(workdir, "validcat.pkl"))

#exit()

