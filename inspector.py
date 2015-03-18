#!/usr/bin/env python
# encoding: utf-8


import optparse
from construct import *
from functools import wraps
from azure.storage import BlobService
from formats import *


VERSION = 'v1.0.0'
USAGE = 'usage: %prog [options] arg1 arg2'
HD_TYPE_FIXED = 2
HD_TYPE_DYNAMIC = 3


def get_options():
    """TODO: Docstring for get_options.
    :returns: TODO
    """
    parser = optparse.OptionParser(usage=USAGE, version=VERSION)

    parser.add_option('-n', '--name', action='store', type='string',
                      help='Account Name', dest='account_name', default='')
    parser.add_option('-k', '--key', action='store', type='string',
                      help='Account Key', dest='account_key', default='')
    parser.add_option('-v', '--vhd', action='store', type='string',
                      help='VHD File', dest='vhd', default='')
    parser.add_option('-c', '--container', action='store', type='string',
                      help='Container Name', dest='container', default='vhds')
    parser.add_option('-b', '--hostbase', action='store', type='string',
                      help='Host Base', dest='host_base', default='.blob.core.windows.net')
    parser.add_option('-t', '--test', action='store_true', dest='test',
                      help='Test the difference between sync and async.')

    return parser.parse_args()


def check_vhd_type(blob_service, options):
    """TODO: Docstring for check_vhd_type.

    :blob_service: TODO
    :properties: TODO
    :options: TODO
    :returns: TODO

    """
    properties = blob_service.get_blob_properties(options.container, options.vhd)
    rangerange = 'bytes=' + str(int(properties['content-length']) - 512) + \
            '-' + str(int(properties['content-length'])-1)
    blob_page = blob_service.get_blob(options.container,
                                    options.vhd,
                                    x_ms_range=rangerange)
    hd_ftr = Hd_ftr.parse(blob_page)

    return hd_ftr.type


def get_superblock(blob_service, start_at_byte, options):
    """TODO: Docstring for get_superblock.

    :blob_service: TODO
    :partition: TODO
    :options: TODO
    :returns: TODO

    """
    rangerange = 'bytes=' + str(start_at_byte+1024) + \
            '-' + str(start_at_byte+1024+1023)
    blob_page = blob_service.get_blob(options.container,
                                    options.vhd,
                                    x_ms_range=rangerange)

    return Superblock.parse(blob_page)


def get_group_desc_table(blob_service, start_at_byte, options):
    """TODO: Docstring for get_group_desc_table.

    :blob_service: TODO
    :start_at_byte: TODO
    :options: TODO
    :returns: TODO

    """
    # Can be beautified. Pendding.
    if options.block_size == 1024:
        offset = 2048
        Group_desc_table = Group_desc_table0
    if options.block_size == 2048:
        offset = 2048
        Group_desc_table = Group_desc_table1
    if options.block_size == 4096:
        offset = 4096
        Group_desc_table = Group_desc_table2

    rangerange = 'bytes=' + str(start_at_byte+offset) + \
            '-' + str(start_at_byte+offset+options.block_size-1)
    blob_page = blob_service.get_blob(options.container,
                                    options.vhd,
                                    x_ms_range=rangerange)

    return Group_desc_table.parse(blob_page)


def retrieve_inode_file(arg1):
    """TODO: Docstring for retrieve_inode_file.

    :arg1: TODO
    :returns: TODO

    """
    pass


def parse_KB(superblock):
    """TODO: Docstring for parse_KB.

    :superblock: TODO
    :returns: TODO

    """
    if superblock.log_block_size == 'OneKB':
        result = 1024
    if superblock.log_block_size == 'TwoKB':
        result = 2048
    if superblock.log_block_size == 'FourKB':
        result = 4096

    return result


def parse_partition(blob_service, partition, options):
    """TODO: Docstring for parse_partition.

    :blob_service: TODO
    :partition: TODO
    :options: TODO
    :returns: TODO

    """
    start_at_byte = partition.starting_sector * 512
    superblock = get_superblock(blob_service, start_at_byte, options)
    options.block_size = parse_KB(superblock)
    group_desc_table = get_group_desc_table(blob_service,
                                              start_at_byte,
                                              options)

    group_num = ((superblock.blocks_count - superblock.first_data_block - 1) /
                 superblock.blocks_per_group) + 1

    for group_desc in group_desc_table.group_desc:
        if superblock.inode_size == 128:
            Inode = Inode_128
        if superblock.inode_size == 256:
            Inode = Inode_256
        offset = options.block_size * group_desc.inode_table_ptr
        table_size = superblock.inodes_per_group * superblock.inode_size
        Inode_table = Struct('inode_table',
                             Array(superblock.inodes_per_group, Inode),
                             )
        rangerange = 'bytes=' + str(start_at_byte+offset) + \
                '-' + str(start_at_byte+offset+table_size-1)
        blob_page = blob_service.get_blob(options.container,
                                        options.vhd,
                                        x_ms_range=rangerange)
        inode_table = Inode_table.parse(blob_page)
        print inode_table.inode[1]
        print inode_table.inode[2006]
        print inode_table.inode[670]
        print group_desc
        exit(0)

    print partition
    print superblock
    print group_num


def parse_image(blob_service, options):
    """TODO: Docstring for parse_image.

    :blob_service: TODO
    :options: TODO
    :returns: TODO

    """
    blob_page = blob_service.get_blob(options.container,
                                    options.vhd,
                                    x_ms_range='bytes=0-511')

    mbr = Mbr.parse(blob_page)

    for partition in mbr.mbr_partition_entry:
        partition.boot_indicator == 0x80 and \
                parse_partition(blob_service, partition, options)


def main():
    """TODO: Docstring for main.
    :returns: TODO

    """
    (options, args) = get_options()

    blob_service = BlobService(options.account_name,
                               options.account_key,
                               host_base=options.host_base)

    check_vhd_type(blob_service, options) == HD_TYPE_FIXED and \
            parse_image(blob_service, options)


if __name__ == '__main__':
    main()
