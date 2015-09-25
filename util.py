import sys
import requests
from time import time
from functools import wraps
from urlparse import urlparse
from os import unlink, makedirs
from os.path import isdir, exists
from optparse import OptionParser
from azure.storage import BlobService


VERSION = 'v1.0.0'
USAGE = 'usage: python %prog -u url -k account_key -p path -f filename\n' \
'*(Required field)'


def print_warning():
    """TODO: Docstring for print_warning.
    :returns: TODO

    """
    print 'Extension and Filename are mutually exclusive.'
    return 1


def get_options():
    """TODO: Docstring for get_options.
    :returns: TODO
    """
    parser = OptionParser(usage=USAGE, version=VERSION)

    parser.add_option('-u', '--url', action='store', type='string',
                      help='Url of the vhd *', dest='url', default='')
    parser.add_option('-k', '--key', action='store', type='string',
                      help='Account Key', dest='account_key', default='')
    parser.add_option('-f', '--file', action='store', type='string',
                      help='File name', dest='filename', default='')
    parser.add_option('-p', '--path', action='store', type='string',
                      help='Searching path *', dest='path', default='/')
    parser.add_option('-e', '--extension', action='store', type='string',
                      help='Extension', dest='extension', default='')
    parser.add_option('-t', '--type', action='store', type='int',
                      help='EXT2/3/4; 2,3,4', dest='type', default='4')
    parser.add_option('--ls', action='store_true',
                      help='List the dir', dest='ls', default=False)

    (options, args) = parser.parse_args()
    len(sys.argv) == 1 and exit(parser.print_help())
    options.extension and options.filename and exit(print_warning())
    tmp = urlparse(options.url)
    options.account_name = tmp.netloc.split('.')[0]
    options.container = tmp.path.split('/')[1]
    options.vhd = tmp.path.split('/')[2]
    options.host_base = tmp.netloc[tmp.netloc.find('.'):]

    if options.account_key:
        options.blob_service = BlobService(options.account_name,
                                           options.account_key,
                                           host_base=options.host_base)
        options.blob_service._httpclient.request_session = requests.Session()
    else:
        options.blob_service = None

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
        @wraps(fn)
        def wrapper(*arg):

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
