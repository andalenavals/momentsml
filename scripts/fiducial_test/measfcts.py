import momentsml.meas


def default(catalog, stampsize):
	"""
	Default measfct, runs on "img".
	"""	
	
	# HSM adamom
	catalog = momentsml.meas.galsim_adamom.measfct(catalog, stampsize=stampsize, variant="wider")
	catalog = momentsml.meas.adamom_calc.measfct(catalog)
	
	# And skystats
	catalog = momentsml.meas.skystats.measfct(catalog, stampsize=stampsize)
	
	# And snr
	catalog = momentsml.meas.snr.measfct(catalog, gain=1.0e12) # Gain set to give sky-limited SNR
	
	
	return catalog
	
	


default_groupcols = [
'adamom_flag',
'adamom_flux',
'adamom_x',
'adamom_y',
'adamom_g1',
'adamom_g2',
'adamom_sigma',
'adamom_rho4',
'adamom_logflux',
'adamom_g',
'adamom_theta',
'skystd',
'skymad',
'skymean',
'skymed',
'skystampsum',
'skyflag',
'snr'
]

default_removecols = []
