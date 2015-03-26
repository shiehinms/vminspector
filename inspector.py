#!/usr/bin/env python
# encoding: utf-8


from util import *
from formats import *
from math import ceil
from construct import *
from operator import add
from os.path import splitext, join


PTR_TYPE = {
        0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0, 11:0,
        12:1, 13:2, 14:3,
        }
(options, args) = get_options()


@embed_params(blob_service=options.blob_service,
              container=options.container, vhd=options.vhd)
def check_vhd_type(blob_service, container, vhd):
    """TODO: Docstring for check_vhd_type.

    :properties: TODO
    :returns: TODO

    """
    properties = blob_service.get_blob_properties(container, vhd)
    rangerange = 'bytes=%d-%d' % (int(properties['content-length'])-512,
                                  int(properties['content-length'])-1)
    blob_page = blob_service.get_blob(container, vhd, x_ms_range=rangerange)

    return Hd_ftr.parse(blob_page).type


def get_superblock(ph):
    """TODO: Docstring for get_superblock.

    :partition: TODO
    :returns: TODO

    """
    return Superblock.parse(get_blob_page(ph, 1024, 1024))


def get_group_desc_table(ph, block_size):
    """TODO: Docstring for get_group_desc_table.

    :returns: TODO

    """
    offset = int(ceil(2048.0 / block_size) * block_size)
    Group_desc_table = Struct('group_desc_table',
                              Array(block_size/32, Group_desc))

    return Group_desc_table.parse(get_blob_page(ph, offset, block_size))


@embed_params(blob_service=options.blob_service,
              container=options.container, vhd=options.vhd)
def get_blob_page(ph, offset, page_size,
                  blob_service, container, vhd):
    """TODO: Docstring for get_blob_page.

    :offset: TODO
    :page_size: TODO
    :returns: TODO

    """
    rangerange = 'bytes=%d-%d' % (ph+offset, ph+offset+page_size-1)

    return blob_service.get_blob(container, vhd, x_ms_range=rangerange)


def get_data_ptr(ph, block_size, ptr, ptr_type):
    """TODO: Docstring for get_data_indir1.

    :indir_ptr: TODO
    :returns: TODO

    """
    offset = block_ptr_to_byte(ptr, block_size)
    blob_page = get_blob_page(ph, offset, block_size)

    if ptr_type == 0:
        return blob_page

    Indir_ptr_list = Struct('indir_ptr_list',
                            Array(block_size/4, ULInt32('indir_ptr')))
    parsed = Indir_ptr_list.parse(blob_page)

    data = reduce(add, (get_data_ptr(ph, block_size, ptr, ptr_type-1)
                        for ptr in parsed.indir_ptr_list))

    return data


def get_data_extent(ph, extent, block_size):
    """TODO: Docstring for get_data_extent.

    :extent: TODO
    :returns: TODO

    """
    block_ptr = (extent.start_hi << 32) + extent.start_lo
    offset = block_ptr_to_byte(block_ptr, block_size)

    return get_blob_page(ph, offset, extent.len*block_size)


def get_data_idx(ph, idx, block_size):
    """TODO: Docstring for get_data_idx.

    :idx: TODO
    :returns: TODO

    """
    block_ptr = (idx.leaf_hi << 32) + idx.leaf_lo
    offset = block_ptr_to_byte(block_ptr, block_size)
    Node_block = Struct('index_node_block', Ext4_extent_header,
                        Array(block_size/12-1, Ext4_extent))

    return Node_block.parse(get_blob_page(ph, offset, block_size))


def get_data_ext4_tree(ph, extent_tree, block_size):
    """TODO: Docstring for get_data_from_ext4_i_block.

    :extent_tree: TODO
    :returns: TODO

    """
    if extent_tree.ext4_extent_header.depth == 0:
        tmp = sorted(((extent.block, get_data_extent(ph, extent, block_size))
                      for index, extent in enumerate(extent_tree.ext4_extent)
                      if index < extent_tree.ext4_extent_header.entries),
                     key=lambda e: e[0])
    else:
        Indexs = Array(extent_tree.ext4_extent_header.max, Ext4_extent_idx)
        indexs = Indexs.parse(Ext4_extents.build(extent_tree.ext4_extent))
        tmp = sorted(((idx.block,
                       get_data_ext4_tree(ph, get_data_idx(ph, idx,
                                                           block_size),
                                          block_size))
                      for index, idx in enumerate(indexs)
                      if index < extent_tree.ext4_extent_header.entries),
                     key=lambda e: e[0])

    return reduce(lambda a, b: (0, ''.join([a[1], b[1]])), tmp, (0, ''))[1]


def download_ext3_file(ph, inode, filename, block_size):
    """TODO: Docstring for download_ext3_file.

    :inode: TODO
    :returns: TODO

    """
    data = ''.join((get_data_ptr(ph, block_size, ptr, PTR_TYPE[index])
                    for index, ptr in enumerate(inode.blocks_ptr) if ptr != 0))

    with open(''.join(['./', vhd, join(path, filename)]), 'w') as result:
        result.write(data)

    return True


