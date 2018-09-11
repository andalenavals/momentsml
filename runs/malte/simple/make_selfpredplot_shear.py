execfile("config.py")

from momentsml.tools.feature import Feature

import matplotlib
import matplotlib.pyplot as plt

import numpy as np


cat = momentsml.tools.io.readpickle(os.path.join(workdir, "train1_SimpleS1", "precat.pkl"))
#cat = momentsml.tools.io.readpickle(os.path.join(workdir, "validcat.pkl"))

print momentsml.tools.table.info(cat)



for col in ["pre_s1", "pre_s2", "snr"]:
	momentsml.tools.table.addstats(cat, col)
momentsml.tools.table.addrmsd(cat, "pre_s1", "tru_s1")
momentsml.tools.table.addrmsd(cat, "pre_s2", "tru_s2")

print momentsml.tools.table.info(cat)


fig = plt.figure(figsize=(20, 13))


ax = fig.add_subplot(3, 4, 1)
momentsml.plot.scatter.scatter(ax, cat, Feature("tru_rad", rea=1),  Feature("tru_sersicn", rea="full"), sidehists=True, sidehistkwargs={"bins":20})
ax = fig.add_subplot(3, 4, 2)
momentsml.plot.scatter.scatter(ax, cat, Feature("adamom_sigma", rea="full"), Feature("tru_rad", rea="full"))
ax = fig.add_subplot(3, 4, 3)
momentsml.plot.scatter.scatter(ax, cat, Feature("tru_s2"), Feature("tru_rad", rea="full"), Feature("pre_s2_bias"))
ax = fig.add_subplot(3, 4, 4)
momentsml.plot.scatter.scatter(ax, cat, Feature("tru_s1"), Feature("tru_rad", rea="full"), Feature("pre_s1_bias"))

ax = fig.add_subplot(3, 4, 5)
momentsml.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_s1", rea="full"), ebarmode="scatter")
ax = fig.add_subplot(3, 4, 6)
momentsml.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_s1", rea="full"), Feature("tru_flux"), ncbins=3, equalcount=True, ebarmode="scatter")
ax = fig.add_subplot(3, 4, 7)
momentsml.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_s1", rea="full"), Feature("tru_rad", rea="full"), ncbins=3, equalcount=True, ebarmode="scatter")
ax = fig.add_subplot(3, 4, 8)
momentsml.plot.bin.res(ax, cat, Feature("tru_s1"), Feature("pre_s1", rea="full"), Feature("tru_g", rea="full"), ncbins=3, equalcount=True, ebarmode="scatter")

ax = fig.add_subplot(3, 4, 9)
momentsml.plot.bin.res(ax, cat, Feature("tru_s2"), Feature("pre_s2", rea="full"), ebarmode="scatter")
ax = fig.add_subplot(3, 4, 10)
momentsml.plot.bin.res(ax, cat, Feature("tru_s2"), Feature("pre_s2", rea="full"), Feature("tru_flux", rea="full"), ncbins=3, equalcount=True, ebarmode="scatter")
ax = fig.add_subplot(3, 4, 11)
momentsml.plot.bin.res(ax, cat, Feature("tru_s2"), Feature("pre_s2", rea="full"), Feature("tru_rad", rea="full"), ncbins=3, equalcount=True, ebarmode="scatter")
ax = fig.add_subplot(3, 4, 12)
momentsml.plot.bin.res(ax, cat, Feature("tru_s2"), Feature("pre_s2", rea="full"), Feature("tru_g", rea="full"), ncbins=3, equalcount=True, ebarmode="scatter")


plt.tight_layout()
plt.show()
plt.close(fig) # Helps releasing memory when calling in large loops.


