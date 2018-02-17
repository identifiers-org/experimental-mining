# Makefile based helper for experimental data mining and reporting on identifiers.org data

#														#
# Author: Manuel Bernal Llinares <mbdebian@gmail.com>	#
#														#

all:
	@echo "<===|DEVOPS|===> [ALL] There is no default target for this helper"

install_requirements:
	@echo "<===|DEVOPS|===> [INSTALL] Installing Application Requirements"
	@python_install/bin/pip install pipreqs nose
	@python_install/bin/pip install -r requirements.txt

python_install:
	@echo "<===|DEVOPS|===> [INSTALL] Python Virtual Environment"
	@pip install --user virtualenv
	@virtualenv python_install

tmp:
	@echo "<===|DEVOPS|===> [MKDIR] Temporary folder"
	@mkdir tmp

dev_environment: python_install install_requirements
	@echo "<===|DEVOPS|===> [INSTALL] Development Environment"

install: dev_environment
	@echo "<===|DEVOPS|===> [INSTALL] Initializing Application Installation"

update_requirements_file: dev_environment
	@echo "<===|DEVOPS|===> [UPDATE] Application Requirements"
	#@python_install/bin/pipreqs --use-local --savepath requirements.txt $(PWD)
	@python_install/bin/pip freeze > requirements.txt

clean_dev:
	@echo "<===|DEVOPS|===> [CLEAN] Removing Python Virtual Environment"
	@rm -rf python_install

clean_logs:
	@echo "<===|DEVOPS|===> [CLEAN] Removing logs"
	@rm -rf logs/*log

clean_tmp:
	@echo "<===|DEVOPS|===> [CLEAN] "
	@rm -rf tmp

clean: clean_logs clean_tmp

clean_all: clean clean_dev

.PHONY: install dev_environment install_requirements update_requirements_file clean_logs clean_dev clean_all clean_tmp clean
