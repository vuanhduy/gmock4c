#!/usr/bin/python3

import os
import sys
import re
from glob import glob
from optparse import OptionParser

from clang.cindex import Index, TranslationUnit, CursorKind, TypeKind, Config

# TODO: detect type parsing error. When clang cannot parse a type (of a function and parameter), it automatically casts
#  it to int. How can we detect this situation and inform users to update their parsing_args?


class MockMethod:
    template = """MOCK_METHOD%(num)d( %(method_name)s, %(result_type)s( %(parameters_with_types)s ) );"""

    def __init__(self, cursor):
        self._result_type = cursor.result_type.spelling
        self._method_name = cursor.spelling
        self._is_variadic = cursor.type.is_function_variadic()
        self._parameters_with_types = [arg.type.spelling + ' ' + arg.spelling for arg in cursor.get_arguments()]

    @property
    def result_type(self):
        return self._result_type

    @property
    def method_name(self):
        return self._method_name

    @property
    def parameters_with_types(self):
        return self._parameters_with_types

    def __str__(self):
        # NOTE: we cannot mock variadic functions
        if self._is_variadic:
            return ''

        method = MockMethod.template % {'num': len(self._parameters_with_types), 'method_name': self._method_name,
                                        'result_type': self._result_type,
                                        'parameters_with_types': ', '.join(self._parameters_with_types),
                                        }
        return method.replace("(  )", "()").replace(' *(', '*(').replace('* ', '*')


class Mock:
    def __init__(self, name_space, mock_name, header_template, src_template, header_output_path):
        self._mock_name = mock_name + "Mock"
        self._name_space = name_space
        self._header_template = header_template
        self._src_template = src_template
        self._header_output_path = header_output_path
        self._mock_instance = mock_name.lower() + "mock"
        self._guard = "__" + mock_name.upper() + "_MOCK_HPP_"
        self._mock_header = mock_name.lower() + "_mock.hpp"
        self._mock_src = mock_name.lower() + "_mock.cpp"
        self._mock_methods = []
        self._headers = []

    def add_header(self, header_file):
        inc = """#include "%s" """ % header_file
        self._headers.append(inc)

    def add_mock_method(self, method):
        self._mock_methods.append(method)

    def write_header(self, path="./"):
        headers = "\n".join(self._headers)
        methods = "\n    ".join(self._mock_methods)
        content = self._header_template % {'guard': self._guard, 'name_space': self._name_space,
                                           'mock_name': self._mock_name, 'mock_instance': self._mock_instance,
                                           'mock_methods': methods, 'header_files': headers,
                                           }
        # TODO: Remove this hard-code
        real_path = path + '/inc/mocks/' + self._header_output_path
        if not os.path.exists(real_path):
            os.makedirs(real_path)

        with open(real_path + "/" + self._mock_header, "w") as file:
            file.write(content)

    def write_src(self, path="./"):
        content = self._src_template % {'name_space': self._name_space, 'mock_name': self._mock_name,
                                        'mock_instance': self._mock_instance, 'mock_header': self._mock_header,
                                        'header_output_path': self._header_output_path,
                                        }

        # TODO: Remove this hard-code
        real_path = path + '/src'
        if not os.path.exists(real_path):
            os.makedirs(real_path)

        with open(real_path + "/" + self._mock_src, "w") as file:
            file.write(content)


class StubFunction:
    variadic_function_template = """\n%(result_type)s %(function_name)s( %(parameters_with_types)s ) {}\n"""

    def __init__(self, cursor, mock_name, template):
        self._mock_name = mock_name + "Mock"
        self._template = template
        self._result_type = cursor.result_type.spelling
        self._is_returnable = False if cursor.result_type.kind == TypeKind.VOID else True
        self._name = cursor.spelling
        self._is_variadic = cursor.type.is_function_variadic()
        self._parameters = []
        self._parameters_with_types = []
        for arg in [a for a in cursor.get_arguments()]:
            self._parameters.append(arg.spelling)
            self._parameters_with_types.append(arg.type.spelling + ' ' + arg.spelling)

    @property
    def result_type(self):
        return self._result_type

    @property
    def name(self):
        return self._name

    @property
    def parameters(self):
        return self._parameters

    @property
    def parameters_with_types(self):
        return self._parameters_with_types

    @property
    def is_returnable(self):
        return self._is_returnable

    @property
    def is_variadic(self):
        return self._is_variadic

    def __str__(self):
        function = ''
        if self.is_variadic:
            function = StubFunction.variadic_function_template % {
                'result_type': self.result_type, 'function_name': self.name,
                'parameters_with_types': self.parameters_with_types,
            }
        else:
            function = self._template % {'result_type': self.result_type, 'function_name': self.name,
                                         'parameters_with_types': ', '.join(self.parameters_with_types),
                                         'mock_name': self._mock_name, 'parameters': ', '.join(self.parameters),
                                         'return': 'return' if self.is_returnable else '',
                                         }

        return function.replace("(  )", "()").replace(" * (", "* (").replace("* ", "*")


