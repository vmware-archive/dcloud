<!--- 
Copyright (C) 2013-2014 Pivotal Software, Inc. 

All rights reserved. This program and the accompanying materials
are made available under the terms of the under the Apache License, 
Version 2.0 (the "License”); you may not use this file except in compliance 
with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->


Overview
====================
dcloud is a tool to orchestrate Docker containers.

![dcloud design diagram](https://raw.githubusercontent.com/gopivotal/dcloud/master/doc/diagram1.jpg)

Prerequites
==========================

Host OS
-----------
Currently Centos65, Redhat65 and Ubuntu13 are supported.

MacOS is NOT suported

python
-----------
python version 2.6.6 is recommended. There seems ways to accomplish this.
Here is some idea...

### Install python on ubuntu

```
add-apt-repository ppa:fkrull/deadsnakes
sudo apt-get update
sudo apt-get install python2.6 python2.6-dev
cd /usr/bin
ln -s python2.6 python
```

Dependencies (Third party libraries)
------------------------

### python dependencies

```
yum -y install gcc python-devel gmp-devel bash-completion
wget --no-check-certificate https://raw.github.com/pypa/pip/master/contrib/get-pip.py
python get-pip.py
# yum -y install python-crypto
pip install pycrypto
pip install paramiko
easy_install --upgrade ecdsa

```
If you are using Debian
```
apt-get install gcc
apt-get install python-dev
```

### Docker
Refer to the Docker Installation document. Currently version 0.11.1 is recommended

https://www.docker.io/gettingstarted/#h_installation

#### Note
This is a handy unofficial note for Docker installation on Centos. Please refer to the Docker official page for detail.

```
sudo yum install http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
sudo yum update -y
sudo yum -y install docker-io
sudo service docker start
```



How to Install dcloud
==========================

```bash
git clone <dcloud source path>
sudo python setup.py install --record installedFiles.txt
```

### How to Uninstall dcloud
```
cat installedFiles.txt  | sudo xargs rm -rf
```

How to use dcloud
=======================
Please note that you run dcloud command as root user at this point. We have a ticket to fix this limitation https://github.com/gopivotal/dcloud/issues/2

How to create a dcloud cluster
-----------------
### Example with image
```
$ cat example/cluster_from_images.json
{
	"id" : "example_cluster1",
	"domain" : "mydomain.com",
	"dns" : ["8.8.8.8", "8.8.4.4"],
	"nodes": [
		{
			"hostname" : "node[1..3]",
			"imageName" : "dcloud/ssh-base",
			"cmd" : "service sshd start && tail -f /var/log/yum.log"
		}
	]
}
$ dcloud create example/cluster_from_images.json
```
### Example with Dockerfile
```
$ cat example/cluster_from_Dockerfile/cluster_from_Dockerfile.json
{
  "id" : "example_cluster2",
  "domain" : "mydomain.com",
  "dns" : ["8.8.8.8", "8.8.4.4"],
  "nodes": [
    {
      "hostname" : "node[1..2]",
      "Dockerfile" : "example/cluster_from_Dockerfile/.",
      "cmd" : "service sshd start && service httpd start && tail -f /var/log/yum.log"
    }
  ]
}
$ cat example/cluster_from_Dockerfile/Dockerfile
FROM centos
RUN echo root:changeme | chpasswd
RUN yum -y install httpd
RUN yum -y install openssh-server openssh-clients

$ dcloud create example/cluster_from_Dockerfile/cluster_from_Dockerfile.json
```

How to list dcloud clusters
------------------------

```
dcloud list
dcloud list example_cluster1
```

How to destroy
------------------------
```
dcloud destroy example_cluster1
```

How to snapshot
------------------------
```
dcloud snapshot example_cluster1 phd
```

How to archive
------------------------
__TODO__ Fix this.

```
dcloud archive example_cluster1
ls -laFh /tmp/dcloud_work/
md5
```

Development
=====================================
unit test
---------------------
```
nosetests test
```

Mac Support
=====================================
Currently dcloud assumes network access to the containers.  This will not work for macs, so a simpler solution is given for mac support: dcloud inside docker.

To get this running, run the following

    docker run -t -i --privileged dcloud/dcloud:0.2

This will Mac users to run a Docker image from docker.io that contains dcloud, open up a bash shell and run dcloud.

TODO
---------------------

Update docs once the pivotal namespace has been registered with docker registry and a dcloud image is hosted there.

How to make artifacts
=====================================

This section talks about how to make dcloud distributable artifacts. Currently we have only one option, docker image.

Docker image
-----------------------

The provided `Makefile` supports building docker images under any namespace provided

    NAMESPACE=mynamespacehere make --environment-overrides docker-build

The above example will create a docker image named `mynamespacehere/dcloud:0.2`

### If you want to publish the image to docker.io

    docker login 

then

    make docker-push 

or

    make docker-release # which will build images and push to docker.io


