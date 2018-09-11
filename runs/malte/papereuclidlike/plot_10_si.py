import momentsml
import os
import config
import numpy as np

from momentsml.tools.feature import Feature

import matplotlib
import matplotlib.pyplot as plt



cat = momentsml.tools.io.readpickle(os.path.join(config.simmeasdir, config.datasets["si"], "groupmeascat.pkl"))

#print momentsml.tools.table.info(cat)


fig = plt.figure(figsize=(20, 13))


snr = Feature("snr", 0, 50, nicename="Measured S/N")
tru_rad = Feature("tru_rad", nicename="True half-light radius [pixel]")
tru_mag = Feature("tru_mag", 20, 26.5, nicename="Magnitude")
tru_sersicn = Feature("tru_sersicn", 0, 7, nicename="True Sersic index")

#snr = Feature("snr", nicename="Measured S/N")
#tru_rad = Feature("tru_rad", nicename="True half-light radius [pixel]")
#tru_mag = Feature("tru_mag", nicename="Magnitude")
#tru_sersicn = Feature("tru_sersicn", nicename="True Sersic index")


ax = fig.add_subplot(2, 3, 1)
momentsml.plot.scatter.scatter(ax, cat, tru_sersicn, tru_rad, sidehists=True, sidehistkwargs={"bins":20})
ax = fig.add_subplot(2, 3, 2)
momentsml.plot.scatter.scatter(ax, cat, tru_mag,  tru_rad, sidehists=True, sidehistkwargs={"bins":20})
ax = fig.add_subplot(2, 3, 3)
momentsml.plot.scatter.scatter(ax, cat, tru_mag,  tru_rad, snr)


ax = fig.add_subplot(2, 3, 4)
sel = momentsml.tools.table.Selector("draw", [
		("in", "tru_mag", 24.45, 24.55),
])
limcat = sel.select(cat)
momentsml.plot.scatter.scatter(ax, limcat, snr, tru_rad, sidehists=True, sidehistkwargs={"bins":20})
ax.grid()


ax = fig.add_subplot(2, 3, 5)
momentsml.plot.scatter.scatter(ax, cat, snr, tru_mag)
ax.grid()
ax = fig.add_subplot(2, 3, 6)
momentsml.plot.hist.hist(ax, cat, snr)




plt.tight_layout()
plt.show()
plt.close(fig) # Helps releasing memory when calling in large loops.


