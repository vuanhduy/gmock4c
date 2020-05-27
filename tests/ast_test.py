import gmock4c.ast as SUT
from tests.fixtures import *


@pytest.mark.usefixtures("translation_unit_cursor")
def test_wrong_cursor_type(translation_unit_cursor):
    with pytest.raises(TypeError) as pytest_wrapped_e:
        SUT.Function(translation_unit_cursor)
    assert TypeError == pytest_wrapped_e.type


@pytest.mark.usefixtures("function_cursors")
def test_basic_func(function_cursors):
    func = SUT.Function(function_cursors[0])
    assert 'basic_function' == func.name
    assert 'int' == func.result_type
    assert ['int a', 'int b'] == [str(arg) for arg in func.arguments]
    assert 'int basic_function( int a, int b )' == str(func)

    func1 = SUT.Function(function_cursors[1])
    assert 'simple_user_defined_type_function' == func1.name
    assert 'my_type_t' == func1.result_type
    assert ['const char *arg1', 'const my_type_t *arg2'] == [str(arg) for arg in func1.arguments]
    assert 'my_type_t simple_user_defined_type_function( const char *arg1, const my_type_t *arg2 )' == str(func1)

    func2 = SUT.Function(function_cursors[2])
    assert 'simple_user_defined_type_function2' == func2.name
    assert 'const my_type_t *' == func2.result_type
    assert [] == [str(arg) for arg in func2.arguments]
    assert 'const my_type_t *simple_user_defined_type_function2()' == str(func2)

    func3 = SUT.Function(function_cursors[3])
    assert 'void variadic_function( int arg1, ... )' == str(func3)

    func4 = SUT.Function(function_cursors[4])
    assert 'my_type my_function( const char *arg1, const my_type2 *arg2 )' == str(func4)


