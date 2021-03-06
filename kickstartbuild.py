from string import Template
from optparse import OptionParser, OptionValueError
from urlparse import urljoin
from subprocess import PIPE, Popen
from sys import argv, stdout
import ConfigParser
import os

class KickstartBuild(object):
	"""
	Class BuildKS: Constructs a kickstart file based on premade template

	"""
	
	def __init__(self):
		"""
		Builds the parser menu, sets attibutes

		"""

		config = ConfigParser.RawConfigParser()
		config.read('/etc/buildks/buildks.conf')

		# Config options
		self.template_file = config.get('global', 'template')
		self.base_url = config.get('global', 'base_url')
		self.repo_name = config.get('global', 'repo')
		self.output_dir = config.get('global', 'output_dir')
		self.bootstrap_path = config.get('global', 'bootstrap_path')

		self.repo_url = '/'.join([self.base_url,self.repo_name])
		self.valid_releases = ['4', '5', '6']
		self.valid_archs = ['x86_64', 'i386']

		# args_required should be set to minimum required arguments
		self.args_required = 4

		# Parser options
		self.parser = OptionParser(
			add_help_option=True,
			usage = "%prog [options] <fqdn> <ipaddress> <netmask> <gateway>",
			version = "%prog 1.1",
		)

		self.parser.set_defaults(
			arch = config.get('parser', 'default_arch'),
			release = config.get('parser', 'default_release'),
			bootstrap = config.get('parser', 'default_bootstrap'),
			dns = config.get('parser', 'default_dns'),
			skip_validate = config.get('parser', 'default_validation')
		)

		self.parser.add_option('-a', '--arch', action='store', type='string',
						 help='x86_64 or i386', dest='arch')

		self.parser.add_option('-b', '--bootstrap', action='store', type='string', dest='bootstrap',
						 help='Your bootstrap script (i.e., bakerlu_bootstrap.sh)')

		self.parser.add_option('-d', '--dns', action='store', type='string', dest='dns',
						 help='DNS server')

		self.parser.add_option('-r', '--release', action='store',type='string', dest='release',
						 help='Distribution Release, (i.e., 5 or 6)')

		self.parser.add_option('-s', '--skip-validate', action='store_true', dest='skip_validate',
						 help='Skip validation checks: (IP / hostname resolution)')

		# Set options and args
		(self.options, self.args) = self.parser.parse_args()
	
	def check_args(self):
		"""
		Validate argument length, arch and release options.
		Length validation compares number of args vs self.args_required (set in constructor)
		Arch validation compares the arch option vs self.valid_archs (list, set in constructor)
		Release validation compares release option vs self.valid_releases (list, set in constructor)

		"""

		if len(self.args) < self.args_required:
			self.parser.error('Incorrect number of arguments')

		if self.options.arch not in self.valid_archs:
			raise OptionValueError('Not a valid arch')

		if self.options.release not in self.valid_releases:
			raise OptionValueError('Not a valid release')

	def validate(self):
		"""
		Validate digs the fqdn and IP address. If either of these do not resolve properly, raise an error
		If the bootstrap option is specified, validate checks to make sure that the script exists

		"""

		# Slice off the last character from the result [:-2]
		checked_hostname = Popen("dig +short -x %s" % self.args[1], stdout=PIPE, shell=True).communicate()[0][:-2]
		checked_ip = Popen("dig +short %s" % self.args[0], stdout=PIPE, shell=True).communicate()[0].strip()	

		if checked_hostname != self.args[0] or checked_ip != self.args[1]:
			raise OptionValueError('Your FQDN and IP do not resolve properly')

		bootstrap = os.path.join(self.bootstrap_path, self.options.bootstrap)

		if os.path.exists(bootstrap) is not True:
			raise OptionValueError('The specified bootstrap script does not exist')

	def build_url_segments(self):
		"""
		Construct a url segment to match the installation directory on rhn
		ie, rhn.missouri.edu/pub/RHEL5_64

		"""
		
		# Build the installation directory
		install_dir = []
		install_dir.append('RHEL'+self.options.release)

		if self.options.arch == 'x86_64':
			install_dir.append('64')
		else:
			install_dir.append('i386')
	
		# Create the install URL segment
		install_segment = '_'.join(install_dir)

		# Build the repo URL segment
		if self.options.arch != 4:
			repo_segment = '/'.join([self.options.release+'Server', self.options.arch])
		else:
			repo_segment = '/'.join([self.options.release, self.options.arch])

		results = {
			'install_segment': install_segment,
			'repo_segment': repo_segment,
		}

		return results

	def build(self):
		"""
		Constructs template based on the file self.template_file

		"""

		if self.options.skip_validate is True:
			pass
		else:
			self.validate()

		try:
			f = open(self.template_file, 'r')
			try:
				lines = f.read()
			finally:
				f.close()
		except IOError, e:
			print "Problem reading file: %s" % e

		# Create template from the file
		tmpl = Template(lines)

		# Call install_dir() to build our url segment
		url_segments = self.build_url_segments()

		# Substitute template variables with arguments
		output = tmpl.safe_substitute(
			# i.e., rhn.missouri.edu/pub/RHEL5_x86
			install_url = '/'.join([self.base_url, url_segments.get('install_segment')]),
			hostname = self.args[0],
			ip = self.args[1],
			netmask = self.args[2],
			gateway = self.args[3],
			dns = self.options.dns,
			bootstrap = self.options.bootstrap,
			# i.e., rhn.missouri.edu/pub/csgrepo/5Server/x86_64
			repo_url = '/'.join([self.repo_url, url_segments.get('repo_segment')]),	
		)

		dir = os.path.dirname(self.output_dir)

		# The kickstart filename is <hostname>.ks
		filename = '.'.join([self.args[0], 'ks'])
		file = os.path.join(dir, filename)

		if os.path.exists(dir):			
			try:
				f = open(file, 'w')
				try:
					f.write(output)
				finally:
					f.close()
					print('File %s has been created') % file
			except IOError, e:
				print "Problem reading file: %s" % e
		else:
			raise DirectoryError('Directory does not exist')
