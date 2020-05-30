import os
import glob
import logging

import clang.cindex as Clang
import gmock4c.config as GMockConfig
import gmock4c.ast as GMockAST
import gmock4c.stub as GMockStub
import gmock4c.mock as GMock


logger = logging.getLogger('gmock4c_application')


class Generator:
    def __init__(self, config_file, input_path):
        self._config_file = config_file
        self._input_path = input_path
        self._stubs_list = []
        self._config = GMockConfig.Config(config_file)
        self._mock = GMock.Mock(self._config)

    def parse(self):
        # A recursive function to parse all the nodes.
        def parse_node(node, stubs):
            # NOTE: the parsed header was precompiled (i.e., it includes the content of files of '#include', so we need
            # to filter and process only functions declared inside the current header)
            if node.kind != Clang.CursorKind.TRANSLATION_UNIT \
                    and (node.location.file is None or not node.location.file.name.endswith(f)):
                return

            if node.kind == Clang.CursorKind.FUNCTION_DECL:
                func = GMockAST.Function(node)
                stub_function = GMockStub.StubFunction(func, self._config)
                mock_method = GMock.MockMethod(func)
                self._mock.append_mock_method(str(mock_method))
                stubs.append_stub_function(stub_function)
                return

            for child in [c for c in node.get_children()]:
                parse_node(child, stubs)

        files = []
        if os.path.isfile(self._input_path):
            files.append(self._input_path)
        else:
            files.extend(glob.glob(self._input_path + "/**/*.h*", recursive=True))

        # Utilize clang to parse each file
        for f in files:
            logger.info("Processing " + f)
            print("Processing ", f)
            if f == self._input_path:
                self._mock.add_header(os.path.basename(f))
            else:
                self._mock.add_header(os.path.relpath(f, self._input_path))

            stubs_file = GMockStub.StubsFile(self._config, self._input_path, self._config.header_output_path)
            parsing_options = Clang.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES \
                              | Clang.TranslationUnit.PARSE_INCOMPLETE \
                              | Clang.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD

            parsing_args = self._config.parsing_args.split()

            translation_unit = Clang.Index.create().parse(path=f, args=parsing_args, options=parsing_options)
            parse_node(translation_unit.cursor, stubs_file)
            self._stubs_list.append(stubs_file)

    def write_mock_header(self, path="./"):
        self._mock.write_header(path)

    def write_mock_src(self, path="./"):
        self._mock.write_src(path)

    def write_stubs_src(self, path="./"):
        for s in self._stubs_list:
            s.write(path)
