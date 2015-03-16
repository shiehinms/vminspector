#!/usr/bin/env python
# encoding: utf-8


import optparse
from construct import *
from functools import wraps
from azure.storage import BlobService
from formats import *


VERSION = 'v1.0.0'
USAGE = 'usage: %prog [options] arg1 arg2'


def get_options():
    """TODO: Docstring for get_options.
    :returns: TODO
    """
    parser = optparse.OptionParser(usage=USAGE, version=VERSION)

    parser.add_option('-n', '--name', action='store', type='string',
                      help='Account Name', dest='account_name', default='')
    parser.add_option('-k', '--key', action='store', type='string',
                      help='Account Key', dest='account_key', default='')
    parser.add_option('-b', '--hostbase', action='store', type='string',
                      help='Host Base', dest='host_base', default='.blob.core.windows.net')
    parser.add_option('-t', '--test', action='store_true', dest='test',
                      help='Test the difference between sync and async.')
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
                      help='Output verbosely.')

    return parser.parse_args()


def get_data(blob_service, container_name, blob_name, from_to):
    """TODO: Docstring for get_data.

    :blob_service: TODO
    :returns: TODO

    """
    return blob_service.get_blob(container_name, blob_name, x_ms_range=from_to)


def main():
    """TODO: Docstring for main.
    :returns: TODO

    """
    (options, args) = get_options()

    blob_service = BlobService(options.account_name,
                               options.account_key,
                               host_base=options.host_base)
    containers = blob_service.list_containers()

    for container in containers:
        print container.name
        for blob in blob_service.list_blobs(container.name):
            print blob.name

        result = blob_service.get_page_ranges(container.name, 'shieh-shieh-2015-03-15.vhd')
        print result[0].start, result[0].end

        properties =  blob_service.get_blob_properties(container.name, 'shieh-shieh-2015-03-15.vhd')
        rangerange = 'bytes=' + str(int(properties['content-length']) - 512) + '-' + str(int(properties['content-length'])-1)
        print rangerange
        result1 = blob_service.get_blob(container.name, 'shieh-shieh-2015-03-15.vhd', x_ms_range=rangerange)
        print hd_ftr.parse(result1)

        result2 = blob_service.get_blob(container.name, 'shieh-shieh-2015-03-15.vhd', x_ms_range='bytes=0-511')
        with open('result.txt', 'w') as output:
            output.write(result2)
        print mbr.parse(result2)
        # result2 = blob_service.get_blob(container.name, 'shieh-shieh-2015-03-15.vhd', x_ms_range='bytes=1536-2559')
        # print superblock.parse(result2)


if __name__ == '__main__':
    main()
