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

"""Server operation implementations; see protocol.py for types"""
from sync_server.oracle import get_connection
import cx_Oracle
import hashlib
from sys import stderr
import sync_db.error

OFFLINE_LICENSE_EXPIRY_TIME = "3000-01-01 00:00:00 +0000"
COPYRIGHT = ("Copyright (c) 2012 Citrix Systems, Inc.- XenClient - "
             "{3282892a-f098-4e3d-a591-9504b704a4d1}")

def hello(_device_uuid, _server_port, client_version):
    """Check client version is okay, and return server version"""
    # TODO: act on client version
    return {'server_version': 1}

def get_state(_device_uuid, _server_port):
    """Return target state for machine"""

    def decode_boolean(value):
        return value == 't'

    def decode_disk_type(value):
        return 'iso' if value == 'i' else 'vhd'

    with sync_db.error.convert():
        connection = get_connection(_server_port)
        cursor = connection.cursor()
        device_info_cursor = connection.cursor()
        device_config_cursor = connection.cursor()
        vm_instances_cursor = connection.cursor()
        vm_instance_config_cursor = connection.cursor()
        vm_instance_disks_cursor = connection.cursor()
        disks_cursor = connection.cursor()

        cursor.callproc('sync_server.get_device_state',
                        keywordParameters={
                            'device_uuid': _device_uuid,
                            'device_info': device_info_cursor,
                            'device_config': device_config_cursor,
                            'vm_instances': vm_instances_cursor,
                            'vm_instance_config': vm_instance_config_cursor,
                            'vm_instance_disks': vm_instance_disks_cursor,
                            'disks': disks_cursor})

        data = {'config': [],
                'disks': [],
                'license': {},
                'repo': {}}

        for (release, build, repo_uuid, repo_file_size, repo_file_hash,
             license_expiry_time, license_hash,
             online_licensing) in device_info_cursor:
            data['repo']['release'] = release
            data['repo']['build'] = build
            data['repo']['repo_uuid'] = repo_uuid
            data['repo']['file_size'] = repo_file_size
            data['repo']['file_hash'] = repo_file_hash

            if decode_boolean(online_licensing):
                data['license']['expiry_time'] = license_expiry_time
                data['license']['hash'] = license_hash
            else:
                data['license']['expiry_time'] = OFFLINE_LICENSE_EXPIRY_TIME
                data['license']['hash'] = hashlib.sha256(
                    _device_uuid + COPYRIGHT +
                    OFFLINE_LICENSE_EXPIRY_TIME).hexdigest()

        for daemon, key, value in device_config_cursor:
            data['config'].append({'daemon': daemon,
                                   'key': key,
                                   'value': value})

        vms = {}

        for (vm_instance_uuid, vm_uuid, vm_instance_name,
             locked, removed) in vm_instances_cursor:
            vms[vm_instance_uuid] = {'vm_instance_uuid': vm_instance_uuid,
                                     'vm_uuid': vm_uuid,
                                     'name': vm_instance_name,
                                     'locked': decode_boolean(locked),
                                     'removed': decode_boolean(removed),
                                     'disks': [],
                                     'user_name': 'root',
                                     'config': []}

        for vm_instance_uuid, daemon, key, value in vm_instance_config_cursor:
            vms[vm_instance_uuid]['config'].append({'daemon': daemon,
                                                    'key': key,
                                                    'value': value})

        for vm_instance_uuid, disk_uuid in vm_instance_disks_cursor:
            vms[vm_instance_uuid]['disks'].append({'diskuuid':disk_uuid, 
                                                   'config':[]})

        data['vms'] = [vms[key] for key in sorted(vms.keys())]

        for (disk_uuid, disk_name, disk_type, disk_size, disk_hash,
             encryption_key, shared, read_only) in disks_cursor:
            data['disks'].append({'diskuuid': disk_uuid,
                                  'name': disk_name,
                                  'type': decode_disk_type(disk_type),
                                  'size': disk_size,
                                  'disk_hash' : disk_hash,
                                  'encryption_key': encryption_key,
                                  'shared': decode_boolean(shared),
                                  'read_only': decode_boolean(read_only)})

        return data

def current_state(_device_uuid, _server_port, state):
    """Machine has just supplied us with state"""
    print >>stderr, 'device=', _device_uuid, 'state:', state

    with sync_db.error.convert():
        connection = get_connection(_server_port)
        cursor = connection.cursor()

        cursor.callproc('sync_server.report_device_state',
                        keywordParameters={
                            'device_uuid': _device_uuid,
                            'release': state.get('release'),
                            'build': state.get('build')})

    return {}
