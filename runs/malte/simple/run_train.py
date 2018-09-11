import matplotlib
matplotlib.use("AGG")

execfile("config.py")

import simparams
import mlparams
import plots


sp = simparams.Simple1()
sp.name = "SimpleS1"
traindir = os.path.join(workdir, "train1_" + sp.name)


cat = momentsml.tools.io.readpickle(os.path.join(workdir, sp.name, "groupmeascat_cases.pkl"))

#cat["adamom_g"] = np.hypot(cat["adamom_g1"], cat["adamom_g2"])

#print np.tile(np.array(cat["tru_rad"]), (1, 20))

#exit()

#cat["adamom_g1*adamom_sigma"] = cat["adamom_g1"] * cat["adamom_sigma"]#.reshape((1000,1))
#cat["adamom_g1/adamom_sigma"] = cat["adamom_g1"] / cat["adamom_sigma"]#.reshape((1000,1))


#print momentsml.tools.table.info(cat)

#exit()
momentsml.learn.run.train(cat, traindir, mlparams.trainparamslist, ncpu=1)



# Self-predicting
#cat = momentsml.tools.io.readpickle(os.path.join(workdir, sp.name, "groupmeascat_cases.pkl"))
cat = momentsml.learn.run.predict(cat, traindir, mlparams.trainparamslist)
#momentsml.tools.io.writepickle(cat, os.path.join(workdir, sp.name, "precat.pkl"))
momentsml.tools.io.writepickle(cat, os.path.join(traindir, "precat.pkl"))



