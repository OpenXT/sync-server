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

from os.path import dirname
import sys
sys.path.append(dirname(__file__))
from sync_server.implementations import hello, get_state, current_state
from sync_server.util import fail, start
from sys import stderr
from json import loads, dumps
from httplib import responses, FORBIDDEN, OK, METHOD_NOT_ALLOWED, NOT_FOUND

def application(environ, start_response, implementations=None):
    """Serve main server document requests.

    Synchronizer has no web framework; synchronizer needs no web
    framework."""
    if implementations == None:
        implementations = {'hello':hello, 'get_state':get_state,
                           'current_state':current_state}

    print >> stderr, 'request method', environ['REQUEST_METHOD']
    method = environ['REQUEST_METHOD']
    if method not in ['GET', 'PUT']:
        return fail(start_response, METHOD_NOT_ALLOWED,
                    'Bad request method ' + environ['REQUEST_METHOD'] +
                    '; should be GET or PUT')

    path = environ['PATH_INFO']
    # for now we have some direct dispatch but use old code for 
    # parts of the web interface not implemented that way
    spl = path.split('/')
    if method == 'GET' and spl[:2] == ['', 'hello'] and len(spl) == 3:
        try:
            client_version = int(spl[2])
        except ValueError:
            return fail(start_response, FORBIDDEN,
                        'client_version %r is not integer' %(spl[2]))
        # TODO: handle exceptions
        out = implementations['hello'](environ.get('REMOTE_USER'), 
                                       int(environ['SERVER_PORT']),
                                       client_version)
    elif method == 'GET' and path == '/target_state':
        # TODO: handle exceptions
        out = implementations['get_state'](environ.get('REMOTE_USER'), 
                                           int(environ['SERVER_PORT']))
    elif method == 'PUT' and path == '/current_state':
        doc = environ['wsgi.input'].read()
        # TODO: handle exceptions
        out = implementations['current_state'](environ.get('REMOTE_USER'), 
                                               int(environ['SERVER_PORT']),
                                               loads(doc))
    else:
        return fail(start_response, NOT_FOUND, 'No such document')

    headers = [('content-type', 'application/json; charset=utf-8')]
    start(start_response, OK, headers)
    return [dumps(out),]
