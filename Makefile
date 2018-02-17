# Makefile based helper for experimental data mining and reporting on identifiers.org data

#														#
# Author: Manuel Bernal Llinares <mbdebian@gmail.com>	#
#														#

install_requirements:
	@python_install/bin/pip install pipreqs nose
	@python_install/bin/pip install -r requirements.txt

python_install:
	@pip install --user virtualenv
	@virtualenv python_install
