DOMAIN = "pivotal"
NAME = "dcloud"
VERSION = "0.1"

build: 
	@python setup.py install --record installedFiles.txt

uninstall:
	@cat installedFiles.txt | xargs rm -rf

docker: docker-build

docker-build:
	@echo "Building docker image: $(DOMAIN)/$(NAME):$(VERSION)"
	@docker build -t "$(DOMAIN)/$(NAME):$(VERSION)" .
