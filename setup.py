from distutils.core import setup

setup(
    name='ks-build',
    version='1.0',
    py_modules=['kickstartbuild'],
    scripts=['/home/ljb6tw/kickstart-builder/bin/ks-build'],
    data_files=[
    	('/etc/ks-build', ['/home/ljb6tw/kickstart-builder/conf/ks-build.conf']),	
    	('/etc/ks-build/templates', [
			'/home/ljb6tw/kickstart-builder/conf/templates/csgbase.tmpl',
			'/home/ljb6tw/kickstart-builder/conf/templates/oldbase.tmpl',
    		]),
    	]
    )
