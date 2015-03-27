Dx_entry = Struct('dx_entry',
                  ULInt32('hash'),
                  ULInt32('block'),
                  )


Dx_root = Struct('dx_root',
                 ULInt32('dot.inode'),
                 ULInt16('dot.rec_len'),
                 ULInt8('dot.name_len'),
                 ULInt8('dot.file_type'),
                 Array(4, ULInt8('dot.name')),
                 ULInt32('dotdot.inode'),
                 ULInt16('dotdot.rec_len'),
                 ULInt8('dotdot.name_len'),
                 ULInt8('dotdot.file_type'),
                 Array(4, ULInt8('dotdot.name')),
                 ULInt32('dx_root_info.reserved_zero'),
                 Enum(ULInt8('dx_root_info.hash_version'),
                      Legacy            = 0x0,
                      Half_MD4          = 0x1,
                      Tea               = 0x2,
                      Legacy_unsigned   = 0x3,
                      Half_MD4_unsigned = 0x4,
                      Tea_unsigned      = 0x5,
                      ),
                 ULInt8('dx_root_info.info_length'),
                 ULInt8('dx_root_info.indirect_levels'),
                 ULInt8('dx_root_info.unused_flags'),
                 ULInt16('limit'),
                 ULInt16('count'),
                 ULInt32('block'),
                 OptionalGreedyRange(Dx_entry),
                 )


Dx_node = Struct('dx_node',
                 ULInt32('fake.inode'),
                 ULInt16('fake.rec_len'),
                 ULInt8('name_len'),
                 ULInt8('file_type'),
                 ULInt16('limit'),
                 ULInt16('count'),
                 ULInt32('block'),
                 OptionalGreedyRange(Dx_entry),
                 )


