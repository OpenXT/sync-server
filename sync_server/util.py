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

from httplib import (responses, OK, PARTIAL_CONTENT,
                     REQUESTED_RANGE_NOT_SATISFIABLE)
from os import SEEK_END
from re import match
from sys import stderr

def start(start_response, code, headers):
    """Send HTTP status and headers"""
    start_response(str(code) + ' ' + responses[code], headers)

def fail(start_response, code, message):
    """Handle failures"""
    print >> stderr, 'ERROR:', code, message
    start(start_response, code, [('content-type', 'text/plain')])
    return [str(code) + ' ' + responses[code] + ': ' + message]

def serve_file(environ, start_response, file_path):
    """Handle GET request by returning contents of file_path"""
    file_wrapper = environ.get('wsgi.file_wrapper')
    print >> stderr, 'file wrapper', repr(file_wrapper)
    file_like = file(file_path, 'rb')
    file_like.seek(0, SEEK_END)
    file_size = file_like.tell()
    http_range = environ.get('HTTP_RANGE')
    if http_range is None:
        code = OK
        headers = [('content-length', '%d' % file_size)]
        file_like.seek(0)
    else:
        from httplib import NOT_FOUND
        print >> stderr, 'range', http_range
        m = match('bytes=(\d+)-$', http_range)
        if m is None:
            return fail(start_response, REQUESTED_RANGE_NOT_SATISFIABLE,
                        'Requested range not satisfiable')
        first_byte = int(m.group(1))
        if first_byte >= file_size:
            return fail(start_response, REQUESTED_RANGE_NOT_SATISFIABLE,
                        'Start of range beyond end of file')
        code = PARTIAL_CONTENT
        headers = [('content-range',
                    '%d-%d/%d' % (first_byte, file_size - 1, file_size)),
                   ('content-length',
                    '%d' % (file_size - first_byte))]
        file_like.seek(first_byte)
    for header in headers:
        print >> stderr, header[0], header[1]
    start(start_response, code, headers)
    if file_wrapper:
        print >> stderr, 'satisfying using file_wrapper'
        return file_wrapper(file_like)
    else:
        print >> stderr, 'satisfying using iter'
        return iter(lambda: file_like.read(4096), '')
