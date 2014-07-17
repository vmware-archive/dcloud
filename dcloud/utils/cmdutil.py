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


import subprocess
import logging

def execute(*args, **kwargs):
    
    logging.info("executing command: " + " ".join(args[0]))
    process = subprocess.Popen(stdout=subprocess.PIPE, *args, **kwargs)
    stdout, stderr = process.communicate() # TODO stderr always (when retcode is 0 and is not 0) None. Why??
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = args[0]
        # raise subprocess.CalledProcessError(retcode, cmd, output=stdout)
        logging.warn("**WARN** command failed. retcode=" + str(retcode))
    return retcode, stdout

