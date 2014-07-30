# Copyright (C) 2013-2014 Pivotal Software, Inc. 
# 
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the under the Apache License, 
# Version 2.0 (the "License”); you may not use this file except in compliance 
# with the License. You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

DOMAIN = "dcapwell"
NAME = "dcloud"
VERSION = "0.2"

INSTALL_FILE = "installedFiles.txt"

# Installs dcloud on the host environment
install: $(INSTALL_FILE)
	@python setup.py install --record $(INSTALL_FILE)

# uninstall dcloud on the host environment
uninstall:
	@cat $(INSTALL_FILE) | xargs rm -rf

# builds and runs the docker file.
# this will spinoff a new docker container running dcloud
# useful for mac users and anyone who doesnt want to
# install on the host environment
docker: docker-build docker-run

# builds the docker image for dcloud
docker-build:
	@echo "Building docker image: $(DOMAIN)/$(NAME):$(VERSION)"
	@docker build -t "$(DOMAIN)/dns_base:$(VERSION)" $(DOMAIN)/dns_base
	@docker build -t "$(DOMAIN)/ssh_base:$(VERSION)" $(DOMAIN)/ssh_base
	@docker build -t "$(DOMAIN)/$(NAME):$(VERSION)" .

# push a existing dcloud image to the docker registry
docker-push:
	@docker push "$(DOMAIN)/dns_base"
	@docker push "$(DOMAIN)/ssh_base"
	@docker push "$(DOMAIN)/$(NAME)"

# run dcloud in a docker container.
# assumes that docker-build has already run for the given
# domain/name/version
docker-run:
	@docker run -t -i --privileged "$(DOMAIN)/$(NAME):$(VERSION)"
