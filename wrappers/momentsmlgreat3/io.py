"""
I/O functions directly related to the GREAT3 files
"""

import logging
import numpy as np
import os

import astropy.table

logger = logging.getLogger(__name__)



def readgalcat(branch, subfield, xt=None, yt=None):
	"""
	I read the galaxy catalog for a given branch and subfield.
	:returns: An astropy.table 
	"""
	
	filepath = branch.galcatfilepath(subfield, xt, yt)
	
	# There is probably a direct astropy way to read the data
	#cat = astropy.table.Table.read(filepath, format="ascii")
	#cat.rename_column('col1', 'ID')
	
	# But instead, let's try with numpy to illustrate maximum control:
	data = np.loadtxt(filepath)
	
	if xt is None and yt is None:
		assert data.shape[1] == 3
	else:
		assert data.shape[1] == 5
	
	ids = [int(line[2]) for line in data]
	xs = data[:,0]+1.5 # To get the same pixel convention as MomentsML
	ys = data[:,1]+1.5 # idem
	
	if xt is None and yt is None:
		cat = astropy.table.Table([ids, xs, ys],
				names=('ID', 'x', 'y'),
				meta = {"branch":branch, "subfield":subfield, "filepath":filepath}
				)
	else:
		cat = astropy.table.Table([ids, xs, ys, data[:,3], data[:,4]],
				names=('ID', 'x', 'y', 'tile_x_pos_deg', 'tile_y_pos_deg'),
				meta = {"branch":branch, "subfield":subfield, 
					"filepath":filepath, "xt":xt, 'yt':yt}
				)
		
	logger.info("Read %i sources from %s" % (len(cat), filepath))

	return cat


def readshear(filepath):
	"""
	Reads the "shear_params-000.txt" files and returns (g1, g2)
	"""
	logger.info("Reading shear from %s..." % (filepath))

	data = np.loadtxt(filepath)
	return data
	
