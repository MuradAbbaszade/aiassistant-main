from ai.services.responder import AIResponse, MockRAGResponder, get_responder

__all__ = [
    "AIResponse",
    "MockRAGResponder",
    "OpenAIResponder",
    "get_responder",
]


def __getattr__(name: str):
    if name == "OpenAIResponder":
        from ai.services.openai_responder import OpenAIResponder

        return OpenAIResponder
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
