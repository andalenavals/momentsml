import momentsml
import astropy
import os
import config
import measfcts


cat = astropy.table.Table()

prefix = "psf_"

psfpos = (0.5 + config.psfstampsize/2.0, 0.5 + config.psfstampsize/2.0)

cat = astropy.table.Table([[psfpos[0]], [psfpos[1]]], names=('{}x'.format(prefix), '{}y'.format(prefix)))


# To measure the PSF, we attach the image:
cat.meta["img"] = momentsml.tools.imageinfo.ImageInfo(
    filepath=os.path.join(config.workdir, config.psffits),
    xname="{}x".format(prefix),
    yname="{}y".format(prefix),
    stampsize=config.psfstampsize,
    workdir=os.path.join(config.workdir, "psf_measworkdir"),
	pixelscale= 1.0 / config.psfoversampling
    )

# We measure the PSF. Not really needed, but serves as a check.
# There is no noise, so gain and snr are garbage.
meascat = measfcts.default(cat, stampsize=config.psfstampsize, gain=1.0)

print(meascat[0])

if abs(meascat["skystampsum"] - 1.0) > 0.001:
	raise RuntimeError("PSF is not well normalized ?")

# We do not save the measurement here, as we don't need all those fields to be repeated  in our further galaxy measurement catalogs.
  
momentsml.tools.io.writepickle(cat, os.path.join(config.workdir, "psfcat.pkl"))

