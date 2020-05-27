import logging
import collections
import clang.cindex as Clang


class Argument(collections.namedtuple("Argument", ['type', 'name'])):
    __slot__ = ()

    def __str__(self):
        tmp = " ". join([self.type, self.name]).replace('* ', '*')
        return tmp if tmp != ' ' else ''   


class Function:
    def __init__(self, cursor):
        if cursor.kind != Clang.CursorKind.FUNCTION_DECL:
            logging.critical(cursor.spelling, " is not a function")
            raise TypeError

        logging.debug("Parsing function: ", cursor.spelling)
        self._result_type = "void"
        self._name = cursor.spelling
        self._is_variadic = cursor.type.is_function_variadic()
        self._arguments = []
        self._parse(cursor)

    def _parse(self, cursor):
        """"
            This takes a Clang cursor of FUNCTION_DECL kind
             and set up basic information of the function
        """
        tokens = [t for t in cursor.get_tokens()]
        args = [arg for arg in cursor.get_arguments()]
        offset = 0

        # determine result type
        while cursor.location.offset != tokens[offset].location.offset:
            offset += 1

        self._result_type = ' '.join([t.spelling for t in tokens[0:offset]])

        # determine name and type of each argument
        for a in args:
            # determine argument type
            offset += 1
            while tokens[offset].kind == Clang.TokenKind.PUNCTUATION:
                offset += 1

            start_offset = offset
            offset += 1
            while a.location.offset != tokens[offset].location.offset:
                offset += 1

            arg_type = ' '.join([t.spelling for t in tokens[start_offset:offset]])
            arg = Argument(type=arg_type, name=a.spelling)

            # store the parsed argument
            self._arguments.append(arg)

    @property
    def name(self):
        return self._name

    @property
    def is_variadic(self):
        return self._is_variadic

    @property
    def result_type(self):
        return self._result_type

    @property
    def arguments(self):
        return self._arguments

    def __str__(self):
        args = ', '.join([str(arg) for arg in self._arguments])
        args += ', ...' if self._is_variadic else ''
        args = '( ' + args + ' )'
        result = ' '.join([self._result_type, self._name, args])
        return result.replace('* ', '*').replace(' (', '(').replace('(  )', '()')
