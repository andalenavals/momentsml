
import momentsml
import momentsml.plot

import os

from momentsml.tools.feature import Feature
import config

import matplotlib
import matplotlib.pyplot as plt

import numpy as np


cat = momentsml.tools.io.readpickle(os.path.join(config.simmeasdir, config.datasets["tp"], "groupmeascat.pkl"))
#print momentsml.tools.table.info(cat)

fig = plt.figure(figsize=(8, 8))

ax = fig.add_subplot(2, 2, 1)
momentsml.plot.scatter.scatter(ax, cat, Feature("snr", rea=1),  Feature("adamom_failfrac"), sidehists=True)

ax = fig.add_subplot(2, 2, 2)
momentsml.plot.scatter.scatter(ax, cat, Feature("tru_sb"), Feature("tru_rad"), Feature("adamom_failfrac"))


plt.tight_layout()
plt.show()
plt.close(fig) # Helps releasing memory when calling in large loops.

