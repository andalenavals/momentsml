import galsim
import numpy as np
import random
import logging
logger = logging.getLogger(__name__)

def trunc_rayleigh(sigma, max_val):
        """
        A truncated Rayleigh distribution
        """
        assert max_val > sigma
        tmp = max_val + 1.0
        while tmp > max_val:
                tmp = np.random.rayleigh(sigma)
        return tmp

def draw_all_neighbors(neighbors_config,  stampsize,  nei_limits = None):
        #stampsize is required only for positions
        nn = neighbors_config["nn"]
        nn_min = neighbors_config["nn_min"]
        nn_max = neighbors_config["nn_max"]
        if nn is None:
                nn = random.choice(range(nn_min, nn_max + 1))
        logger.info("Drawing %i neighbors"%(nn))
        #logger.info("Drawing %i neighbors in galaxy %i"%(nn,  i))
        #Define list with one dictionary by neighbor properties
        neighs = [ draw_neighbor_dict(neighbors_config, nei_limits=nei_limits) for n in range(nn) ]
        neighs_pos = [ placer_dict(stampsize, neighbors_config) for n in range(nn) ]
        for d1, d2 in zip(neighs, neighs_pos): d1.update(d2)
        return neighs

#This is call for each realization in case features are not defined they
# will vary among realizations
def draw_neighbor(doc=None, psf=None):
        gsparams=None
        if gsparams is None:
                gsparams = galsim.GSParams(maximum_fft_size=10240)

        #begin of possible kwargsneigh
        
        profile_type = doc['profile_type']
        tru_g1 =  doc['tru_g1']
        tru_g2 =  doc['tru_g2']
                
        if (profile_type == "Sersic"):
            sersiccut=doc['Sersic']['sersiccut']
            tru_rad =doc['Sersic']['tru_rad']
            tru_sersicn =  doc['Sersic']['tru_sersicn']
            tru_sb =  doc['Sersic']['tru_sb']
            tru_flux = np.pi * tru_rad * tru_rad * tru_sb 
                
            if sersiccut is None:
                trunc = 0
            else:
                trunc = tru_rad* sersiccut

            gal = galsim.Sersic(n=tru_sersicn, half_light_radius=tru_rad, flux=tru_flux, gsparams=gsparams, trunc=trunc)
            # We make this profile elliptical
            gal = gal.shear(g1=tru_g1, g2=tru_g2) # This adds the ellipticity to the galaxy

        elif profile_type == "Gaussian":
            tru_flux =  doc['Gaussian']['tru_flux']
            tru_sigma =  doc['Gaussian']['tru_sigma']
                                
            gal = galsim.Gaussian(flux=tru_flux, sigma=tru_sigma, gsparams=gsparams)
            # We make this profile elliptical
            gal = gal.shear(g1=tru_g1, g2=tru_g2) # This adds the ellipticity to the galaxy        
                                
        elif profile_type == 'EBulgeDisk':
            # A more advanced Bulge + Disk model
            # It needs GalSim version master, as of April 2017 (probably 1.5).
            
            # Get a Sersic bulge:
            tru_bulge_sersicn =  doc['EBulgeDisk']['tru_bulge_sersicn']
            tru_bulge_rad = doc['EBulgeDisk']['tru_bulge_rad']
            tru_bulge_flux = doc['EBulgeDisk']['tru_bulge_flux']
            tru_disk_hlr = doc['EBulgeDisk']['tru_disk_hlr']
            tru_disk_tilt =  doc['EBulgeDisk']['tru_disk_tilt']
            tru_disk_flux =  doc['EBulgeDisk']['tru_disk_flux']
            tru_theta = doc['EBulgeDisk']['tru_theta'] 
   
                                
            bulge = galsim.Sersic(n=tru_bulge_sersicn, half_light_radius=tru_bulge_rad, flux=tru_bulge_flux)
            # Make it elliptical:
            #bulge_ell = galsim.Shear(g=row["tru_bulge_g"], beta=row["tru_theta"] * galsim.degrees)
            #bulge = bulge.shear(bulge_ell)
            bulge = bulge.shear(g1=tru_g1, g2=tru_g2)
                                
            # Get a disk
            scale_radius = tru_disk_hlr / galsim.Exponential._hlr_factor
            disk = galsim.InclinedExponential(inclination=tru_disk_tilt * galsim.degrees, scale_radius=scale_radius,
                                              flux=tru_disk_flux, scale_h_over_r=tru_disk_scale_h_over_r)
            # Rotate it in the same orientation as the bulge:
            disk = disk.rotate(tru_theta * galsim.degrees)
                
            # And we add those profiles, as done in GalSim demo3.py :
            gal = bulge + disk

        elif profile_type == 'Gaussian_PSF': #you meant to draw stars all of them identical
            gal = galsim.Gaussian(flux=doc['Gaussian_PSF']['flux'], sigma=doc['Gaussian_PSF']['flux'])        
            #gal = gal.shear(g1=tru_g1, g2=tru_g2)

        elif profile_type == 'Stamp_PSF':
            raise RuntimeError("Neighbors with Stamp_PSF, but PSF stamp is not defined in catalog")    
            gal = psf
            #gal = gal.shear(g1=tru_g1, g2=tru_g2)
        else:
            raise RuntimeError("Unknown galaxy profile!")        
                 
        return gal

   
