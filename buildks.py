#!/usr/bin/python -tt

from string import Template
from optparse import OptionParser
from urlparse import urljoin
from sys import argv

class BuildKs(object):
	"""
	Class BuildKS: Constructs a kickstart file based on premade template
	"""
	
	def __init__(self):
		"""
		__init__: Builds the parser menu, sets attibutes
		@param: self
		"""

		# Parser options
		parser = OptionParser(
			add_help_option=False,
			usage = "%prog [options] <hostname> <ipaddress> <netmask> <nameserver> <gateway>",
			version = "%prog 1.0",
		)

		# These options are set by default
		parser.set_defaults(
			arch = 'x86_64',
			release = '5',
			bootstrap = 'bootstrap.sh',
		)

		parser.add_option('-h', '--help', action='help')
		parser.add_option('-r', '--release', action='store', type='string', dest='release')
		parser.add_option('-a', '--arch', action='store', type='string', dest='arch')
		parser.add_option('-b', '--bootstrap', action='store', type='string', dest='bootstrap')
	
		# Set options and args
		(self.options, self.args) = parser.parse_args()

		# Attributes
		self.template_file = 'ks_template.tmpl'	
		self.base_url = 'http://rhn.missouri.edu/pub'
		self.repo_name = 'csgrepo'
		self.repo_url = '/'.join([self.base_url,self.repo_name])
		self.args_required = 5

		# Error out if args are less than self.args_required
		if len(self.args) < self.args_required:
			parser.error("Incorrect number of arguments")
	
	def build_url_segments(self):
		"""
		find_installer(): Construct a url segment to match the installation directory on rhn
		ie, rhn.missouri.edu/pub/RHEL5_64
		@param: self
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

	def build_template(self):
		"""
		build_tempate: Constructs template based on the file self.template_file
		@param: self
		"""

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
			install_url = '/'.join([self.base_url, url_segments.get('install_segment')]),
			hostname = self.args[0],
			ip = self.args[1],
			netmask = self.args[2],
			dns = self.args[3],
			gateway = self.args[4],
			bootstrap = self.options.bootstrap,
			repo_url = '/'.join([self.repo_url, url_segments.get('repo_segment')]),	
		)
			
		try:
			# The kickstart filename is <hostname>.ks
			filename = '.'.join([self.args[0], 'ks'])
			f = open(filename, 'w')
			try:
				f.write(output)
			finally:
				f.close()
		except IOError, e:
			print "Problem reading file: %s" % e

def main():
	b = BuildKs()
	b.build_template()

if __name__ == '__main__':
	main()
