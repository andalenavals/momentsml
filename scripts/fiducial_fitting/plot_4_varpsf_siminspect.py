import momentsml
import momentsml.plot

import os
import config
import numpy as np

from momentsml.tools.feature import Feature

import matplotlib
import matplotlib.pyplot as plt



cat = momentsml.tools.io.readpickle(os.path.join(config.simmeasdir, config.datasets["si"], "groupmeascat.pkl"))

print momentsml.tools.table.info(cat)

fig = plt.figure(figsize=(20, 13))


ax = fig.add_subplot(2, 3, 1)
momentsml.plot.scatter.scatter(ax, cat, Feature("tru_psf_x"),  Feature("tru_psf_y"),  Feature("tru_psf_g1"))
ax = fig.add_subplot(2, 3, 2)
momentsml.plot.scatter.scatter(ax, cat, Feature("tru_psf_x"),  Feature("tru_psf_y"),  Feature("tru_psf_g2"))
ax = fig.add_subplot(2, 3, 3)
momentsml.plot.scatter.scatter(ax, cat, Feature("tru_psf_x"),  Feature("tru_psf_y"),  Feature("tru_psf_sigma"))



ax = fig.add_subplot(2, 3, 4)
momentsml.plot.scatter.scatter(ax, cat, Feature("tru_psf_x"), Feature("tru_psf_y"), Feature("adamom_g1"))
ax = fig.add_subplot(2, 3, 5)
momentsml.plot.scatter.scatter(ax, cat, Feature("tru_psf_x"), Feature("tru_psf_y"), Feature("adamom_g2"))
ax = fig.add_subplot(2, 3, 6)
momentsml.plot.scatter.scatter(ax, cat, Feature("tru_psf_x"), Feature("tru_psf_y"), Feature("adamom_sigma"))


plt.tight_layout()
plt.show()
plt.close(fig) # Helps releasing memory when calling in large loops.