#This function is call for each catalog
def draw_neighbor_dict(doc, nei_limits=None):
    ## stampsize is mandatory only for relative placing
    if nei_limits is not None:
            logger.info("Using neighbor limits from central galaxy")
            p_type = list(nei_limits.keys())[0]
            doc[p_type].update(nei_limits[p_type])
    dict_out ={}
    profile_type = doc['profile_type']
    tru_g1 =  doc['tru_g1']
    tru_g2 =  doc['tru_g2']

    #range values SERSIC profile
    min_tru_rad = doc['Sersic']['tru_rad_min']
    max_tru_rad = doc['Sersic']['tru_rad_max']
    min_sersicn = doc['Sersic']['sersicn_min']
    max_sersicn = doc['Sersic']['sersicn_max']
    ndivs = doc['Sersic']['ndivs']
    min_tru_sb = doc['Sersic']['tru_sb_min']
    max_tru_sb = doc['Sersic']['tru_sb_max']

    #range values EBulge profile
    min_tru_bulge_rad = doc['EBulgeDisk']['tru_bulge_rad_min']
    max_tru_bulge_rad = doc['EBulgeDisk']['tru_bulge_rad_max']
    min_tru_bulge_sersicn = doc['EBulgeDisk']['tru_bulge_sersicn_min']
    max_tru_bulge_sersicn = doc['EBulgeDisk']['tru_bulge_sersicn_max']
    ndivs_bulge = doc['EBulgeDisk']['ndivs_bulge']
    min_tru_bulge_flux = doc['EBulgeDisk']['tru_bulge_flux_min']
    max_tru_bulge_flux = doc['EBulgeDisk']['tru_bulge_flux_max']
    min_disk_hlr = doc['EBulgeDisk']['tru_disk_hlr_min']
    max_disk_hlr = doc['EBulgeDisk']['tru_disk_hlr_max']
    min_disk_tilt = doc['EBulgeDisk']['tru_disk_tilt_min']
    max_disk_tilt = doc['EBulgeDisk']['tru_disk_tilt_max']
    min_disk_flux = doc['EBulgeDisk']['tru_disk_flux_min']
    max_disk_flux = doc['EBulgeDisk']['tru_disk_flux_max']
    min_tru_disk_scale_h_over_r = doc['EBulgeDisk']['tru_disk_scale_h_over_r_min']
    max_tru_disk_scale_h_over_r = doc['EBulgeDisk']['tru_disk_scale_h_over_r_max']
    min_tru_theta = doc['EBulgeDisk']['tru_theta_min']
    max_tru_theta = doc['EBulgeDisk']['tru_theta_max']
    
    
    #range values Gaussian profile
    min_tru_flux = doc['Gaussian']['tru_flux_min'] #np.pi*(min_tru_rad**2)*min_tru_sb
    max_tru_flux = doc['Gaussian']['tru_flux_max'] #np.pi*(max_tru_rad**2)*max_tru_sb
    min_tru_sigma = doc['Gaussian']['tru_sigma_min']
    max_tru_sigma = doc['Gaussian']['tru_sigma_max']
    
    
    #range values, any profile 
    min_tru_g = doc['tru_g_min']
    max_tru_g = doc['tru_g_max']
    
    if tru_g1 is None :
        tru_g = trunc_rayleigh(min_tru_g, max_tru_g)
        tru_theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)
        tru_g1 = tru_g * np.cos(2.0 * tru_theta)
        #(tru_g1, tru_g2) = (tru_g * np.cos(2.0 * tru_theta), tru_g * np.sin(2.0 * tru_theta))
    if tru_g2 is None :
        tru_g = trunc_rayleigh(min_tru_g, max_tru_g)
        tru_theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)
        tru_g2 = tru_g * np.sin(2.0 * tru_theta)

    dict_out["tru_g1"] = tru_g1
    dict_out["tru_g2"] = tru_g2
    dict_out["profile_type"] = profile_type

    if (profile_type == "Sersic"):
        sersiccut=doc['Sersic']['sersiccut']
        tru_rad =doc['Sersic']['tru_rad']
        tru_sersicn =  doc['Sersic']['tru_sersicn']
        tru_sb =  doc['Sersic']['tru_sb']
            
        if tru_rad is None:
            tru_rad = np.random.uniform(min_tru_rad, max_tru_rad)#half_light_radius
        if tru_sersicn is None:
            tru_sersicn = random.choice(np.linspace(min_sersicn, max_sersicn, ndivs))#sersic index
        if tru_sb is None:
            tru_sb = np.random.uniform(min_tru_sb, max_tru_sb )#fiducial noise level
        if tru_rad and tru_sb is not None:
            tru_flux = np.pi * tru_rad * tru_rad * tru_sb #flux
        
        if sersiccut is None:
            trunc = 0
        else:
            trunc = tru_rad* sersiccut

        dict_out['Sersic'] = {}
        dict_out['Sersic']['sersiccut'] = sersiccut
        dict_out['Sersic']['tru_rad'] = tru_rad
        dict_out['Sersic']['tru_sersicn'] = tru_sersicn
        dict_out['Sersic']['tru_sb'] = tru_sb

    elif profile_type == "Gaussian":
        tru_flux =  doc['Gaussian']['tru_flux']
        tru_sigma =  doc['Gaussian']['tru_sigma']
        if tru_flux is None:
            tru_flux = np.random.uniform(min_tru_flux, max_tru_flux)
        if tru_sigma is None:
            tru_sigma = np.random.uniform(min_tru_sigma, max_tru_sigma)

        dict_out['Gaussian'] = {}               
        dict_out['Gaussian']['tru_flux'] = flux
        dict_out['Gaussian']['tru_sigma'] = sigma    
            
    elif profile_type == 'EBulgeDisk':
        # A more advanced Bulge + Disk model
        # It needs GalSim version master, as of April 2017 (probably 1.5).
        
        # Get a Sersic bulge:
        tru_bulge_sersicn =  doc['EBulgeDisk']['tru_bulge_sersicn']
        tru_bulge_rad = doc['EBulgeDisk']['tru_bulge_rad']
        tru_bulge_flux = doc['EBulgeDisk']['tru_bulge_flux']
        tru_disk_hlr = doc['EBulgeDisk']['tru_disk_hlr']
        tru_disk_tilt =  doc['EBulgeDisk']['tru_disk_tilt']
        tru_disk_flux =  doc['EBulgeDisk']['tru_disk_flux']
        tru_theta = doc['EBulgeDisk']['tru_theta'] 
        if tru_bulge_rad is None:
            tru_bulge_rad = np.random.uniform(min_tru_bulge_rad, max_tru_bulge_rad)#half_light_radius
        if tru_bulge_sersicn is None:
            tru_bulge_sersicn = random.choice(np.linspace(min_tru_bulge_sersicn, max_tru_bulge_sersicn, ndivs_bulge))
        if tru_bulge_flux is None:
            tru_bulge_flux = np.random.uniform(min_tru_bulge_flux, max_tru_bulge_sflux)
        if tru_disk_hlr is None:
            tru_disk_hlr = np.random.uniform(min_disk_hlr, max_disk_hlr)
        if tru_disk_tilt is None:
            tru_disk_tilt = np.random.uniform(min_disk_tilt, max_disk_tilt)
        if tru_disk_flux is None:
            tru_disk_flux = np.random.uniform(min_disk_flux, max_disk_flux)
        if tru_theta is None:
            tru_theta = np.random.uniform(min_tru_theta, max_tru_theta)
        if tru_disk_scale_h_over_r is None:
            tru_disk_scale_h_over_r = np.random.uniform(min_tru_disk_scale_h_over_r, max_tru_disk_scale_h_over_r)

        dict_out['EBulgeDisk'] = {}
        dict_out['EBulgeDisk']['tru_bulge_sersicn'] = tru_bulge_sersicn
        dict_out['EBulgeDisk']['tru_bulge_rad'] = tru_bulge_rad
        dict_out['EBulgeDisk']['tru_bulge_flux'] = tru_bulge_flux
        dict_out['EBulgeDisk']['tru_disk_hlr'] = tru_disk_hlr
        dict_out['EBulgeDisk']['tru_disk_tilt'] = tru_disk_tilt
        dict_out['EBulgeDisk']['tru_disk_flux'] = tru_disk_flux
        dict_out['EBulgeDisk']['tru_theta']  = tru_theta

    elif profile_type == 'Gaussian_PSF': #you meant to draw stars all of them identical
        flux=doc['Gaussian_PSF']['flux']
        sigma=doc['Gaussian_PSF']['sigma']
        dict_out['Gaussian_PSF'] = {}
        dict_out['Gaussian_PSF']['flux'] = flux
        dict_out['Gaussian_PSF']['sigma'] = sigma
    

    elif profile_type == 'Stamp_PSF':
        raise RuntimeError("Neighbors with Stamp_PSF, but PSF stamp is not defined in catalog")    
         
    else:
        raise RuntimeError("Unknown galaxy profile!")        

    return dict_out

   
