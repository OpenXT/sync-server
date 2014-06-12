#
# Copyright (c) 2012 Citrix Systems, Inc.
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"""Connect to oracle using a config file determined by port number"""
from cx_Oracle import connect, Cursor
from os import environ
from os.path import join
from ConfigParser import RawConfigParser

def get_connection(server_port):
    """Return a connection to Oracle"""
    # sadly we cannot use SetEnv to pass environemnt to WSGIAuthUserScript
    # (http://code.google.com/p/modwsgi/wiki/AccessControlMechanisms)
    # so instead we read a per port config file
    config = RawConfigParser()
    config.read(join('/etc', 'sync2', 'sync-%d.conf' % server_port))
    
    for key in ['NLS_LANG', 'ORACLE_SID', 'ORACLE_HOME']:
        environ[key] = config.get('environment', key)

    target = config.get('database', 'login')
    return connect(target)
