from construct import *


LChar = SLInt8
ULChar = ULInt8
BChar = SBInt8
UBInt8 = UBInt8
SLInt16 = SLInt16
ULInt16 = ULInt16
BShort = SBInt16
UBShort = UBInt16
SLInt32 = SLInt32
ULInt32 = ULInt32
BLong = SBInt32
UBInt32 = UBInt32


Superblock = Struct("superblock",
                ULInt32('inodes_count'),
                ULInt32('blocks_count'),
                ULInt32('reserved_blocks_count'),
                ULInt32('free_blocks_count'),
                ULInt32('free_inodes_count'),
                ULInt32('first_data_block'),
                Enum(ULInt32('log_block_size'), 
                    OneKB = 0,
                    TwoKB = 1,
                    FourKB = 2,
                ),
                SLInt32('log_frag_size'),
                ULInt32('blocks_per_group'),
                ULInt32('frags_per_group'),
                ULInt32('inodes_per_group'),
                ULInt32('mtime'),
                ULInt32('wtime'),
                ULInt16('mnt_count'),
                SLInt16('max_mnt_count'),
                Const(ULInt16('magic'), 0xEF53),
                ULInt16('state'),
                ULInt16('errors'),
                ULInt16('minor_rev_level'),
                ULInt32('lastcheck'),
                ULInt32('checkinterval'),
                ULInt32('creator_os'),
                ULInt32('rev_level'),
                ULInt16('def_resuid'),
                ULInt16('def_resgid'),
                ULInt32('first_ino'),
                ULInt16('inode_size'),
                ULInt16('block_group_nr'),
                ULInt32('feature_compat'),
                Padding(464),
                )


Group_desc = Struct('group_desc',
                    ULInt32('block_bitmap_ptr'),
                    ULInt32('inode_bitmap_ptr'),
                    ULInt32('inode_table_ptr'),
                    ULInt16('free_blocks_count'),
                    ULInt16('free_inodes_count'),
                    ULInt16('used_dirs_count'),
                    ULInt16('pad'),
                    Array(3, ULInt32('reversed')),
                    )


Group_desc_table0 = Struct('group_desc_table0',
                           Array(32, Group_desc),
                          )


Group_desc_table1 = Struct('group_desc_table1',
                           Array(64, Group_desc),
                          )


Group_desc_table2 = Struct('group_desc_table2',
                           Array(128, Group_desc),
                          )


Ext3_inode_128 = Struct("inode",
               FlagsEnum(ULInt16('mode'),
                         IFSOCK =  0xC000,
                         IFLNK  =  0xA000,
                         IFREG  =  0x8000,
                         IFBLK  =  0x6000,
                         IFDIR  =  0x4000,
                         IFCHR  =  0x2000,
                         IFIFO  =  0x1000,
                         ISUID  =  0x0800,
                         ISGID  =  0x0400,
                         ISVTX  =  0x0200,
                         IRUSR  =  0x0100,
                         IWUSR  =  0x0080,
                         IXUSR  =  0x0040,
                         IRGRP  =  0x0020,
                         IWGRP  =  0x0010,
                         IXGRP  =  0x0008,
                         IROTH  =  0x0004,
                         IWOTH  =  0x0002,
                         IXOTH  =  0x0001,
                         ),
               ULInt16('uid'),
               ULInt32('size'),
               ULInt32('atime'),
               ULInt32('ctime'),
               ULInt32('mtime'),
               ULInt32('dtime'),
               ULInt16('gid'),
               ULInt16('links_count'),
               ULInt32('blocks'),
               FlagsEnum(ULInt32('flags'),
                        SECRM        = 0x00000001,
                        UNRM         = 0x00000002,
                        COMPR        = 0x00000004,
                        SYNC         = 0x00000008,
                        IMMUTABLE    = 0x00000010,
                        APPEND       = 0x00000020,
                        NODUMP       = 0x00000040,
                        NOATIME      = 0x00000080,
                        DIRTY        = 0x00000100,
                        COMPRBLK     = 0x00000200,
                        NOCOMPR      = 0x00000400,
                        ECOMPR       = 0x00000800,
                        BTREE        = 0x00001000,
                        INDEX        = 0x00001000,
                        IMAGIC       = 0x00002000,
                        JOURNAL_DATA = 0x00004000,
                        RESERVED     = 0x80000000,
                        ),
               ULInt32('i_reserved1'),
               Array(15, ULInt32('blocks_ptr')),
               Padding(28),
               )


Ext3_inode_256 = Struct("inode",
                        Embed(Ext3_inode_128),
                        Padding(128),
                        )


Ext4_extent_header = Struct('ext4_extent_header',
                            ULInt16('magic'),
                            ULInt16('entries'),
                            ULInt16('max'),
                            ULInt16('depth'),
                            ULInt32('generation'),
                            )


Ext4_extent_idx = Struct('ext4_extent_idx',
                         ULInt32('block'),
                         ULInt32('leaf_lo'),
                         ULInt16('leaf_hi'),
                         ULInt16('unused'),
                         )


