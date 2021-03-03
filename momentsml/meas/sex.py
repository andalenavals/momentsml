import glob
import logging
import sys
import os
import shlex

def run_with_timeout(cmd, timeout_sec):
    # cf. https://stackoverflow.com/questions/1191374/using-module-subprocess-with-timeout
    import subprocess, shlex
    from threading import Timer

    proc = subprocess.Popen(shlex.split(cmd))
    kill_proc = lambda p: p.kill()
    timer = Timer(timeout_sec, kill_proc, [proc])
    try:
        timer.start()
        proc.communicate()
    finally:
        timer.cancel()
def add_stream_handler(logger, level):
    formatter = logging.Formatter('%(message)s')
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(level)
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    logger.setLevel(level)  # Not sure if both this and sh.setLevel are required...

def run_STAR_CLASSIFICATION(cat_file, img_file, sat, fwhm, noweight, sex_dir, sex_config, sex_params, sex_filter, sex_nnw, logger):
    """Run sextractor, but only if the output file does not exist yet.
    """

    logger.info('   running sextractor')
    cat_cmd = "{sex_dir}/sex {img_file}[0] -c {config} -CATALOG_NAME {cat_file} -CATALOG_TYPE FITS_LDAC -PARAMETERS_NAME {params} -FILTER_NAME {filter}  -STARNNW_NAME {nnw} -DETECT_MINAREA 3".format(
            sex_dir=sex_dir, img_file=img_file, config=sex_config,
            cat_file=cat_file, params=sex_params, filter=sex_filter,
            nnw=sex_nnw, fwhm=fwhm, sat=sat)
    if not noweight:
        cat_cmd += " -WEIGHT_TYPE MAP_WEIGHT -WEIGHT_IMAGE {img_file}[2]".format(img_file=img_file)
    if fwhm != 0:
        cat_cmd += " -SEEING_FWHM {fwhm}".format(fwhm=fwhm)
    if sat != -1:
        cat_cmd += " -SATUR_LEVEL {sat}".format(sat=sat)
    logger.info(cat_cmd)
    run_with_timeout(cat_cmd, 120)

    if not os.path.exists(cat_file) or os.path.getsize(cat_file) == 0:
        logger.info('   Error running SExtractor.  No ouput file was written.')
        logger.info('   Try again, in case it was a fluke.')
        run_with_timeout(cat_cmd, 120)
        if os.path.getsize(cat_file) == 0:
            os.remove(cat_file)
            logger.info('   Error running SExtractor (again).')
            return None
    return cat_file

def run_SEGMAP( img_file, cat_file, check_file, sex_bin, sex_config, sex_params, sex_filter, logger):
    """Run sextractor, but only if the output file does not exist yet.
    """
    logger.info('running sextractor')
    
    cat_cmd = "{sex_bin} {img_file} -c {config} -CATALOG_NAME {cat_file} -CATALOG_TYPE FITS_LDAC -PARAMETERS_NAME {params} -FILTER_NAME {filter} -CHECKIMAGE_NAME {check_file} ".format(
        sex_bin=sex_bin, img_file=img_file, config=sex_config,
        cat_file=cat_file, params=sex_params, filter=sex_filter,
        check_file=check_file)
    


    logger.info(cat_cmd)
    run_with_timeout(cat_cmd, 120)

    if not os.path.exists(cat_file) or os.path.getsize(cat_file) == 0:
        logger.info('   Error running SExtractor.  No ouput file was written.')
        logger.info('   Try again, in case it was a fluke.')
        run_with_timeout(cat_cmd, 120)
        if os.path.getsize(cat_file) == 0:
            os.remove(cat_file)
            logger.info('   Error running SExtractor (again).')
            return None


def run_SEXTRACTORPP(img_file, cat_file, sex_filter, sex_bin, sex_config, sex_params, python_config, psf_file,  check_flags, logger):
    """Run sextractor, but only if the output file does not exist yet.??
    """
    logger.info('Running SourceSextractorPlusPlus')

    if python_config is not None:
        python_config = "--python-config-file %s"%(python_config)
        #python_arg = "--python-arg=%s"%("image_file=%s"%(img_file))
        python_arg = "--python-arg=%s"%("image_file=%s psf_file=%s"%(img_file,psf_file))
        #if psf_file is not None:
        #    psf_flag="--python-arg=%s"%("psf_file=%s"%(psf_file))
        #    python_arg= "%s %s"%(python_arg, psf_flag )
    else:
        python_arg = ""
        
    
    cat_cmd = "{sex_bin} --detection-image {img_file} --config-file {config} --output-catalog-filename {cat_file} {sex_params} --segmentation-filter {filter} {python_config} {python_arg} {check_flags}".format( sex_bin=sex_bin, img_file=img_file, config=sex_config,  cat_file=cat_file,  filter=sex_filter, check_flags=check_flags,  sex_params=sex_params,  python_config=python_config,  python_arg=python_arg)

    logger.info(cat_cmd)
    run_with_timeout(cat_cmd, 120)

    if not os.path.exists(cat_file) or os.path.getsize(cat_file) == 0:
        logger.info('   Error running SExtractor++.  No ouput file was written.')
        logger.info('   Try again, in case it was a fluke.')
        run_with_timeout(cat_cmd, 120)
        if os.path.getsize(cat_file) == 0:
            os.remove(cat_file)
            logger.info('   Error running SExtractor++ (again).')
            return None

def read_sexparam(sexparam_path):
    out = []
    try:
        f = open(sexparam_path, 'r')
        lines = f.readlines()
    except OSError :
            with open(sexparam_path) as file: raise
            
    for line in lines:
        lex = shlex.shlex(line)
        lex.whitespace = '\n' # if you want to strip newlines, use '\n'
        line = ''.join(list(lex))
        if not line:
            continue
        out.append(line)
    
    return ",".join(out)

def get_checkflags(img_path):
    cflags = ["check-image-model-fitting", "check-image-residual", "check-image-background",
                  "check-image-variance", "check-image-segmentation", "check-image-partition",
                  "check-image-grouping", "check-image-filtered", "check-image-thresholded", 
                  "check-image-auto-aperture", "check-image-aperture", "check-image-psf"]
    check_dir = os.path.expanduser(os.path.join(img_path,"check"))
    try:
        if not os.path.exists(check_dir):
            os.makedirs(check_dir)
    except OSError:
        if not os.path.exists(check_dir): raise
    check_flags_list = ["--%s %s"%(name, os.path.join(check_dir, "%s.fits"%(name) )) for name in cflags]
    check_flags = " ".join(check_flags_list)
    return check_flags
