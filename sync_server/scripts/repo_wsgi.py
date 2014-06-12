#
# Copyright (c) 2013 Citrix Systems, Inc.
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

""" Synchronizer XT WSGI script """

from os.path import dirname, join
import sys
sys.path.append(dirname(__file__))

from sys import stderr
from os import environ
from sync_server.oracle import get_connection
from sync_server.util import serve_file
import cx_Oracle
import sync_db.error

def application(environ, start_response):
    """WSGI entry point"""
    device_uuid = environ.get('REMOTE_USER')
    print >> stderr, 'device uuid', device_uuid
    request_path = environ['PATH_INFO']
    print >> stderr, 'request path', request_path
    base = request_path.split('/')[-1]
    repo_uuid = base.split('.')[0]
    print >> stderr, 'repo uuid', repo_uuid
    connection = get_connection(int(environ['SERVER_PORT']))
    # TODO: handle exceptions:
    file_path = get_repo_path(connection, device_uuid, repo_uuid)
    print >> stderr, 'file path', file_path
    return serve_file(environ, start_response, file_path)

def get_repo_path(connection, device_uuid, repo_uuid):
    """Map repo_uuid to file_path"""
    with sync_db.error.convert():
        cursor = connection.cursor()
        file_path = cursor.callfunc("sync_server.get_repo_path",
                                    cx_Oracle.STRING,
                                    keywordParameters={
                                        "device_uuid": device_uuid,
                                        "repo_uuid": repo_uuid})

    return file_path
