#!/usr/bin/env python
# encoding: utf-8


import copy
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
    parser.add_option('-e', '--ext', action='store', type='int',
                      help='EXT2/3/4', dest='ext', default='4')
    parser.add_option('-t', '--test', action='store_true', dest='test',
                      help='Test the difference between sync and async.')

    return parser.parse_args()


def log_time(fn):
    """TODO: Docstring for log_time.

    :fn: TODO
    :returns: TODO

    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        start_time = time.time()

        result = fn(*args, **kwargs)

        end_time = time.time()
        print_info('Time used : {0}'.format(end_time - start_time))

        return result

    return wrapper


def check_vhd_type(options):
    """TODO: Docstring for check_vhd_type.

    :properties: TODO
    :options: TODO
    :returns: TODO

    """
    blob_service = options.blob_service
    properties = blob_service.get_blob_properties(options.container, options.vhd)
    rangerange = 'bytes=' + str(int(properties['content-length']) - 512) + \
            '-' + str(int(properties['content-length'])-1)
    blob_page = blob_service.get_blob(options.container,
                                    options.vhd,
                                    x_ms_range=rangerange)
    hd_ftr = Hd_ftr.parse(blob_page)

    return hd_ftr.type


def get_superblock(start_at_byte, options):
    """TODO: Docstring for get_superblock.

    :partition: TODO
    :options: TODO
    :returns: TODO

    """
    blob_page = get_blob_page(start_at_byte, 1024, 1024, options)

    return Superblock.parse(blob_page)


def get_group_desc_table(start_at_byte, options):
    """TODO: Docstring for get_group_desc_table.

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

    blob_page = get_blob_page(start_at_byte, offset, options.block_size, options)

    return Group_desc_table.parse(blob_page)


def get_blob_page(start_at_byte, offset, page_size, options):
    """TODO: Docstring for get_blob_page.

    :offset: TODO
    :page_size: TODO
    :options: TODO
    :returns: TODO

    """
    rangerange = 'bytes=' + str(start_at_byte+offset) + \
            '-' + str(start_at_byte+offset+page_size-1)
    blob_page = options.blob_service.get_blob(options.container,
                                              options.vhd,
                                              x_ms_range=rangerange)

    return blob_page


def get_data_from_dir_ptr(dir_ptr, start_at_byte, options):
    """TODO: Docstring for get_data_from_dir_ptr.

    :dir_ptr: TODO
    :start_at_byte: TODO
    :options: TODO
    :returns: TODO

    """
    offset = block_ptr_to_byte(dir_ptr, options)
    blob_page = get_blob_page(start_at_byte, offset,
                              options.block_size, options)

    return blob_page


def get_data_from_indir_ptr1(indir_ptr, start_at_byte, options):
    """TODO: Docstring for get_data_from_indir_ptr1.

    :indir_ptr: TODO
    :start_at_byte: TODO
    :options: TODO
    :returns: TODO

    """
    Indir_ptr_list = Struct('indir_ptr_list',
                            Array(options.block_size/4, ULInt32('indir_ptr')),
                            )
    offset = block_ptr_to_byte(dir_ptr, options)
    blob_page = get_blob_page(start_at_byte, offset, options.block_size, options)
    indir_ptr_list = Indir_ptr_list.parse(blob_page)

    data = ''
    for dir_ptr in indir_ptr_list.indir_ptr_list:
        data = data + get_data_from_dir_ptr(dir_ptr, start_at_byte, options)

    return data


def get_data_from_indir_ptr2(indir_ptr, start_at_byte, options):
    """TODO: Docstring for get_data_from_indir_ptr2.

    :indir_ptr: TODO
    :start_at_byte: TODO
    :options: TODO
    :returns: TODO

    """
    Indir_ptr_list = Struct('indir_ptr_list',
                            Array(options.block_size/4, ULInt32('indir_ptr')),
                            )
    offset = block_ptr_to_byte(dir_ptr, options)
    blob_page = get_blob_page(start_at_byte, offset, options.block_size, options)
    indir_ptr_list = Indir_ptr_list.parse(blob_page)

    data = ''
    for indir_ptr1 in indir_ptr_list.indir_ptr_list:
        data = data + get_data_from_indir_ptr1(dir_ptr, start_at_byte, options)

    return data


def get_data_from_indir_ptr3(indir_ptr, start_at_byte, options):
    """TODO: Docstring for get_data_from_indir_ptr3.

    :indir_ptr: TODO
    :start_at_byte: TODO
    :options: TODO
    :returns: TODO

    """
    Indir_ptr_list = Struct('indir_ptr_list',
                            Array(options.block_size/4, ULInt32('indir_ptr')),
                            )
    offset = block_ptr_to_byte(dir_ptr, options)
    blob_page = get_blob_page(start_at_byte, offset, options.block_size, options)
    indir_ptr_list = Indir_ptr_list.parse(blob_page)

    data = ''
    for indir_ptr2 in indir_ptr_list.indir_ptr_list:
        data = data + get_data_from_indir_ptr2(dir_ptr, start_at_byte, options)

    return data


def get_data_from_extent(extent, start_at_byte, options):
    """TODO: Docstring for get_data_from_extent.

    :extent: TODO
    :start_at_byte: TODO
    :options: TODO
    :returns: TODO

    """
    block_ptr = (extent.start_hi << 32) + extent.start_lo
    offset = block_ptr_to_byte(block_ptr, options)
    blob_page = get_blob_page(start_at_byte, offset,
                              extent.len*options.block_size-1, options)

    return blob_page


