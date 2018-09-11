"""
A demo of plot.stamps.pngstampgrid()
"""

import logging
logging.basicConfig(level=logging.DEBUG)

import momentsml
import momentsml.plot.stamps

print "For this demo to work, run draw_and_measure_sims.py first."


img = "simgalimg.fits"
cat = momentsml.tools.io.readpickle("meascat.pkl")

# Let's illustrate selecting stamps randomly:
cat = momentsml.tools.table.shuffle(cat)


momentsml.plot.stamps.pngstampgrid(img, cat[:20], "stamps.png", stampsize=40)