def placer_dict(stampsize, doc):
    dict_out = {}
    method = doc['placer_method']
    ##Relative placing
        
    if method == 'random_box':
        xmin_n = ymin_n  = 0
        xmax_n = ymax_n = stampsize
        if doc['random_box']['xmin'] is not None: xmin_n = int(doc['random_box']['xmin']*stampsize)
        if doc['random_box']['xmax'] is not None: xmax_n = int(doc['random_box']['xmax']*stampsize)
        if doc['random_box']['ymin'] is not None: ymin_n = int(doc['random_box']['ymin']*stampsize)
        if doc['random_box']['ymax'] is not None: ymax_n = int(doc['random_box']['ymax']*stampsize) 
        if doc['random_box']['x'] is not None:
            x =  int(doc['random_box']['x']*stampsize)
        else:
            x = np.random.uniform( xmin_n, xmax_n - 1)
        if doc['random_box']['y'] is not None:
            y =  int(doc['random_box']['y'] * stampsize)
        else:
            y = np.random.uniform( ymin_n, ymax_n - 1)
        xrel = x - stampsize*0.5 #approximated no jiter included
        yrel = y - stampsize*0.5
        dict_out["x_rel"] = xrel 
        dict_out["y_rel"] = yrel 
        
    if method ==  'random_ring':
        rmax = stampsize * 0.5
        rmin = 0
        theta_min = 0
        theta_max = 2*np.pi  
        if doc['random_ring']['rmin'] is not None: rmin = doc['random_ring']['rmin']
        if doc['random_ring']['rmax'] is not None: rmax = doc['random_ring']['rmax']
        if doc['random_ring']['theta_min'] is not None:theta_min=doc['random_ring']['theta_min']*np.pi
        if doc['random_ring']['theta_max'] is not None:theta_max=doc['random_ring']['theta_max']*np.pi
        max_rsq = rmax**2
        min_rsq = rmin**2

        if doc['random_ring']['r'] is not None and doc['random_ring']['theta'] is not None:
            r = doc['random_ring']['r']
            theta =  doc['random_ring']['theta']*np.pi
            x = r*np.cos(theta)
            y = r*np.sin(theta)
        elif doc['random_ring']['r'] is not None and doc['random_ring']['theta'] is None:
            r = doc['random_ring']['r']
            theta =  np.random.uniform(theta_min, theta_max)
            x = r*np.cos(theta)
            y = r*np.sin(theta)
        elif doc['random_ring']['r'] is None and doc['random_ring']['theta'] is not None:
            theta = doc['random_ring']['theta']*np.pi
            r =  np.random.uniform(rmin, rmax)
            x = r*np.cos(theta)
            y = r*np.sin(theta)
        else:
            while True:  # (This is essentially a do..while loop.)
                x = np.random.uniform( -rmax, rmax)
                y = np.random.uniform( -rmax, rmax)
                rsq = x**2 + y**2
                theta = np.arctan2(y, x)
                if theta < 0: theta +=2*np.pi
                bo = rsq>=min_rsq and rsq<=max_rsq and theta>=theta_min and theta<=theta_max
                if bo: break
        dict_out["x_rel"] = x #in pixel
        dict_out["y_rel"] = y
        
        return dict_out


def polar_translation(nei, doc):
    theta_min = 0
    theta_max = 2*np.pi 
    if doc['random_ring']['theta_min'] is not None:theta_min=doc['random_ring']['theta_min']*np.pi
    if doc['random_ring']['theta_max'] is not None:theta_max=doc['random_ring']['theta_max']*np.pi
    theta =  np.random.uniform(theta_min, theta_max)
    r = np.sqrt(nei['x_rel']**2 +  nei['y_rel']**2)
    x_new = r*np.cos(theta)
    y_new = r*np.sin(theta)
    nei.update({'x_rel': x_new,  'y_rel': y_new})


def find_nearest(neighs):
        raux = neighs[0]["x_rel"]**2 + neighs[0]["y_rel"]**2
        idx = 0
        for i, n in enumerate(neighs):
                r2 = n["x_rel"]**2 + n["y_rel"]**2
                if r2 < raux:
                        raux = r2
                        idx = i              
        return neighs[idx]
