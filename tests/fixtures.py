import os
import platform
import logging
import pytest
import clang.cindex as Clang
import gmock4c.config as GMockConfig


def setup_clang():
    libclang_path = ""
    if platform.system() == 'Linux':
        libclang_path = "/usr/lib/llvm-6.0/lib/libclang.so"
    elif platform.system() == 'Darwin':
        libclang_path = \
            "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/libclang.dylib"

    Clang.Config.loaded = False
    Clang.Config.set_library_file(libclang_path)
    logging.info("libclang_path: " + libclang_path)

    header_file_name = 'test_header.hpp'
    header_file_path = os.getcwd() + "/" + header_file_name
    logging.debug("header file: " + header_file_path)

    parsing_options = Clang.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES \
                      | Clang.TranslationUnit.PARSE_INCOMPLETE \
                      | Clang.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD

    parsing_args = "-x c++ --std=c++11".split()
    translation_unit = Clang.Index.create().parse(path=header_file_path,
                                                  args=parsing_args, options=parsing_options)

    return translation_unit


@pytest.fixture(scope='module', autouse=True)
def translation_unit_cursor():
    translation_unit = setup_clang()
    return translation_unit.cursor


@pytest.fixture(scope='module', autouse=True)
def function_cursors():
    def get_cursors(_node, _cursors):
        # if _node.kind != Clang.CursorKind.TRANSLATION_UNIT \
        #         and (_node.location.file is None or not _node.location.file.name.endswith(header_file_name)):
        #     return

        if _node.kind == Clang.CursorKind.FUNCTION_DECL:
            _cursors.append(_node)
            return

        for child in [c for c in _node.get_children()]:
            get_cursors(child, _cursors)

    translation_unit = setup_clang()
    cursors = []
    get_cursors(translation_unit.cursor, cursors)
    return cursors


@pytest.fixture(scope='module', autouse=True)
def gmock4c_config():
    config_file_name = 'test.conf'
    config_file_path = os.getcwd() + "/" + config_file_name
    return GMockConfig.Config(config_file_path)
