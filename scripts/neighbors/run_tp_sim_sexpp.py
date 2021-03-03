import matplotlib
matplotlib.use("AGG")

import os
import glob
import momentsml
import config
import argparse
import fitsio

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
    parser.add_argument('--skipdone', default=False,
                        action='store_const', const=True, help='Skip finished measures both sextractor and hsm. If false overwrite measures')
    parser.add_argument('--savepsfimg', default=False,
                        action='store_const', const=True, help='Use partion map as weigths')
    parser.add_argument('--savetrugalimg', default=False,
                        action='store_const', const=True, help='Use partion map as weigths')
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
    parser.add_argument('--python_config', default=None,
                        help='location of the python config')
    parser.add_argument('--check', default=False,
                        action='store_const', const=True, help='Create check dir and save check images')
    parser.add_argument('--psf_img', default=False,
                        action='store_const', const=True, help='Pass psf image, to the FlexiModelFiting')
    parser.add_argument('--ext', default='_galimg.fits',
                        help='filename extesion of the detect image')
    parser.add_argument('--psfext', default='_psfcoreimg.fits',
                        help='filename extension of psf img ')
    args = parser.parse_args()
    return args


def configure(doc, name):
    sp = simparams.Fiducial_statshear(
            name = name,
            snc_type = 0,
            shear = 0.0,
            noise_level = 1.0,
            min_tru_sb = 1.0,
        )
    drawconf = {
            "n":1,
            "nc":1,
            "nrea":1,
            "ncat":1,
            "ncpu":1,
            "groupmode":"shear",
            "skipdone":True    
        }
    

        

    

    
    return (sp, drawconf, doc )


def run(configuration, simdir, measdir, ncpu=1, drawsim=True, measure=True,  sextractor_config=None, skipdone=False, savepsfimg=False, savetrugalimg=False):
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
            savepsfimg=savepsfimg, savetrugalimg=savetrugalimg, savepsfcoreimg=savepsfimg
        )

    ## Deblending and weights
    ## external code run sextractor++ (new sextractor)
    if sextractor_config is not None:
        logger.info("Running sextractor")
        momentsml.meas.run.sextractorpp(
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
            measfctkwargs={"stampsize":config.stampsize},
            ncpu=ncpu,
            skipdone=skipdone
        )

        

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
    simmeasdir =os.path.join(measdir, args.name)

    sextractor_config={"sex_bin":args.sex_bin,
                       "sex_config":args.sex_config,
                       "sex_params":args.sex_params,
                       "sex_filter":args.sex_filter,
                       "python_config":args.python_config,
                       "use_check":args.check,
                       "use_psfimg":args.psf_img}

    
    if args.runsex==False: sextractor_config=None
    
    
    status = run(configure(doc, args.name), simdir, measdir,
                 ncpu=args.ncpu, drawsim=args.drawsim,
                 measure=args.measure,
                 sextractor_config=sextractor_config,
                 skipdone=args.skipdone,
                 savetrugalimg=args.savetrugalimg,
                 savepsfimg=args.savepsfimg)
    #exit(status)
    

    #Repeat sim without neighbors for testing
    
    folder = os.path.join(simdir,args.name)
    catalogs= glob.glob(os.path.join(folder,'*_cat.pkl') )
    print(catalogs)

    for cat in catalogs:
        dirname = cat.replace("_cat.pkl", "_img")
        galfilename = "%s_wngalimg.fits"%(os.path.basename(dirname).replace("_img","_0"))
        galname = os.path.join(dirname, galfilename)
        trugalfilename = "%s_wntrugalimg.fits"%(os.path.basename(dirname).replace("_img","_0"))
        trugalname = os.path.join(dirname, trugalfilename)

        if args.drawsim:
            if not os.path.isfile(galname):
                momentsml.sim.stampgrid.drawimg(momentsml.tools.io.readpickle(cat),
                                                galname, trugalname)
                
        if args.measure:
            file_name=os.path.join(measdir,args.name,"%s_meascat.pkl"%(galfilename.replace(".fits","")))
            if not os.path.isfile(file_name):
                cat_out =momentsml.meas.galsim_adamom.measure(galname,
                                                              momentsml.tools.io.readpickle(cat),
                                                              stampsize=config.drawstampsize
                                                              , variant="wider")
                momentsml.tools.io.writepickle(cat_out, file_name)
        


    #run newsextractor on img without neis
    if (args.runsex):
        sextractor_config.update({"use_check":False,"ext":"_wngalimg.fits"})
        momentsml.meas.run.sextractorpp(
            simdir=os.path.join(simdir,args.name), ncpu=args.ncpu,
            skipdone=args.skipdone, **sextractor_config )

if __name__ == "__main__":
    main()
    

