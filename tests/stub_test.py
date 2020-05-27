import gmock4c.stub as Stub
import gmock4c.ast as AST
from tests.fixtures import *


@pytest.mark.usefixtures("function_cursors")
@pytest.mark.usefixtures("gmock4c_config")
def test_stub_methods(function_cursors, gmock4c_config):
    func = AST.Function(function_cursors[0])
    stub = Stub.StubFunction(func, gmock4c_config)
    expected_result = """
int basic_function( int a, int b ) {
    return MyClassMock::getInstance()->basic_function( a, b );
}
"""
    assert str(stub) == expected_result

    func = AST.Function(function_cursors[1])
    stub = Stub.StubFunction(func, gmock4c_config)
    expected_result = """
my_type_t simple_user_defined_type_function( const char *arg1, const my_type_t *arg2 ) {
    return MyClassMock::getInstance()->simple_user_defined_type_function( arg1, arg2 );
}
"""
    assert str(stub) == expected_result

    func = AST.Function(function_cursors[2])
    stub = Stub.StubFunction(func, gmock4c_config)
    expected_result = """
const my_type_t *simple_user_defined_type_function2() {
    return MyClassMock::getInstance()->simple_user_defined_type_function2();
}
"""
    assert str(stub) == expected_result

    func = AST.Function(function_cursors[3])
    stub = Stub.StubFunction(func, gmock4c_config)
    assert str(stub) == "\nvoid variadic_function( int arg1, ... ) {\n}\n"

    func = AST.Function(function_cursors[4])
    stub = Stub.StubFunction(func, gmock4c_config)
    expected_result = """
my_type my_function( const char *arg1, const my_type2 *arg2 ) {
    return MyClassMock::getInstance()->my_function( arg1, arg2 );
}
"""
    assert str(stub) == expected_result

    func = AST.Function(function_cursors[5])
    stub = Stub.StubFunction(func, gmock4c_config)
    expected_result = """
void my_void_function( int a ) {
     MyClassMock::getInstance()->my_void_function( a );
}
"""
    assert str(stub) == expected_result


@pytest.mark.usefixtures("function_cursors")
@pytest.mark.usefixtures("gmock4c_config")
def test_stub_file(function_cursors, gmock4c_config):
    header_file_name = 'test_header.hpp'
    stubs_file = Stub.StubsFile(gmock4c_config, header_file_name, header_file_name)
    for f in function_cursors:
        func = AST.Function(f)
        stub = Stub.StubFunction(func, gmock4c_config)
        stubs_file.append_stub_function(stub)

    stubs_file.write()
