import gmock4c.mock as Mock
import gmock4c.ast as AST
import gmock4c.config as MockConf
from tests.fixtures import *


@pytest.mark.usefixtures("function_cursors")
def test_mock_methods(function_cursors):
    func = AST.Function(function_cursors[0])
    mock_method = Mock.MockMethod(func)
    assert str(mock_method) == 'MOCK_METHOD2( basic_function, int( int a, int b ) );'

    func1 = AST.Function(function_cursors[1])
    mock_method1 = Mock.MockMethod(func1)
    assert str(mock_method1) == 'MOCK_METHOD2( simple_user_defined_type_function, my_type_t( const char *arg1, const my_type_t *arg2 ) );'

    func2 = AST.Function(function_cursors[2])
    mock_method2 = Mock.MockMethod(func2)
    assert str(mock_method2) == 'MOCK_METHOD0( simple_user_defined_type_function2, const my_type_t*() );'

    # This is a variadic function --> we do not mock this.
    func3 = AST.Function(function_cursors[3])
    mock_method3 = Mock.MockMethod(func3)
    assert str(mock_method3) == ''


@pytest.mark.usefixtures("function_cursors")
@pytest.mark.usefixtures("gmock4c_config")
def test_mock_files(function_cursors, gmock4c_config):
    mock = Mock.Mock(gmock4c_config)
    mock.add_header("header.hpp")
    for f in function_cursors:
        func = AST.Function(f)
        mock_method = Mock.MockMethod(func)
        mock.append_mock_method(str(mock_method))

    mock.write_header()
    mock.write_src()
