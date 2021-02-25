import glob
import logging
import sys
import os

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
    return cat_file

