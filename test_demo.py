import gc
from weakref import WeakValueDictionary

from demo import WithoutGc, WithTraverse, WithTraverseAndClear


class Foo:
    def __init__(self, wrapper):
        self.wrapped = wrapper(self)


def run(wrapper) -> int:
    cache = WeakValueDictionary()

    for _ in range(1_000):
        f = Foo(wrapper)
        cache[id(f)] = f
        del f

    gc.collect(0)
    gc.collect(1)
    gc.collect(2)

    return len(cache)

res = run(WithoutGc)
print(f"WithoutGc: {res}")

res = run(WithTraverse)
print(f"WithTraverse: {res}")

res = run(WithTraverseAndClear)
print(f"WithTraverseAndClear: {res}")
