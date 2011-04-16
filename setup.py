from distutils.core import setup

base_dir = '/home/ljb6tw/kickstart-builder'

setup(
    name = 'buildks',
    version = '1.1',
    py_modules = ['kickstartbuild'],
    scripts = ['%s/script/buildks' % base_dir],
    data_files = [
    	('/etc/buildks', ['%s/conf/buildks.conf' % base_dir]),	
    	('/etc/buildks/templates', [
			'%s/conf/templates/csgbase.tmpl' % base_dir,
			'%s/conf/templates/oldbase.tmpl' % base_dir,
    		]),
    	]
	)
