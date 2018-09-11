import momentsml
import os
import config
import numpy as np

from momentsml.tools.feature import Feature

import matplotlib
import matplotlib.pyplot as plt



#cat = momentsml.tools.io.readpickle(os.path.join(config.simmeasdir, "si-1-gems-20rea", "groupmeascat.pkl"))
cat = momentsml.tools.io.readpickle(os.path.join(config.simmeasdir, "si-1-uni-100rea", "groupmeascat.pkl"))


momentsml.tools.table.addstats(cat, "snr")

#print momentsml.tools.table.info(cat)
#exit()

fig = plt.figure(figsize=(20, 13))

snr_mean = Feature("snr_mean", 0, 20, nicename="$\\langle \mathrm{S}/\mathrm{N}\\rangle$")

snr = Feature("snr", 0, 50, nicename="Measured S/N")
tru_rad = Feature("tru_rad", nicename="True half-light radius [pixel]")

tru_mag = Feature("tru_mag", 20, 26, nicename="Magnitude")
tru_sersicn = Feature("tru_sersicn", 0, 7, nicename="True Sersic index")

skystd = Feature("skystd")
skymed = Feature("skymed")
adamom_flux = Feature("adamom_flux")
adamom_logflux = Feature("adamom_logflux")
adamom_sigma = Feature("adamom_sigma")
adamom_g1 = Feature("adamom_g1")
adamom_g2 = Feature("adamom_g2")
adamom_g = Feature("adamom_g")
adamom_rho4 = Feature("adamom_rho4")


ax = fig.add_subplot(2, 3, 1)
momentsml.plot.scatter.scatter(ax, cat, tru_mag,  tru_rad, sidehists=True, sidehistkwargs={"bins":20})

ax = fig.add_subplot(2, 3, 2)
momentsml.plot.scatter.scatter(ax, cat, tru_mag,  snr_mean, tru_rad)

ax = fig.add_subplot(2, 3, 3)
momentsml.plot.scatter.scatter(ax, cat, tru_rad,  snr_mean, tru_mag)

ax = fig.add_subplot(2, 3, 4)
momentsml.plot.scatter.scatter(ax, cat, tru_rad, tru_mag, snr_mean)

plt.tight_layout()
plt.show()
plt.close(fig) # Helps releasing memory when calling in large loops.