Ext4_extent = Struct('ext4_extent',
                     ULInt32('block'),
                     ULInt16('len'),
                     ULInt16('start_hi'),
                     ULInt32('start_lo'),
                     )


Ext4_extent_placeholder = Struct('ext4_extent_placeholder',
                                 Padding(12),
                                 )


Ext4_inode_128 = Struct("inode",
               FlagsEnum(ULInt16('mode'),
                         IFSOCK =  0xC000,
                         IFLNK  =  0xA000,
                         IFREG  =  0x8000,
                         IFBLK  =  0x6000,
                         IFDIR  =  0x4000,
                         IFCHR  =  0x2000,
                         IFIFO  =  0x1000,
                         ISUID  =  0x0800,
                         ISGID  =  0x0400,
                         ISVTX  =  0x0200,
                         IRUSR  =  0x0100,
                         IWUSR  =  0x0080,
                         IXUSR  =  0x0040,
                         IRGRP  =  0x0020,
                         IWGRP  =  0x0010,
                         IXGRP  =  0x0008,
                         IROTH  =  0x0004,
                         IWOTH  =  0x0002,
                         IXOTH  =  0x0001,
                         ),
               ULInt16('uid'),
               ULInt32('size'),
               ULInt32('atime'),
               ULInt32('ctime'),
               ULInt32('mtime'),
               ULInt32('dtime'),
               ULInt16('gid'),
               ULInt16('links_count'),
               ULInt32('blocks'),
               FlagsEnum(ULInt32('flags'),
                        SECRM            = 0x00000001,
                        UNRM             = 0x00000002,
                        COMPR            = 0x00000004,
                        SYNC             = 0x00000008,
                        IMMUTABLE        = 0x00000010,
                        APPEND           = 0x00000020,
                        NODUMP           = 0x00000040,
                        NOATIME          = 0x00000080,
                        DIRTY            = 0x00000100,
                        COMPRBLK         = 0x00000200,
                        NOCOMPR          = 0x00000400,
                        ECOMPR           = 0x00000800,
                        BTREE            = 0x00001000,
                        INDEX            = 0x00001000,
                        IMAGIC           = 0x00002000,
                        JOURNAL_DATA     = 0x00004000,
                        NOTAIL           = 0x8000,
                        DIRSYNC          = 0x10000,
                        TOPDIR           = 0x20000,
                        HUGE_FILE        = 0x40000,
                        EXTENTS          = 0x80000,
                        EA_INODE         = 0x200000,
                        EOFBLOCKS        = 0x400000,
                        SNAPFILE         = 0x01000000,
                        SNAPFILE_DELETED = 0x04000000,
                        SNAPFILE_SHRUNK  = 0x08000000,
                        INLINE_DATA      = 0x10000000,
                        USER1            = 0x4BDFFF,
                        USER2            = 0x4B80FF,
                        RESERVED         = 0x80000000,
                        ),
               ULInt32('i_reserved1'),
               Ext4_extent_header,
               Array(4, Ext4_extent),
               Padding(28),
               )


Ext4_inode_256 = Struct("inode",
                        Embed(Ext4_inode_128),
                        Padding(128),
                        )


# special inodes
EXT2_BAD_INO = 1
EXT2_ROOT_INO = 2
EXT2_ACL_IDX_INO = 3
EXT2_ACL_DATA_INO = 4
EXT2_BOOT_LOADER_INO = 5
EXT2_UNDEL_DIR_INO = 6
EXT2_FIRST_INO = 11 


Dir_entry = Struct("dir_entry",
                   ULInt32("inode"),
                   ULInt16("rec_length"),
                   ULInt8("name_length"),
                   ULInt8("file_type"),
                   Field("name", lambda ctx: ctx["name_length"]),
                   )


Mbr_pe = Struct('mbr_partition_entry',
                ULInt8('boot_indicator'),
                Padding(3),
                ULInt8('partition_type'),
                Padding(3),
                ULInt32('starting_sector'),
                ULInt32('total_sector'),
                )


Mbr = Struct('mbr',
             Array(446, SBInt8('bootstrapper')),
             Array(4, Mbr_pe),
             ULInt8('signature1'),
             ULInt8('signature2'),
             )


Hd_ftr = Struct("hd_ftr",
                Array(8, SBInt8('cookie')),
                UBInt32('feature'),
                UBInt32('ff_version'),
                UBInt64('data_offset'),
                UBInt32('timestamp'),
                Array(4, SBInt8('crtr_app')),
                UBInt32('crtr_ver'),
                UBInt32('crtr_os'),
                UBInt64('orig_size'),
                UBInt64('curr_size'),
                UBInt32('geometry'),
                UBInt32('type'),
                UBInt32('checksum'),
                SBInt8('uuid'),
                SBInt8('saved'),
                SBInt8('hidden'),
                Array(426, SBInt8('reserved')),
                )

