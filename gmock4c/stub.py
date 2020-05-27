import os
import re
import logging


class StubFunction:
    def __init__(self, func, config):
        logging.info('Creating stub for ' + func.name)
        self._func = func
        self._config = config
        self._is_returnable = False if self._func.result_type == 'void' else True

    # @property
    # def result_type(self):
    #     return self._result_type

    @property
    def name(self):
        return self._func.name

    # @property
    # def parameters(self):
    #     return self._parameters

    # @property
    # def parameters_with_types(self):
    #     return self._parameters_with_types

    # @property
    # def is_returnable(self):
    #     return self._is_returnable

    @property
    def is_variadic(self):
        return self._func.is_variadic

    def __str__(self):
        function = ''
        if self._func.is_variadic:
            function = "\n" + str(self._func) + " {\n}\n"
        else:
            function = self._config.stub_function_template % {
                'result_type': self._func.result_type, 'function_name': self._func.name,
                'parameters_with_types': ', '.join([str(arg) for arg in self._func.arguments]),
                'mock_name': self._config.mock_name, 'parameters': ', '.join(arg.name for arg in self._func.arguments),
                'return': 'return' if self._is_returnable else '',
            }

        return function.replace("(  )", "()").replace(" * (", "* (").replace("* ", "*")


class StubsFile:
    def __init__(self, config, header_file, header_root_dir):
        self._functions = []
        self._config = config
        if header_file == header_root_dir:
            self._header_file = os.path.basename(header_file)
        else:
            self._header_file = os.path.relpath(header_file, header_root_dir)

    def append_stub_function(self, stub_func):
        self._functions.append(stub_func)

    def write(self, path='./'):
        if len(self._functions) == 0:
            return

        stubs = ""
        for f in self._functions:
            if f.is_variadic:
                logging.info(f.name + " is a variadic function, so it should be managed manually")
                print("(!!!)", f.name, "is a variadic function, so it should be managed manually.")
            stubs += str(f)

        content = self._config.stubs_file_template % {
            'stubs_header': self._header_file, 'mock_header': self._config.mock_header_name,
            'name_space': self._config.name_space, 'stubs': stubs, 'mock_name': self._config.mock_name,
            'header_output_path': self._config.header_output_path,
        }

        stub_file_name = re.sub(r"\.hpp|\.h", "_stubs.cpp", os.path.basename(self._header_file))

        # TODO: Remove this hard-code
        real_path = path + '/src'
        if not os.path.exists(real_path):
            os.makedirs(real_path)

        with open(real_path + "/" + stub_file_name, 'w') as file:
            file.write(content)
