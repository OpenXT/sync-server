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

"""Test HTTP/WSGI/dispatch hook up"""
import server_wsgi
from urllib2 import urlopen
from multiprocessing import Process, Queue
from wsgiref.simple_server import make_server
from socket import error
from json import loads
from server_wsgi import application
from os import environ

def run_server(queue, wsgi_application):
    """Run a WSGI server"""
    port = 8000
    environ['REMOTE_USER'] = '42'
    while 1:
        try:
            server = make_server('', port, wsgi_application)
        except error:
            port += 1
        else:
            break
    queue.put(port)
    server.serve_forever()

def start_server(wsgi_application):
    """Start test HTTP server"""
    queue = Queue()
    process = Process(target=run_server, args=(queue, wsgi_application))
    process.start()
    port = queue.get()
    return (process, queue), port

def close_server(server):
    """Shut down test HTTP server"""
    server[0].terminate()

def sample_hello(_device_uuid, _server_port, client_version):
    return {'server_version':1}

def test_hello():
    """Check we can invoke the hello method"""
    def myapp(*l):
        return application(*(list(l)+[{'hello':sample_hello}]))
    server, port = start_server(myapp)
    try:
        print 'port', port
        data = loads(urlopen('http://127.0.0.1:%d/hello/1' % port).read())
        print 'data', data
    finally:
        close_server(server)
    print data

if __name__ == "__main__":
    test_hello()
