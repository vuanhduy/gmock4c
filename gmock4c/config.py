import os
import logging


logger = logging.getLogger('gmock4c_application')


class Config:
    def __init__(self, config_file_name):
        if not os.path.exists(config_file_name):
            logger.critical(config_file_name, "(config file) is not found!!")
            exit(-1)

        self._config = {}
        with open(config_file_name, 'r') as file:
            exec(file.read(), self._config)
            self._mock_name = self._config['mock_name']
            self._name_space = self._config['name_space']
            self._mock_header_template = self._config['mock_header_template']
            self._mock_cpp_template = self._config['mock_cpp_template']
            self._stubs_file_template = self._config['stubs_file_template']
            self._stub_function_template = self._config['stub_function_template']
            self._header_output_path = self._config['header_output_path']
            self._source_output_path = self._config['source_output_path']
            self._parsing_args = self._config['parsing_args']

            # Se inferred variables from mockname
            self._mock_instance_name = self._mock_name.lower() + "mock"
            self._guard = "__" + self._mock_name.upper() + "_MOCK_HPP_"
            self._mock_header_name = self._mock_name.lower() + "_mock.hpp"
            self._mock_src_name = self._mock_name.lower() + "_mock.cpp"

            # Add suffix to mockname. Note, mockname can no longer be used  to infer other variables
            self._mock_name = self._mock_name + "Mock"

    @property
    def guard(self):
        return self._guard

    @property
    def name_space(self):
        return self._name_space

    @property
    def header_output_path(self):
        return self._header_output_path

    @property
    def mock_name(self):
        return self._mock_name

    @property
    def mock_header_template(self):
        return self._mock_header_template

    @property
    def mock_cpp_template(self):
        return self._mock_cpp_template

    @property
    def mock_instance_name(self):
        return self._mock_instance_name

    @property
    def mock_header_name(self):
        return self._mock_header_name

    @property
    def mock_src_name(self):
        return self._mock_src_name

    @property
    def stubs_file_template(self):
        return self._stubs_file_template

    @property
    def stub_function_template(self):
        return self._stub_function_template

    @property
    def parsing_args(self):
        return self._parsing_args