@embed_params(vhd=options.vhd, path=options.path)
def download_ext4_file(ph, inode, filename, block_size, vhd, path):
    """TODO: Docstring for download_ext4_file.

    :returns: TODO

    """
    data = get_data_ext4_tree(ph, inode.ext4_extent_tree,
                              block_size)[:inode.size]

    with open(''.join(['./', vhd, join(path, filename)]), 'w') as result:
        result.write(data)

    return True


def block_ptr_to_byte(block_ptr, block_size):
    """TODO: Docstring for block_ptr_to_byte.

    :block_ptr: TODO
    :returns: TODO

    """
    return block_size * block_ptr


def parse_KB(superblock):
    """TODO: Docstring for parse_KB.

    :superblock: TODO
    :returns: TODO

    """
    KB_INT = {
            'OneKB':1024,
            'TwoKB':2048,
            'FourKB':4096,
            }

    return KB_INT[superblock.log_block_size]


@embed_params(path_list=options.path_list, extension=options.extension)
def search_i(ph, inode, index, block_size,
               filetype, get_inode, path_list, extension):
    """TODO: Docstring for search_i.

    :returns: TODO

    """
    data = get_data_ext4_tree(ph, inode.ext4_extent_tree, block_size)

    if filetype:
        directory = Dirs2.parse(data)
        if index == len(path_list):
            return [(get_inode(item.inode), item.name) for item in directory
                    if splitext(item.name)[1] == extension]
        else:
            inodes = [search_i(ph, get_inode(item.inode),
                                 index+1, block_size, filetype, get_inode)
                      for item in directory if item.name == path_list[index]]
            if inodes:
                return inodes[0]
            else:
                return []
    else:
        pass # pending.


def parse_partition(partition):
    """TODO: Docstring for parse_partition.

    :partition: TODO
    :returns: TODO

    """
    ph = partition.starting_sector * 512
    superblock = get_superblock(ph)
    block_size = parse_KB(superblock)
    inodes_per_group = superblock.inodes_per_group
    group_desc_table = get_group_desc_table(ph, block_size)
    inode_type = {
            128:{4:Ext4_inode_128, 3:Ext3_inode_128,},
            256:{4:Ext4_inode_256, 3:Ext3_inode_256,},
            }

    Inode = inode_type[superblock.inode_size][options.type]
    Inode_table = Struct('inode_table', Array(inodes_per_group, Inode))
    table_size = inodes_per_group * superblock.inode_size

    def get_inode(num):
        """TODO: Docstring for get_inode.

        :num: TODO
        :group_desc_table: TODO
        :returns: TODO

        """
        block_group = (num-1) / inodes_per_group
        local_index = (num-1) % inodes_per_group

        group_desc = group_desc_table.group_desc[block_group]
        offset = block_ptr_to_byte(group_desc.inode_table_ptr, block_size)
        blob_page = get_blob_page(ph, offset, table_size)
        inode_table = Inode_table.parse(blob_page)
        inode = inode_table.inode[local_index]

        return inode

    root = get_inode(2)
    target = [(inode, name) for inode, name
              in search_i(ph, root, 0, block_size,
                          superblock.feature_incompat.FILETYPE, get_inode)]

    len1 = len([download_ext4_file(ph, inode, name, block_size)
                for inode, name in target if inode.flags.EXTENTS is True])
    len2 = len([download_ext3_file(ph, inode, name, block_size)
                for inode, name in target if inode.flags.EXTENTS is False])
    print '%d ext4 files + %d ext2/3 files have been downloaded.' % (len1, len2)

    return True


def part_type(pt):
    """TODO: Docstring for part_type.

    :pt: TODO
    :returns: TODO

    """
    partition_type = {
            0x00: 'Empty',
            }

    return partition_type[pt]


def parse_image():
    """TODO: Docstring for parse_image.

    :returns: TODO

    """
    mbr = Mbr.parse(get_blob_page(0, 0, 512))

    for partition in mbr.mbr_partition_entry:
        pt = partition.partition_type
        if pt == 0x83 or pt == 0x93:
            partition.boot_indicator == 0x80 and parse_partition(partition)
        else:
            print 'Unsupported \'partition type\' / \'file system\'. \
                    status : %d' % (pt)

    return True


if __name__ == '__main__':
    if options.path[0] != '/':
        print 'Support only absolute path.'
        exit(0)

    HD_TYPE_FIXED = 2
    HD_TYPE_DYNAMIC = 3

    init_dir(''.join(['./', options.vhd, options.path]))
    check_vhd_type() == HD_TYPE_FIXED and parse_image() or \
            check_vhd_type() == HD_TYPE_DYNAMIC and True