class StubsFile:
    variadic_function_template = """\n%(result_type)s %(function_name)s( %(parameters_with_types)s ) {}\n"""

    def __init__(self, name_space, mock_name, file_template, function_template, header_file, header_root_dir,
                 header_output_path):
        self._name_space = name_space
        self._mock_name = mock_name + 'Mock'
        self._mock_header = mock_name.lower() + "_mock.hpp"
        self._file_template = file_template
        self._function_template = function_template
        self._header_output_path = header_output_path
        if header_file == header_root_dir:
            self._header_file = os.path.basename(header_file)
        else:
            self._header_file = os.path.relpath(header_file, header_root_dir)
        self._functions = []

    def append_stub_function(self, stub):
        self._functions.append(stub)

    def write(self, path='./'):
        if len(self._functions) == 0:
            return

        stubs = ""
        for f in self._functions:
            if f.is_variadic:
                print("(!!!)", f.name, "is a variadic function, so it should be manged manually.")
            stubs += str(f)

        content = self._file_template % {'stubs_header': self._header_file, 'mock_header': self._mock_header,
                                         'name_space': self._name_space, 'stubs': stubs, 'mock_name': self._mock_name,
                                         'header_output_path': self._header_output_path,
                                         }

        stub_file_name = re.sub(r"\.hpp|\.h", "_stubs.cpp", os.path.basename(self._header_file))

        # TODO: Remove this hard-code
        real_path = path + '/src'
        if not os.path.exists(real_path):
            os.makedirs(real_path)

        with open(real_path + "/" + stub_file_name, 'w') as file:
            file.write(content)


class Generator:
    def __init__(self, config_file, input_path):
        self._config_file = config_file
        self._input_path = input_path
        self._stubs_list = []
        self._config = {}

        with open(self._config_file, 'r') as file:
            exec(file.read(), self._config)
            self._mock_name = self._config['mock_name']
            self._name_space = self._config['name_space']
            self._mock_header_template = self._config['mock_header_template']
            self._mock_cpp_template = self._config['mock_cpp_template']
            self._stubs_file_template = self._config['stubs_file_template']
            self._stub_function_template = self._config['stub_function_template']
            self._header_output_path = self._config['header_output_path']
            self._mock = Mock(self._name_space, self._mock_name, self._mock_header_template, self._mock_cpp_template,
                              self._header_output_path)
            self._parsing_args = self._config['parsing_args']

    def parse(self):
        # A recursive function to parse all the nodes.
        def parse_node(node, stubs):
            # NOTE: the parsed header was precompiled (i.e., it includes the content of files of '#include', so we need
            # to filter and process only functions declared inside the current header)
            if node.kind != CursorKind.TRANSLATION_UNIT \
                    and (node.location.file is None or not node.location.file.name.endswith(f)):
                return

            if node.kind == CursorKind.FUNCTION_DECL:
                stub_function = StubFunction(node, self._mock_name, self._stub_function_template)
                mock_method = MockMethod(node)
                self._mock.add_mock_method(str(mock_method))
                stubs.append_stub_function(stub_function)
                return

            for child in [c for c in node.get_children()]:
                parse_node(child, stubs)

        files = []
        if os.path.isfile(self._input_path):
            files.append(self._input_path)
        else:
            files.extend(glob(self._input_path + "/**/*.h*", recursive=True))

        # Utilize clang to parse each file
        for f in files:
            print("Processing ", f)
            if f == self._input_path:
                self._mock.add_header(os.path.basename(f))
            else:
                self._mock.add_header(os.path.relpath(f, self._input_path))

            stubs_file = StubsFile(self._name_space, self._mock_name, self._stubs_file_template,
                                   self._stub_function_template, f, self._input_path, self._header_output_path)
            parsing_options = TranslationUnit.PARSE_SKIP_FUNCTION_BODIES \
                              | TranslationUnit.PARSE_INCOMPLETE \
                              | TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD

            parsing_args = self._parsing_args.split()
            if os.path.isdir(self._input_path):
                parsing_args.append("-I " + self._input_path)

            translation_unit = Index.create().parse(path=f, args=parsing_args, options=parsing_options)
            parse_node(translation_unit.cursor, stubs_file)
            self._stubs_list.append(stubs_file)

    def write_mock_header(self, path="./"):
        self._mock.write_header(path)

    def write_mock_src(self, path="./"):
        self._mock.write_src(path)

    def write_stubs_src(self, path="./"):
        for s in self._stubs_list:
            s.write(path)


def main(args):
    # TODO: this is for testing only
    Config.set_library_file(
        "/usr/lib/llvm-6.0/lib/libclang.so")
    # "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/libclang.dylib")

    sys.path.append(os.path.dirname(__file__))
    default_config = "gmock.conf"
    default_output = os.getcwd()

    parser = OptionParser(usage="usage: %prog [options] file/dir")
    parser.add_option("-c", "--config", dest="config_file", default=default_config,
                      help="config FILE (default='gmock.conf')", metavar="FILE")
    parser.add_option("-o", "--output", dest="output_path", default=default_output,
                      help="path for storing generated files", metavar="DIR")
    parser.add_option("-l", "--libclang", dest="libclang_path", default=None, help="path to libclang.so (default=None)",
                      metavar="LIBCLANG")
    (options, args) = parser.parse_args(args)

    if len(args) == 1:
        parser.print_help()
        exit(1)

    if options.libclang_path:
        Config.set_library_file(options.libclang)

    gen = Generator(options.config_file, args[1])
    gen.parse()
    gen.write_mock_header(options.output_path)
    gen.write_mock_src(options.output_path)
    gen.write_stubs_src(options.output_path)


if __name__ == "__main__":
    main(sys.argv)