def get_data_from_idx(idx, start_at_byte, options):
    """TODO: Docstring for get_data_from_idx.

    :idx: TODO
    :start_at_byte: TODO
    :options: TODO
    :returns: TODO

    """
    block_ptr = (idx.leaf_hi << 32) + idx.leaf_lo
    offset = block_ptr_to_byte(block_ptr, options)
    blob_page = get_blob_page(start_at_byte, offset,
                              options.block_size-1, options)
    Node_block = Struct('index_node_block',
                              Ext4_extent_header,
                              Array(options.block_size/12, Ext4_extent),
                              )

    return Node_block.parse(blob_page)


def get_data_from_ext4_tree(extent_tree, start_at_byte, options):
    """TODO: Docstring for get_data_from_ext4_i_block.

    :extent_tree: TODO
    :returns: TODO

    """
    if extent_tree.ext4_extent_header.depth == 0:
        tmp = sorted([(extent.block, get_data_from_extent(extent,
                                                          start_at_byte,
                                                          options))
                      for index, extent in enumerate(extent_tree.ext4_extent)
                      if index < extent_tree.ext4_extent_header.entries],
                     key=lambda e: e[0])

        return reduce(lambda a, b: (0, a[1]+b[1]), tmp)[1]

    else:
        Indexs = Array(extent_tree.ext4_extent_header.max, Ext4_extent_idx)
        indexs = Indexs.parse(Extents.build(extent_tree.ext4_extent))
        tmp = sorted([(idx.block, get_data_from_ext4_tree(get_data_from_idx(node_block,
                                                                            start_at_byte,
                                                                            options),
                                                          start_at_byte,
                                                          options))
                      for index, idx in enumerate(indexs)
                      if index < extent_tree.ext4_extent_header.entries],
                     key=lambda e: e[0])

        return reduce(lambda a, b: (0, a[1]+b[1]), tmp)[1]


def download_from_ext3_inode(inode, start_at_byte, options):
    """TODO: Docstring for get_data_from_inode.

    :inode: TODO
    :start_at_byte: TODO
    :options: TODO
    :returns: TODO

    """
    data = ''
    for index, ptr in enumerate(inode.blocks_ptr):
        if ptr == 0:
            break

        offset = block_ptr_to_byte(ptr, options)
        blob_page = get_blob_page(start_at_byte, offset,
                                  options.block_size, options)

        if index < 12:
            data = data + blob_page
        elif index == 12:
            data = get_data_from_indir_ptr1(ptr, start_at_byte, options)
        elif index == 13:
            data = get_data_from_indir_ptr2(ptr, start_at_byte, options)
        elif index == 14:
            data = get_data_from_indir_ptr3(ptr, start_at_byte, options)

    return True


def download_from_ext4_inode(inode, start_at_byte, options):
    """TODO: Docstring for get_data_from_ext4_inode.

    :inode: TODO
    :start_at_byte: TODO
    :options: TODO
    :returns: TODO

    """
    data = get_data_from_ext4_tree(inode.ext4_extent_tree,
                                      start_at_byte,
                                      options)[:inode.size]
    with open('result.txt', 'w') as result:
        result.write(data)

    return True


def block_ptr_to_byte(block_ptr, options):
    """TODO: Docstring for block_ptr_to_byte.

    :block_ptr: TODO
    :options: TODO
    :returns: TODO

    """
    return options.block_size * block_ptr


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


def parse_partition(partition, options):
    """TODO: Docstring for parse_partition.

    :partition: TODO
    :options: TODO
    :returns: TODO

    """
    start_at_byte = partition.starting_sector * 512
    superblock = get_superblock(start_at_byte, options)
    options.block_size = parse_KB(superblock)
    group_desc_table = get_group_desc_table(start_at_byte, options)

    for group_desc in group_desc_table.group_desc:
        if superblock.inode_size == 128:
            if options.ext == 4:
                Inode = Ext4_inode_128
            else:
                Inode = Ext3_inode_128
        elif superblock.inode_size == 256:
            if options.ext == 4:
                Inode = Ext4_inode_256
            else:
                Inode = Ext3_inode_256

        Inode_table = Struct('inode_table',
                             Array(superblock.inodes_per_group, Inode),
                             )
        offset = block_ptr_to_byte(group_desc.inode_table_ptr, options)
        table_size = superblock.inodes_per_group * superblock.inode_size
        blob_page = get_blob_page(start_at_byte, offset, table_size, options)
        inode_table = Inode_table.parse(blob_page)

        inode_table.inode[422].flags.EXTENTS and \
                download_from_ext4_inode(inode_table.inode[422],
                                         start_at_byte, options) \
                or download_from_ext3_inode(inode_table.inode[422],
                                            start_at_byte, options)

        exit(0)


def parse_image(options):
    """TODO: Docstring for parse_image.

    :options: TODO
    :returns: TODO

    """
    blob_page = options.blob_service.get_blob(options.container,
                                    options.vhd,
                                    x_ms_range='bytes=0-511')

    mbr = Mbr.parse(blob_page)

    for partition in mbr.mbr_partition_entry:
        pt = partition.partition_type
        if pt == 0x83 or pt == 0x93:
            partition.boot_indicator == 0x80 and \
                    parse_partition(partition, copy.deepcopy(options))
        else:
            print 'Unsupported \'partition type\' / \'file system\'.'

    return True


def main():
    """TODO: Docstring for main.
    :returns: TODO

    """
    (options, args) = get_options()

    blob_service = BlobService(options.account_name,
                               options.account_key,
                               host_base=options.host_base)
    options.blob_service = blob_service

    check_vhd_type(options) == HD_TYPE_FIXED and \
            parse_image(options)


if __name__ == '__main__':
    main()
