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
logger = logging.getLogger(__name__)


def parse_args(): 
    parser = argparse.ArgumentParser(description='Basic code to produce simulations with neighbors')
    parser.add_argument('--neighbors_config', default='configfiles/neighbors_config.yaml',  #default=None,
                        help='yaml config define the properties of neighbors')
    parser.add_argument('--name', default='ngbs-nearest-nn-tp-1', help='Name for the run')
    parser.add_argument('--verbose', default=None, help='verbose level { 50:CRITICAL, 40:ERROR, 30:WARNING, 20:INFO, 10:DEBUGG ')
    parser.add_argument('--drawsim', default=False,
                        action='store_const', const=True, help='Draw simulations')
    parser.add_argument('--measure', default=False,
                        action='store_const', const=True, help='Measure simulations')
    parser.add_argument('--runsex', default=False,
                        action='store_const', const=True, help='Run sextractor')
    parser.add_argument('--weight', default=False,
                        action='store_const', const=True, help='Use partion map as weigths')
    parser.add_argument('--skipdone', default=False,
                        action='store_const', const=True, help='Skip finished measures both sextractor and hsm. If false overwrite measures')
    parser.add_argument('--ncpu', default=1, type=int, 
                        help='Number of cpus')
    parser.add_argument('--workdir', default='~/test', 
                        help='diractory of work')
    parser.add_argument('--sex_bin', default='/usr/bin/sex',
                        help='location of sextrator executable')
    parser.add_argument('--sex_config',
                        default='y3.sex',
                        help='sextractor config file')
    parser.add_argument('--sex_params',
                        default='sex.param_piff',
                        help='sextractor param file')
    parser.add_argument('--sex_filter',
                        default='sex.conv',
                        help='name of sextractor filter file')
    args = parser.parse_args()
    return args


def configure(doc, name):
    """Configures settings for the different datasets
    """
    '''
    sp = simparams.Fiducial_statshear(
            name = name,
            snc_type = 2000,
            shear = 0.1,
            noise_level = 1.0,
            min_tru_sb = 1.0,
        )
    drawconf = {
            "n":1,
            "nc":1,
            "nrea":1,
            "ncat":4000,
            "ncpu":10,
            "groupmode":"shear",
            "skipdone":False    
        }
    '''
    
    
    sp = simparams.Fiducial_statshear(
            name = name,
            snc_type = 1,
            shear = 0.1,
            noise_level = 1.0,
            min_tru_sb = 1.0,
        )
    drawconf = {
            "n":1,
            "nc":1,
            "nrea":1,
            "ncat":6,
            "ncpu":1,
            "groupmode":"shear",
            "skipdone":True    
        }
    

        

    

    
    return (sp, drawconf, doc )


def run(configuration, simdir, measdir, ncpu=1, drawsim=True, measure=True, weight=False, sextractor_config=None, skipdone=False):
    """Draws the simulations and measures them
    """
    sp, drawconf, doc = configuration
    
    # Simulating images
    if (drawsim):
        logger.info("Drawing simulations")
        momentsml.sim.run.multi(
            simdir=simdir,
            simparams=sp,
            drawcatkwargs={"n":drawconf["n"], "nc":drawconf["nc"], "stampsize":config.drawstampsize,  'neighbors_config':doc},
            drawimgkwargs={}, 
            psfcat=None, psfselect="random",
            ncat=drawconf["ncat"], nrea=drawconf["nrea"], ncpu=ncpu,
            savepsfimg=False, savetrugalimg=False
        )

    ## Deblending and weights
    ## external code run sextractor++ (new sextractor)
    if sextractor_config is not None:
        logger.info("Running sextractor")
        momentsml.meas.run.sextractor(
            simdir=os.path.join(simdir,sp.name),
            ncpu=ncpu,
            skipdone=skipdone,
            **sextractor_config )
    
    # Measuring the newly drawn images
    if (measure):
        logger.info("Measuring draw simulations")
        momentsml.meas.run.onsims(
            simdir=simdir,
            simparams=sp,
            measdir=measdir,
            measfct=measfcts.default,
            measfctkwargs={"stampsize":config.stampsize, "weight":weight},
            ncpu=ncpu,
            skipdone=skipdone
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
    if args.verbose is not None:
        level = int(args.verbose)
    else:
        level = logging.DEBUG
    logging.basicConfig(format=config.loggerformat, level=level)

    try:
        with open(args.neighbors_config) as file:
            doc = yaml.load(file, Loader=yaml.FullLoader)
    except OSError :
            with open(args.neighbors_config) as file: raise

    outpath = os.path.expanduser(args.workdir)
    try:
        if not os.path.exists(outpath):
            os.makedirs(outpath)
    except OSError:
        if not os.path.exists(outpath): raise
        
    simdir=os.path.join(outpath, "sim")
    measdir = os.path.join(outpath, "simmeas")

    sextractor_config={"sex_bin":args.sex_bin,
                       "sex_config":args.sex_config,
                       "sex_params":args.sex_params,
                       "sex_filter":args.sex_filter}

    if args.runsex==False: sextractor_config=None
    
    status = run(configure(doc, args.name), simdir, measdir, ncpu=args.ncpu, drawsim=args.drawsim, measure=args.measure, weight=args.weight,sextractor_config=sextractor_config, skipdone=args.skipdone)
    exit(status)

if __name__ == "__main__":
    main()
    

