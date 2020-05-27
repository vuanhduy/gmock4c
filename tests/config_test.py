import gmock4c.config as SUT
from tests.fixtures import *


def test_file_not_found():
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        SUT.Config("unknown_file.conf")
    assert SystemExit == pytest_wrapped_e.type
    assert -1 == pytest_wrapped_e.value.code


@pytest.mark.usefixtures("gmock4c_config")
def test_config(gmock4c_config):
    assert "__MYCLASS_MOCK_HPP_" == gmock4c_config.guard
    assert "mynamespace" == gmock4c_config.name_space
    assert "my/output/path/" == gmock4c_config.header_output_path
    assert "MyClassMock" == gmock4c_config.mock_name
    assert "myclassmock" == gmock4c_config.mock_instance_name
    assert "myclass_mock.hpp" == gmock4c_config.mock_header_name
    assert "myclass_mock.cpp" == gmock4c_config.mock_src_name
