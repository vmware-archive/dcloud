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

DOMAIN = "pivotal"
NAME = "dcloud"
VERSION = "0.1"

INSTALL_FILE = "installedFiles.txt"

install: $(INSTALL_FILE)
	@python setup.py install --record $(INSTALL_FILE)

uninstall:
	@cat $(INSTALL_FILE) | xargs rm -rf

docker: docker-build

docker-build:
	@echo "Building docker image: $(DOMAIN)/$(NAME):$(VERSION)"
	@docker build -t "$(DOMAIN)/$(NAME):$(VERSION)" .
