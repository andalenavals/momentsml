#Calling and running function of stampgrid.py for development porpouse.
import simparams_d
import stampgrid_d
import os
import datetime
import tempfile
import pickle
import copy
import multiprocessing
from momentsml import tools
import numpy as np
import argparse
import logging
logger = logging.getLogger(__name__)
import yaml

class _WorkerSettings():
	"""
	A class to hold together all the settings for processing a catalog-realization combination.
	If one day we have different drawimg() functions, we'll just pass this function here as well.
	"""
	
	def __init__(self, catalog, reaindex, drawimgkwargs, workdir):
		"""
		The catalog's catname, reaindex, and workdir define the filepaths in which the image(s)
		drawn with the drawimgkwargs will be written.
		"""
		
		self.catalog = catalog # No copy needed, we won't change it!
		self.reaindex = reaindex
		self.drawimgkwargs = drawimgkwargs # This is already a changed deep copy from the original argument to multi().
		self.workdir = workdir # Stays the same for all workers !
	
		
	def __str__(self):
		"""
		A short string describing these settings
		"""
		return "[catalog '%s', realization %i]" % (self.catalog.meta["catname"], self.reaindex)
	
	
def _worker(ws):
	"""
	Worker function that processes one _WorkerSettings object.
	"""		
	starttime = datetime.datetime.now()
	# Make sure that we indeed start from different seeds
	np.random.seed()
	p = multiprocessing.current_process()
	logger.info("%s is starting to draw %s with PID %s" % (p.name, str(ws), p.pid))
	
	# It's just a single call:
	stampgrid_d.drawimg(ws.catalog, **ws.drawimgkwargs)
	
	endtime = datetime.datetime.now()
	logger.info("%s is done, it took %s" % (p.name, str(endtime - starttime)))


def parse_args():
    parser = argparse.ArgumentParser(description='Basic code to produce simulations with neighbors')
    parser.add_argument('--neighbors_config', default='neighbors_config.yaml',  #default=None,
                        help='yaml config definete properties of neighbors')
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    try:
        with open(args.neighbors_config) as file:
            doc = yaml.load(file, Loader=yaml.FullLoader)
    except OSError :
            with open(args.neighbors_config) as file: raise
    
    #"tp-1-small"
    sp = simparams_d.Fiducial_statshear(
            name = doc['name'],
            snc_type = 5, 
            shear = 0.1, 
            noise_level = 1.0, 
            min_tru_sb = 1.0,
        )
    drawconf = {
            "n":1,
            "nc":1,
            "nrea":1,
            "ncat":2,
            "ncpu":2,
            "groupmode":"shear",
            "skipdone":False    
        }
    
    simdir = "/data/git_repositories/momentsml/out/fiducial/sim"
    workdir = os.path.join(simdir, sp.name)
    if not os.path.exists(workdir):
        os.makedirs(workdir)
        
    stampsize = 64 #64
    print( args.neighbors_config)
    ncat = drawconf["ncat"]
    nrea = drawconf["nrea"]
    ncpu=drawconf["ncpu"]
    drawcatkwargs={"n":drawconf["n"], "nc":drawconf["nc"], "stampsize":stampsize}


    
            
    drawimgkwargs={"neighbors":doc}
    #drawimgkwargs={}
    psfcat=None; psfselect="random"
    savetrugalimg=True; savepsfimg=False

    catalogs = [stampgrid_d.drawcat(sp, **drawcatkwargs) for i in range(ncat)]

    starttime = datetime.datetime.now()
    prefix = starttime.strftime("%Y%m%dT%H%M%S_")
    
    for catalog in catalogs:

        # We open a file object:
        catfile = tempfile.NamedTemporaryFile(mode='wb', prefix=prefix, suffix="_cat.pkl", dir=workdir, delete=False)
                
        # Now we can get the unique filename
        catalog.meta["catname"] = os.path.basename(str(catfile.name)).replace("_cat.pkl","")
                
        # The images will be written here:
        catimgdirpath = os.path.join(workdir, catalog.meta["catname"] + "_img")
        
        # We set the ImageInfos of the reas, using this unique catname
        catalog.meta["imgreas"] = [
            tools.imageinfo.ImageInfo(
                os.path.join(catimgdirpath, "%s_%i_galimg.fits" % (catalog.meta["catname"], reaindex)),
                xname="x", yname="y", stampsize = catalog.meta["stampsize"], pixelscale=catalog.meta['pixelscale'])
            for reaindex in range(nrea)]
        
        # And we can write this catalog to disk
        pickle.dump(catalog, catfile) # We directly use this open file object.
        catfile.close()

    wslist = []
    for catalog in catalogs:	
        for reaindex in range(nrea):
            
            # We have to customize the drawimgkwargs, and so we work on a copy
            thisdrawimgkwargs = copy.deepcopy(drawimgkwargs)
            
            # Preparing the filepaths in which we will write the output image(s)
            catname = catalog.meta["catname"]
            catimgdirpath = os.path.join(workdir, catname + "_img")
            
            # We have already stored the simgalimgfilepath in the catalog meta:
            thisdrawimgkwargs["simgalimgfilepath"] = catalog.meta["imgreas"][reaindex].filepath        
            #thisdrawimgkwargs["simgalimgfilepath"] =\
            #        os.path.join(catimgdirpath, "%s_%i_galimg.fits" % (catname, reaindex))
            
            # If the user asked for a trugalimg and a psfimg, we also prepare these filepaths.
            if savetrugalimg:
                thisdrawimgkwargs["simtrugalimgfilepath"] = os.path.join(catimgdirpath, "%s_%i_trugalimg.fits" % (catname, reaindex))
            if savepsfimg:
                thisdrawimgkwargs["simpsfimgfilepath"] = os.path.join(catimgdirpath, "%s_%i_psfimg.fits" % (catname, reaindex))
        
            ws = _WorkerSettings(catalog, reaindex, thisdrawimgkwargs, workdir)
            
            wslist.append(ws)
                        
        # While in this simple loop over catalogs, we also make the dir that will contain the images.
        # Indeed the worker loop iterates over this same dir for every realization.
                
        os.mkdir(os.path.join(workdir, catalog.meta["catname"] + "_img"))
                
                
    assert len(wslist) == ncat * nrea
        
    # The catalogs could be heavy, but note that we do not put unique copies of the catalogs in this list !
    # Still, it would seem better to just have small thinks like "indexes" in the settings.
    # However it seems that accessing shared memory from a multiprocessing.Pool is not trivial.
    # So until we need something better, we leave it like this.
    # Note for the future: instead of thinking about how to share memory to optimize this, the workers could well
    # read their data from disk, and stay embarassingly parallel. 
    
    if ncpu == 0:
        try:
            ncpu = multiprocessing.cpu_count()
        except:
            print("multiprocessing.cpu_count() is not implemented!")
            ncpu = 1
                        
    print("Start drawing %i images using %i CPUs" % (len(wslist), ncpu))

    # Suppress the info-or-lower-level logging from the low-level functions:
    #stampgridlogger = logging.getLogger("momentsml.sim.stampgrid")
    #stampgridlogger.setLevel(logging.WARNING)
        
    if ncpu == 1:
        # The single-processing version (not using multiprocessing to keep it easier to debug):
        print("Not using multiprocessing")
        list(map(_worker, wslist))

    else:
        # multiprocessing map:
        pool = multiprocessing.Pool(processes=ncpu)
        pool.map(_worker, wslist)
        pool.close()
        pool.join()
        
    endtime = datetime.datetime.now()
    nstamps = len(catalogs[0])*nrea

if __name__ == "__main__":
    main()
