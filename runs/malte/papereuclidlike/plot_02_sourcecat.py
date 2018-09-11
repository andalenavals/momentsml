import momentsml
import os
import config
import numpy as np

from momentsml.tools.feature import Feature

import matplotlib
import matplotlib.pyplot as plt



cat = momentsml.tools.io.readpickle(os.path.join(config.workdir, "cat.pkl"))

print momentsml.tools.table.info(cat)


fig = plt.figure(figsize=(20, 13))


#tru_rad = Feature("tru_rad", nicename="True half-light radius [pixel]")
#tru_mag = Feature("tru_mag", 20, 25, nicename="Magnitude")
#tru_sersicn = Feature("tru_sersicn", 0, 7, nicename="True Sersic index")

tru_rad = Feature("tru_rad")
tru_mag = Feature("tru_mag")
tru_sersicn = Feature("tru_sersicn")


ax = fig.add_subplot(2, 3, 1)
momentsml.plot.scatter.scatter(ax, cat, tru_sersicn, tru_rad, sidehists=True, sidehistkwargs={"bins":20})
ax = fig.add_subplot(2, 3, 2)
momentsml.plot.scatter.scatter(ax, cat, tru_mag,  tru_rad, sidehists=True, sidehistkwargs={"bins":20})

ax = fig.add_subplot(2, 3, 3)
s = momentsml.tools.table.Selector("select", [
		("in", "tru_mag", 24.25, 24.75),
	])
bincat = s.select(cat)
momentsml.plot.hist.hist(ax, bincat, tru_rad)
s = momentsml.tools.table.Selector("select", [
		("in", "tru_mag", 22.75, 23.25),
	])
bincat = s.select(cat)
momentsml.plot.hist.hist(ax, bincat, tru_rad, color="blue")



plt.tight_layout()
plt.show()
plt.close(fig) # Helps releasing memory when calling in large loops.


