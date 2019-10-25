import momentsml
import momentsml.plot
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

adamom_x = Feature("adamom_x")
adamom_y = Feature("adamom_y")
adamom_flux = Feature("adamom_flux")
adamom_sigma = Feature("adamom_sigma")
adamom_rho4 = Feature("adamom_rho4")
adamom_g1 = Feature("adamom_g1")
adamom_g2 = Feature("adamom_g2")


fit_x = Feature("fit_x")
fit_y = Feature("fit_y")
fit_flux = Feature("fit_flux")
fit_r_eff = Feature("fit_r_eff")
fit_n = Feature("fit_n")
fit_g1 = Feature("fit_g1")
fit_g2 = Feature("fit_g2")

fit_info_ier = Feature("fit_info_ier")
fit_info_nfev = Feature("fit_info_nfev")



#snr = Feature("snr", nicename="Measured S/N")
#tru_rad = Feature("tru_rad", nicename="True half-light radius [pixel]")
#tru_mag = Feature("tru_mag", nicename="Magnitude")
#tru_sersicn = Feature("tru_sersicn", nicename="True Sersic index")


color_feature = fit_info_nfev

ax = fig.add_subplot(2, 3, 1)
momentsml.plot.scatter.scatter(ax, cat, adamom_g1, fit_g1, color_feature)
ax = fig.add_subplot(2, 3, 2)
momentsml.plot.scatter.scatter(ax, cat, adamom_g2, fit_g2, color_feature)
ax = fig.add_subplot(2, 3, 3)
momentsml.plot.scatter.scatter(ax, cat, adamom_flux,  fit_flux, color_feature)
ax = fig.add_subplot(2, 3, 4)
momentsml.plot.scatter.scatter(ax, cat, adamom_sigma,  fit_r_eff, color_feature)
ax = fig.add_subplot(2, 3, 5)
momentsml.plot.scatter.scatter(ax, cat, adamom_rho4,  fit_n, color_feature)
ax = fig.add_subplot(2, 3, 6)
momentsml.plot.scatter.scatter(ax, cat, adamom_x,  fit_x, color_feature)


"""
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
"""



plt.tight_layout()
plt.show()
plt.close(fig) # Helps releasing memory when calling in large loops.


