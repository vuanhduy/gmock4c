import os
import logging


class MockMethod:
    template = """MOCK_METHOD%(num)d( %(method_name)s, %(result_type)s( %(parameters_with_types)s ) );"""

    def __init__(self, func):
        self._func = func

    def __str__(self):
        # NOTE: we cannot mock variadic functions
        if self._func.is_variadic:
            logging.info(self._func.name, "is a variadic function")
            return ''

        method = MockMethod.template % {'num': len(self._func.arguments), 'method_name': self._func.name,
                                        'result_type': self._func.result_type,
                                        'parameters_with_types': ', '.join([str(arg) for arg in self._func.arguments]),
                                        }
        method = method.replace("(  )", "()").replace(' *(', '*(').replace('* ', '*')
        logging.info('Created a new mock: ', method)
        return method


class Mock:
    def __init__(self, config):
        self._mock_methods = []
        self._headers = []
        self._config = config

    def add_header(self, header_file):
        inc = """#include "%s" """ % header_file
        self._headers.append(inc)

    def append_mock_method(self, method):
        self._mock_methods.append(method)

    def write_header(self, path="./"):
        headers = "\n".join(self._headers)
        methods = "\n    ".join(self._mock_methods)
        content = self._config.mock_header_template % {'guard': self._config.guard,
                                                       'name_space': self._config.name_space,
                                                       'mock_name': self._config.mock_name,
                                                       'mock_instance': self._config.mock_instance_name,
                                                       'mock_methods': methods, 'header_files': headers,
                                                       }
        # TODO: Remove this hard-code
        real_path = path + '/inc/mocks/' + self._config.header_output_path
        if not os.path.exists(real_path):
            os.makedirs(real_path)

        logging.info("Create a new mock header " + self._config.mock_header_name + " at " + real_path)
        with open(real_path + "/" + self._config.mock_header_name, "w") as file:
            file.write(content)

    def write_src(self, path="./"):
        content = self._config.mock_cpp_template % {'name_space': self._config.name_space,
                                                    'mock_name': self._config.mock_name,
                                                    'mock_instance': self._config.mock_instance_name,
                                                    'mock_header': self._config.mock_header_name,
                                                    'header_output_path': self._config.header_output_path,
                                                    }

        # TODO: Remove this hard-code
        real_path = path + '/src'
        if not os.path.exists(real_path):
            os.makedirs(real_path)

        logging.info("Create a new mock source " + self._config.mock_src_name + " at " + real_path)
        with open(real_path + "/" + self._config.mock_src_name, "w") as file:
            file.write(content)
