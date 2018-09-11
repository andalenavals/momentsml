"""
Top-level classes and functions to help running MomentsML on GREAT3.
"""

import logging
logger = logging.getLogger(__name__)

from astropy.table import Table
import os

import utils
from momentsml import tools



class GREAT3Run(utils.Branch):
	"""
	This is a simple class to group frequently used variables, on top of the Branch class.
	Unlike Branch, it does specify paths to MomentsML-internal temporary files and directories, and handles a workdir.
	"""
	
	def __init__(self, experiment, obstype, sheartype, datadir, truthdir, workdir, g3publicdir, subfields=None, ncpu=None, skipdone=False):
		
		utils.Branch.__init__(self, experiment, obstype, sheartype, datadir, truthdir)
		logger.info("Getting ready to work on branch %s-%s-%s" % (experiment, obstype, sheartype))

		self.workdir=workdir
		if self.workdir == None:
			logger.warning("Better specify a workdir, I think.")
			self.workdir = "./%s" % (self.get_branchacronym())
		self.mkdirs()
		
		self.g3publicdir = g3publicdir
		
		self.subfields=subfields
		if self.subfields is None:
			self.subfields=range(200)
			
		self.ncpu = ncpu
		if ncpu is None:
			self.ncpu = 1
			
		self.skipdone = skipdone

		# Those, and further variables, can be wildly added later:
		self.simparams_name = None
		self.trainparams_name = None
		

	
	def __str__(self):
		"""
		A tiny self-description, for logging
		"""
		return "GREAT3Run on branch %s in workdir '%s'" % (self.get_branchacronym(), self.workdir)

		
	def mkdirs(self, subfield=None):
		"""
		Creates the working directories. 
		"""

		if not os.path.isdir(self.workdir):
			os.makedirs(self.workdir)
	
		if subfield is not None:
			dirpath = self.subpath(subfield)
			if not os.path.isdir(dirpath):
				os.makedirs(dirpath)
				
			# Now must create the sub-directories:
			for subfolder in ["obs","sim","ml","pred","out","val"]:
				dirpath = self.subpath(subfield, subfolder)
				if not os.path.isdir(dirpath):
					os.makedirs(dirpath)


	def path(self,*args):
		"""
		A helper function that returns a filepath within the working directory.
		
		:param args: strings, must be in order of the filepath, similar to os.path.join()
		
		Example usage::
		
			>>> self.path("obs","catalogue_000.fits")
			
		will return the filepath: self.workdir/obs/catalogue_000.fits
		"""
		return os.path.join(self.workdir,"/".join(args))
	
	
	def subpath(self, subfield, *args):
		"""
		Similar, but first argument is a subfield number
		"""
		
		
		
		return os.path.join(self.workdir, "%03i" % subfield, "/".join(args))
	

