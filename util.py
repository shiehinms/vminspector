import sys
from time import time
from functools import wraps
from os import unlink, makedirs
from os.path import isdir, exists
from optparse import OptionParser
from azure.storage import BlobService


VERSION = 'v1.0.0'
USAGE = 'usage: python %prog -n account_name -k account_key -c container'
'-v vhd -p path -e extension'


def get_options():
    """TODO: Docstring for get_options.
    :returns: TODO
    """
    parser = OptionParser(usage=USAGE, version=VERSION)

    parser.add_option('-p', '--path', action='store', type='string',
                      help='Searching path', dest='path', default='/')
    parser.add_option('-n', '--name', action='store', type='string',
                      help='Account Name', dest='account_name', default='')
    parser.add_option('-k', '--key', action='store', type='string',
                      help='Account Key', dest='account_key', default='')
    parser.add_option('-c', '--container', action='store', type='string',
                      help='Container Name', dest='container', default='vhds')
    parser.add_option('-v', '--vhd', action='store', type='string',
                      help='VHD File', dest='vhd', default='')
    parser.add_option('-b', '--hostbase', action='store', type='string',
                      help='Host Base', dest='host_base',
                      default='.blob.core.windows.net')
    parser.add_option('-t', '--type', action='store', type='int',
                      help='EXT2/3/4', dest='type', default='4')
    parser.add_option('-e', '--extension', action='store', type='string',
                      help='Extension', dest='extension', default='.log')

    (options, args) = parser.parse_args()
    len(sys.argv) == 1 and exit(parser.print_help())
    options.blob_service = BlobService(options.account_name,
                                       options.account_key,
                                       host_base=options.host_base)
    options.path_list = split_path(options.path)

    return (options, args)


def log_time(fn):
    """TODO: Docstring for log_time.

    :fn: TODO
    :returns: TODO

    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        start_time = time()

        result = fn(*args, **kwargs)

        print '%s -> Time used : %d\n' % (fn.__name__, time() - start_time)

        return result

    return wrapper


def embed_params(**kwargs):
    """TODO: Docstring for embed_params.

    :**kwargs: TODO
    :returns: TODO

    """
    def decorator(fn):
        """TODO: Docstring for decorator.

        :fn: TODO
        :returns: TODO

        """
        @wraps(fn)
        def wrapper(*arg):
            """TODO: Docstring for wrapper.

            :*arg: TODO
            :returns: TODO

            """
            return fn(*arg, **kwargs)

        return wrapper

    return decorator


def split_path(path):
    """TODO: Docstring for split_path.

    :path: TODO
    :returns: TODO

    """
    item = [x for x in path.split('/') if x != '']

    return item


def init_dir(path):
    """TODO: Docstring for init_dir.

    :path: TODO
    :returns: TODO

    """
    if not isdir(path):
        exists(path) and unlink(path)
        makedirs(path)
