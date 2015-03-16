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


superblock = Struct("superblock",
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
                Padding(235 * 4),
                )


mbr_pe = Struct('mbr_partition_entry',
                ULInt8('Boot_Indicator'),
                Padding(3),
                ULInt8('Partition_Type'),
                Padding(3),
                ULInt32('Starting_Sector'),
                ULInt32('Total_Sector'),
                )


mbr = Struct('MBR',
             Array(446, SBInt8('Bootstrapper')),
             Array(4, mbr_pe),
             ULInt8('signature1'),
             ULInt8('signature2'),
             )


hd_ftr = Struct("hd_ftr",
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

