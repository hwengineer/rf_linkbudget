import numpy as np


class VerifyParameterType():
    @staticmethod
    def verify(value):
        for cls in __class__.__subclasses__():
            if cls.verify(value):
                return cls

        raise ValueError('Parameter malformed : {}'.format(value))


class VerifyParameterNumListOfTuples(VerifyParameterType):
    @staticmethod
    def verify(value):
        if type(value) == list:
            if len(value) >= 1:
                if type(value[0]) == tuple:
                    return True
        return False


class VerifyParameterNumList(VerifyParameterType):
    @staticmethod
    def verify(value):
        if type(value) == list:
            if len(value) > 1:
                if type(value[0]) != tuple:
                    return True
        return False


class VerifyParameterNumListSingleEntry(VerifyParameterType):
    @staticmethod
    def verify(value):
        if type(value) == list:
            if len(value) == 1:
                if type(value[0]) != tuple:
                    return True
        return False


class VerifyParameterNumSingleValue(VerifyParameterType):
    @staticmethod
    def verify(value):
        if type(value) == int or type(value) == float:
            return True
        return False


if __name__ == '__main__':
    print( VerifyParameterType.verify([0]) )
    print( VerifyParameterType.verify([(0, 10)]) )
    print( VerifyParameterType.verify([0, 10, 20]) )
    print( VerifyParameterType.verify(1) )
    # print( VerifyParameterType.verify('a') )
