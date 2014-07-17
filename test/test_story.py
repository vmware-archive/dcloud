# coding: utf-8

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

import os, time
import dcloud.dcloud as dcloud
import dcloud.utils.ssh as ssh

# CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
# 
# clusterConfig = {
# "id" : "phd",
# "nodes": [
#     {
#         "hostname" : "master.mydomain.com",
#         "imageName" : "phd:installed",
#         "cmd" : "/tmp/phd-docker/bin/start_pcc.sh"
#     },
#     {
#         "hostname" : "slave1.mydomain.com",
#         "imageName" : "phd:base",
#         "cmd" : "cp /tmp/phd-docker/shared/start_slave.sh /tmp/phd-docker/bin && /tmp/phd-docker/bin/start_slave.sh",
#                         "volumes" : [
#             CURRENT_DIRECTORY + "/slave:/tmp/phd-docker/shared"
#                         ]
#     },
#     {
#         "hostname" : "slave2.mydomain.com",
#         "imageName" : "phd:base",
#         "cmd" : "cp /tmp/phd-docker/shared/start_slave.sh /tmp/phd-docker/bin && /tmp/phd-docker/bin/start_slave.sh",
#                         "volumes" : [
#             CURRENT_DIRECTORY + "/slave:/tmp/phd-docker/shared"
#                         ]
#     }
# ]
# }
# 	
# result = dcloud.create(clusterConfig)
# 
# time.sleep(5)
# 
# print "aaa"
# _, out, err = ssh.exec_command2(result.dns, "root", "changeme", "ls /")
# print "echo:::" + out
# print "echo:::" + err





