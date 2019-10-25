import galsim
import numpy as np
import os
import astropy
import os
import config
import matplotlib.pyplot as plt


origpsfpath = os.path.join(config.workdir, "sensitivity_testing_psf_p0.fits")

hdul = astropy.io.fits.open(origpsfpath)
hdul.info()

image = hdul[0].data
totflux = np.sum(image)

print "totflux", totflux

image /= totflux


hdul.writeto(config.psffits)

hdul.close()



# Check that the PSF is now normalized:

hdul = astropy.io.fits.open(config.psffits)
hdul.info()
image = hdul[0].data
totflux = np.sum(image)
print "totflux normalized", totflux
hdul.close()
