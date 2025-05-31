"""
一些工具函数
"""
from typing import Callable, Generic, TypeVar
T = TypeVar('T') # 索引类型
RT = TypeVar('RT') # 返回值类型
class func2getitem(Generic[T, RT]):
    """
    将一个函数转换为可以使用索引访问的对象
    """
    def __init__(self, func: Callable[[T], RT]) -> None:
        self.func = func

    def __getitem__(self, idx: T) -> RT:
        return self.func(idx)
S = TypeVar('S') # 相当于self的类型
def method2geitem(func: Callable[[S, T], RT]) -> Callable[[S], func2getitem[T, RT]]: 
    """
    将一个方法转换为可以使用索引访问的对象
    """
    def wrapper_for_property(self_: S) -> func2getitem[T, RT]: 
        @func2getitem
        def wrapper(idx: T) -> RT:
            return func(self_, idx)
        return wrapper
    return wrapper_for_property