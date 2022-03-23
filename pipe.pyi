from typing import (
    Any,
    Callable,
    Concatenate,
    Generic,
    Iterable,
    Iterator,
    ParamSpec,
    Protocol,
    TypeVar,
)

P = ParamSpec("P")
E = ParamSpec("E")
IN = TypeVar("IN")
OUT = TypeVar("OUT")

class Pipe(Generic[IN, OUT, P]):
    def __init__(
        self, function: Callable[Concatenate[Iterable[IN], P], Iterator[OUT]]
    ) -> None: ...
    def __ror__(self, other: Iterable[IN]) -> Iterator[OUT]: ...
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Pipe[IN, OUT, E]: ...

keyfunc = Callable[[Any], Any]

take: Pipe[Any, Any, int]
dedup: Pipe[Any, Any, keyfunc]
tail: Pipe[Any, Any, int]
skip: Pipe[Any, Any, int]
uniq: Pipe[Any, Any, keyfunc]
permutations: Pipe[Any, Any, int]
netcat: Pipe[Any, Any, [str, int]]
