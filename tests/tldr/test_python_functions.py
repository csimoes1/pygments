# Test cases for Python function detection

def regular_function():  # Should detect ✅
    obj.__enter__()  # Should NOT detect ❌
    return obj.__exit__(None, None, None)  # Should NOT detect ❌

async def async_function(param):  # Should detect ✅
    result = some_object.__str__()  # Should NOT detect ❌
    return result

class MyClass:
    def __init__(self):  # Should detect ✅
        self.__setup__()  # Should NOT detect ❌
    
    def method(self):  # Should detect ✅
        return self.__repr__()  # Should NOT detect ❌
    
    async def async_method(self):  # Should detect ✅
        await obj.__aenter__()  # Should NOT detect ❌

def outer_function():  # Should detect ✅
    def inner_function():  # Should detect ✅
        obj.__call__()  # Should NOT detect ❌
    return inner_function

# Method calls that should NOT be detected:
result = obj.__len__()
data.__setitem__(key, value)
instance.__getattr__('name')