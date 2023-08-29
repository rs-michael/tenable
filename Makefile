
ifeq ($(shell python3 --version 2> /dev/null),)
	PYTHON = python
else
	PYTHON = python3
endif
ifeq ($(shell which pip3 2> /dev/null),)
	PIP = pip
else
	PIP = pip3
endif

ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

.PHONY: install lint test


##############################################
# DEVELOPER COMMANDS
##############################################

install:
	$(PIP) install -r requirements.txt

lint:
	black src/ --line-length 120
	pylint --fail-under=8 src/
