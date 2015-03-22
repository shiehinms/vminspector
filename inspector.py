#!/usr/bin/env python
# encoding: utf-8


import math
import os.path
from util import *
from formats import *
from construct import *
from operator import add


HD_TYPE_FIXED = 2
HD_TYPE_DYNAMIC = 3
(options, args) = get_options()


@embed_params(blob_service=options.blob_service,
              container=options.container, vhd=options.vhd)
def check_vhd_type(blob_service, container, vhd):
    """TODO: Docstring for check_vhd_type.

    :properties: TODO
    :options: TODO
    :returns: TODO

    """
    properties = blob_service.get_blob_properties(container, vhd)
    rangerange = 'bytes=' + str(int(properties['content-length']) - 512) + \
            '-' + str(int(properties['content-length'])-1)
    blob_page = blob_service.get_blob(container, vhd, x_ms_range=rangerange)
    hd_ftr = Hd_ftr.parse(blob_page)

    return hd_ftr.type


def get_superblock(ph):
    """TODO: Docstring for get_superblock.

    :partition: TODO
    :options: TODO
    :returns: TODO

    """
    blob_page = get_blob_page(ph, 1024, 1024)

    return Superblock.parse(blob_page)


def get_group_desc_table(ph, block_size):
    """TODO: Docstring for get_group_desc_table.

    :options: TODO
    :returns: TODO

    """
    offset = int(math.ceil(2048.0 / block_size) * block_size)
    Group_desc_table = Struct('group_desc_table',
                              Array(block_size/32, Group_desc))

    blob_page = get_blob_page(ph, offset, block_size)

    return Group_desc_table.parse(blob_page)


@embed_params(blob_service=options.blob_service,
              container=options.container, vhd=options.vhd)
def get_blob_page(ph, offset, page_size,
                  blob_service, container, vhd):
    """TODO: Docstring for get_blob_page.

    :offset: TODO
    :page_size: TODO
    :options: TODO
    :returns: TODO

    """
    rangerange = 'bytes=' + str(ph+offset) + '-' + str(ph+offset+page_size-1)
    blob_page = blob_service.get_blob(container, vhd, x_ms_range=rangerange)

    return blob_page


def get_data_dir(dir_ptr, block_size):
    """TODO: Docstring for get_data_dir.

    :dir_ptr: TODO
    :options: TODO
    :returns: TODO

    """
    offset = block_ptr_to_byte(dir_ptr, block_size)
    blob_page = get_blob_page(ph, offset, block_size)

    return blob_page


def get_data_indir1(ph, block_size, indir_ptr):
    """TODO: Docstring for get_data_indir1.

    :indir_ptr: TODO
    :options: TODO
    :returns: TODO

    """
    Indir_ptr_list = Struct('indir_ptr_list',
                            Array(block_size/4, ULInt32('indir_ptr')))
    offset = block_ptr_to_byte(dir_ptr, block_size)
    blob_page = get_blob_page(ph, offset, block_size)
    parsed = Indir_ptr_list.parse(blob_page)

    data = reduce(add, (get_data_dir(dir_ptr, block_size)
                        for dir_ptr in parsed.indir_ptr_list))

    return data


def get_data_indir2(indir_ptr, block_size):
    """TODO: Docstring for get_data_indir2.

    :indir_ptr: TODO
    :options: TODO
    :returns: TODO

    """
    Indir_ptr_list = Struct('indir_ptr_list',
                            Array(block_size/4, ULInt32('indir_ptr')))
    offset = block_ptr_to_byte(dir_ptr, block_size)
    blob_page = get_blob_page(ph, offset, block_size)
    parsed = Indir_ptr_list.parse(blob_page)

    data = reduce(add, (get_data_dir(dir_ptr1, block_size)
                        for dir_ptr1 in parsed.indir_ptr_list))

    return data


def get_data_indir3(indir_ptr, block_size):
    """TODO: Docstring for get_data_indir3.

    :indir_ptr: TODO
    :options: TODO
    :returns: TODO

    """
    Indir_ptr_list = Struct('indir_ptr_list',
                            Array(block_size/4, ULInt32('indir_ptr')))
    offset = block_ptr_to_byte(dir_ptr, block_size)
    blob_page = get_blob_page(ph, offset, block_size)
    parsed = Indir_ptr_list.parse(blob_page)

    data = reduce(add, (get_data_dir(dir_ptr2, block_size)
                        for dir_ptr2 in parsed.indir_ptr_list))

    return data


def get_data_extent(ph, extent, block_size):
    """TODO: Docstring for get_data_extent.

    :extent: TODO
    :options: TODO
    :returns: TODO

    """
    block_ptr = (extent.start_hi << 32) + extent.start_lo
    offset = block_ptr_to_byte(block_ptr, block_size)
    blob_page = get_blob_page(ph, offset, extent.len*block_size-1)

    return blob_page


def get_data_idx(ph, idx, block_size):
    """TODO: Docstring for get_data_idx.

    :idx: TODO
    :options: TODO
    :returns: TODO

    """
    block_ptr = (idx.leaf_hi << 32) + idx.leaf_lo
    offset = block_ptr_to_byte(block_ptr, block_size)
    blob_page = get_blob_page(ph, offset, block_size-1)
    Node_block = Struct('index_node_block', Ext4_extent_header,
                        Array(block_size/12, Ext4_extent))

    return Node_block.parse(blob_page)


