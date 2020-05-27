from gmock4c.generator import Generator
from tests.fixtures import *


def test_generator():
    config_file_name = 'test.conf'
    header_file_name = 'test_header.hpp'
    setup_clang()

    gen = Generator(config_file_name, header_file_name)
    gen.parse()
    gen.write_mock_header()
    gen.write_mock_src()
    gen.write_stubs_src()
