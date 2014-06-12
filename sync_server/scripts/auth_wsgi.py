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

from os.path import dirname, join
import sys
sys.path.append(dirname(__file__))
from sync_server.oracle import get_connection
import cx_Oracle
import sync_db.error
import hashlib

def get_realm_hash(environ, user, realm):
    connection = get_connection(int(environ['SERVER_PORT']))
    try:
        with sync_db.error.convert():
            cursor = connection.cursor()
            secret = cursor.callfunc("sync_server.get_device_secret",
                                     cx_Oracle.STRING,
                                     keywordParameters={
                                         "device_uuid": user})
    except sync_db.error.SyncError, e:
        # if we fail to get the device secret, generate 403.
        print >>sys.stderr, repr(e)
        return None

    return hashlib.md5('%s:%s:%s' % (user, realm, secret)).hexdigest()
