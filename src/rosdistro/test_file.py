# Software License Agreement (BSD License)
#
# Copyright (c) 2013, Open Source Robotics Foundation, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Open Source Robotics Foundation, Inc. nor
#    the names of its contributors may be used to endorse or promote
#    products derived from this software without specific prior
#    written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from .package import Package
from .repository import Repository


class TestFile(object):

    def __init__(self, name, data, expected_type=None):
        expected_type = expected_type if expected_type is not None else 'test'
        assert data['type'] == str(expected_type)
        self._type = str(expected_type)
        self.version = int(data['version'])
        assert self.version == 1

        self.name = name

        self.repositories = {}
        self.packages = {}
        if 'repositories' in data:
            for repo_name in data['repositories']:
                repo_data = data['repositories'][repo_name]
                repo = Repository(repo_name, repo_data)
                self.repositories[repo_name] = repo

                if repo.package_names:
                    for pkg_name in repo.package_names:
                        assert pkg_name not in self.packages
                        try:
                            pkg_data = repo_data['packages'][pkg_name]
                        except KeyError:
                            pkg_data = None
                        self._add_package(pkg_name, repo, pkg_data)
                else:
                    # no package means a single package in the root of the repository
                    self._add_package(repo_name, repo, {'subfolder': '.'})

    def _add_package(self, pkg_name, repo, pkg_data):
        assert pkg_name not in self.packages
        pkg = Package(pkg_name, repo.name, pkg_data)
        if pkg.status is None:
            pkg.status = repo.status
        if pkg.status_description is None:
            pkg.status_description = repo.status_description
        self.packages[pkg_name] = pkg

    def get_data(self):
        data = {}
        data['type'] = self._type
        data['version'] = 1
        data['repositories'] = {}
        for repo_name in sorted(self.repositories):
            repo = self.repositories[repo_name]
            data['repositories'][repo_name] = repo.get_data()
            for pkg_name in repo.package_names:
                pkg_data = self.packages[pkg_name].get_data(len(repo.package_names) == 1)
                # skip unary if its data is an empty dict
                if len(repo.package_names) == 1 and not pkg_data:
                    continue
                if 'packages' not in data['repositories'][repo_name]:
                    data['repositories'][repo_name]['packages'] = {}
                data['repositories'][repo_name]['packages'][pkg_name] = pkg_data
        return data