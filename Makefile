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

tmp:
	@mkdir tmp

dev_environment: python_install install_requirements

install: dev_environment

update_requirements_file: dev_environment
	@python_install/bin/pipreqs --use-local --savepath requirements.txt $(PWD)

clean_dev:
	@rm -rf python_install

clean_logs:
	@rm -rf logs/*log

clean_tmp:
	@rm -rf tmp

clean: clean_logs clean_tmp
