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


import dcloud.utils.cmdutil as cmdutil

class TestCmdUtil(object):

    # @nose.with_setup(AbstractTest.setup, AbstractTest.teardown)
    def test_positive(self):
        retcode, stdout = cmdutil.execute(["ls", "-laF", "/"])
        assert retcode == 0
        assert "home/" in stdout

    def test_negative(self):
        # error case
        # on ubuntu 
        # jaoki@jaoki-ubuntu:~/coding/phd-docker/dcloud$ ls aaaaaa
        # ls: cannot access aaaaaa: No such file or directory

        retcode, stdout = cmdutil.execute(["ls", "aaaaaa"])
        assert retcode == 2
        assert stdout == ""