def get_data_ext4_tree(ph, extent_tree, block_size):
    """TODO: Docstring for get_data_from_ext4_i_block.

    :extent_tree: TODO
    :returns: TODO

    """
    if extent_tree.ext4_extent_header.depth == 0:
        tmp = sorted([(extent.block, get_data_extent(ph, extent, block_size))
                      for index, extent in enumerate(extent_tree.ext4_extent)
                      if index < extent_tree.ext4_extent_header.entries],
                     key=lambda e: e[0])
    else:
        Indexs = Array(extent_tree.ext4_extent_header.max, Ext4_extent_idx)
        indexs = Indexs.parse(Extents.build(extent_tree.ext4_extent))
        tmp = sorted([(idx.block, get_data_ext4_tree(get_data_idx(node_block,
                                                                  block_size),
                                                     block_size))
                      for index, idx in enumerate(indexs)
                      if index < extent_tree.ext4_extent_header.entries],
                     key=lambda e: e[0])

    return reduce(lambda a, b: (0, a[1]+b[1]), tmp)[1]


def download_ext3_file(ph, inode, filename, block_size):
    """TODO: Docstring for get_data_from_inode.

    :inode: TODO
    :options: TODO
    :returns: TODO

    """
    data = ''
    for index, ptr in enumerate(inode.blocks_ptr):
        if ptr == 0:
            break

        offset = block_ptr_to_byte(ptr, block_size)
        blob_page = get_blob_page(ph, offset, block_size)

        if index < 12:
            data = data + blob_page
        elif index == 12:
            data = get_data_indir1(ptr, block_size)
        elif index == 13:
            data = get_data_indir2(ptr, block_size)
        elif index == 14:
            data = get_data_indir3(ptr, block_size)

    return True


def download_ext4_file(ph, inode, filename, block_size):
    """TODO: Docstring for get_data_from_ext4_inode.

    :inode: TODO
    :options: TODO
    :returns: TODO

    """
    data = get_data_ext4_tree(ph, inode.ext4_extent_tree,
                              block_size)[:inode.size]

    with open(filename, 'w') as result:
        result.write(data)

    return True


def block_ptr_to_byte(block_ptr, block_size):
    """TODO: Docstring for block_ptr_to_byte.

    :block_ptr: TODO
    :options: TODO
    :returns: TODO

    """
    return block_size * block_ptr


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


@embed_params(path_list=options.path_list)
def search_dir(ph, inode, index, block_size, filetype, path_list):
    """TODO: Docstring for search_dir.

    :inode: TODO
    :returns: TODO

    """
    data = get_data_ext4_tree(ph, inode.ext4_extent_tree, block_size)

    if filetype:
        Directory = OptionalGreedyRange(Dir_entry2)
        directory = Directory.parse(data)
        if index == len(path_list):
            inodes =  [item.inode for item in directory
                       if os.path.splitext(item.name)[1] == '.log']
        else:
            inodes =  [item.inode for item in directory
                       if item.name == path_list[index]]
    else:
        pass

    print directory
    print len(data)
    print len(directory)
    print inodes

    exit(0)

    return inodes


def parse_partition(partition):
    """TODO: Docstring for parse_partition.

    :partition: TODO
    :options: TODO
    :returns: TODO

    """
    ph = partition.starting_sector * 512
    superblock = get_superblock(ph)
    block_size = parse_KB(superblock)
    group_desc_table = get_group_desc_table(ph, block_size)

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
                             Array(superblock.inodes_per_group, Inode))
        offset = block_ptr_to_byte(group_desc.inode_table_ptr, block_size)
        table_size = superblock.inodes_per_group * superblock.inode_size
        blob_page = get_blob_page(ph, offset, table_size)
        inode_table = Inode_table.parse(blob_page)

        print inode_table.inode[1]
        target = search_dir(ph, inode_table.inode[1], 0,
                            block_size, superblock.feature_incompat.FILETYPE)
        exit(0)

        test_inode = inode_table.inode[422]
        test_inode.flags.EXTENTS and \
                download_ext4_file(test_inode, 'result.txt', block_size) or\
                download_ext3_file(test_inode, 'result.txt', block_size)

        exit(0)


@embed_params(blob_service=options.blob_service,
              container=options.container, vhd=options.vhd)
def parse_image(blob_service, container, vhd):
    """TODO: Docstring for parse_image.

    :options: TODO
    :returns: TODO

    """
    blob_page = blob_service.get_blob(container, vhd, x_ms_range='bytes=0-511')

    mbr = Mbr.parse(blob_page)

    for partition in mbr.mbr_partition_entry:
        pt = partition.partition_type
        if pt == 0x83 or pt == 0x93:
            partition.boot_indicator == 0x80 and \
                    parse_partition(partition)
        else:
            print 'Unsupported \'partition type\' / \'file system\'.'

    return True


def main():
    """TODO: Docstring for main.
    :returns: TODO

    """
    check_vhd_type() == HD_TYPE_FIXED and parse_image()


if __name__ == '__main__':
    main()
