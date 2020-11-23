import matplotlib
matplotlib.use("AGG")

import os
import momentsml
import config
import argparse

import simparams
import measfcts
import numpy as np
import yaml 
import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)


def parse_args(): 
    parser = argparse.ArgumentParser(description='Basic code to produce simulations with neighbors')
    parser.add_argument('--neighbors_config', default='configfiles/neighbors_config.yaml',  #default=None,
                        help='yaml config define the properties of neighbors')
    parser.add_argument('--name', default='ngbs-nearest-nn-vp-1', help='Name for the run')
    args = parser.parse_args()
    return args


def configure(doc, name):
    """Configures settings for the different datasets
    """
    '''
    sp = simparams.Fiducial_statshear(
            name = name,
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
    '''
    

    sp = simparams.Fiducial_statshear(
            name = name,
            snc_type = 10000, 
            shear = 0.1, 
            noise_level = 1.0, 
            min_tru_sb = 1.0,
        )
    drawconf = {
            "n":1,
            "nc":1,
            "nrea":1,
            "ncat":5000,
            "ncpu":10,
            "groupmode":"shear",
            "skipdone":False    
        }
    
    

    
    return (sp, drawconf, doc )








def run(configuration):
    """Draws the simulations and measures them
    """
    sp, drawconf, doc = configuration
    
    simdir = config.simdir
    measdir = config.simmeasdir

    # Simulating images
    momentsml.sim.run.multi(
        simdir=simdir,
        simparams=sp,
        drawcatkwargs={"n":drawconf["n"], "nc":drawconf["nc"], "stampsize":config.drawstampsize,  'neighbors_config':doc},
        drawimgkwargs={}, 
        psfcat=None, psfselect="random",
        ncat=drawconf["ncat"], nrea=drawconf["nrea"], ncpu=drawconf["ncpu"],
        savepsfimg=False, savetrugalimg=False
    )

    # Measuring the newly drawn images
    momentsml.meas.run.onsims(
        simdir=simdir,
        simparams=sp,
        measdir=measdir,
        measfct=measfcts.default,
        measfctkwargs={"stampsize":config.stampsize},
        ncpu=drawconf["ncpu"],
        skipdone=drawconf["skipdone"]
    )

    cat = momentsml.meas.avg.onsims(
        measdir=measdir, 
        simparams=sp,
        task="group",
        groupcols=measfcts.default_groupcols, 
        removecols=measfcts.default_removecols
    )

    momentsml.tools.table.keepunique(cat)
    momentsml.tools.io.writepickle(cat, os.path.join(measdir, sp.name, "groupmeascat.pkl"))
    
    
    # Now we perform some additional computations on this catalog.
    cat = momentsml.tools.io.readpickle(os.path.join(measdir, sp.name, "groupmeascat.pkl"))
    
    if drawconf["groupmode"] == "shear":
    
        #cat = momentsml.tools.table.groupreshape(cat, groupcolnames=["tru_s1", "tru_s2"])
        cat = momentsml.tools.table.fastgroupreshape(cat, groupcolnames=["tru_s1", "tru_s2"])    
    
        momentsml.tools.table.keepunique(cat)
    
    if drawconf["groupmode"] in ["shear", "ellipticity"]:
    
        # For each case, we add the fraction of failed measurements
        nrea = cat["adamom_g1"].shape[1]
        logger.info("We have {} realizations".format(nrea))
        cat["adamom_failfrac"] = np.sum(cat["adamom_g1"].mask, axis=1) / float(nrea)        
    
        #print momentsml.tools.table.info(cat)
        momentsml.tools.io.writepickle(cat, os.path.join(measdir, sp.name, "groupmeascat.pkl"))

def main():
    args = parse_args()

    try:
        with open(args.neighbors_config) as file:
            doc = yaml.load(file, Loader=yaml.FullLoader)
    except OSError :
            with open(args.neighbors_config) as file: raise

    status = run(configure(doc, args.name))
    exit(status)

if __name__ == "__main__":
    main()
    

