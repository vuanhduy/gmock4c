#!/usr/bin/python3
import os
import platform
import sys
import optparse
import logging

import clang.cindex as Clang


def setup(args):
    default_libclang_path = ''
    if platform.system() == 'Linux':
        logging.info("Platform: Linux")
        default_libclang_path = "/usr/lib/llvm-6.0/lib/libclang.so"
    elif platform.system() == 'Darwin':
        logging.info("Platform: MacOS")
        default_libclang_path = \
            "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/libclang.dylib"
    else:
        logging.critical("Platform: Not supported")
        default_libclang_path = ""
        exit(-1)

    default_config = "gmock.conf"
    default_output = os.getcwd()

    parser = optparse.OptionParser(usage="usage: %prog [options] file/dir")
    parser.add_option("-c", "--config", dest="config_file", default=default_config,
                      help="config FILE (default='gmock.conf')", metavar="FILE")
    parser.add_option("-o", "--output", dest="output_path", default=default_output,
                      help="path for storing generated files", metavar="DIR")
    parser.add_option("-l", "--libclang", dest="libclang_path", default=default_libclang_path,
                      help="path to libclang.so (default=None)", metavar="LIBCLANG")
    (options, args) = parser.parse_args(args)

    if len(args) == 1:
        parser.print_help()
        exit(1)

    Clang.Config.set_library_file(options.libclang_path)

    return options


def setup_logger():
    # create logger with 'spam_application'
    logger = logging.getLogger('gmock4c_application')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('gmock4c.log')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)


if __name__ == "__main__":
    options = setup(sys.argv)
    setup_logger()

    sys.path.append(os.path.dirname(__file__))
    import gmock4c.generator as GMock4C

    gen = GMock4C.Generator(options.config_file, sys.argv[1])
    gen.parse()
    gen.write_mock_header(options.output_path)
    gen.write_mock_src(options.output_path)
    gen.write_stubs_src(options.output_path)
