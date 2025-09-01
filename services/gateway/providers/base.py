from typing import Protocol, AsyncIterator, Any, Mapping

class LLMProvider(Protocol):
    name: str
    async def complete(self, prompt: str, **kwargs) -> str: ...
    async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]: ...


