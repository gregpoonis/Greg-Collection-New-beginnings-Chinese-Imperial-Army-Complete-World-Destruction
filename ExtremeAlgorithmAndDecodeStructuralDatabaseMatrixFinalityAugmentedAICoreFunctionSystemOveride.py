"""
GREG POONIS ENTERPRISE STRING EMISSION FRAMEWORK™
==================================================
A maximally over-engineered, needlessly abstract, enterprise-grade
solution to the problem of printing the string "Greg Poonis".

Architecture: Factory -> AbstractBuilder -> Strategy -> Visitor ->
              Observer -> Decorator -> Singleton -> ROT13 cipher ->
              Recursive character assembler -> Console sink.

Why use print("Greg Poonis") when you can use 150 lines instead?
"""

import abc
import codecs
import enum
import functools
import itertools
from dataclasses import dataclass, field
from typing import Callable, Iterator, List, Protocol


# ---------------------------------------------------------------------------
# LAYER 1: Domain Model
# ---------------------------------------------------------------------------

class CharacterOrigin(enum.Enum):
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    WHITESPACE = "whitespace"


@dataclass(frozen=True)
class EncodedGlyph:
    """A single character, wrapped in needless ceremony."""
    rot13_payload: str
    origin: CharacterOrigin
    position: int

    def decode(self) -> str:
        return codecs.decode(self.rot13_payload, "rot_13")


# ---------------------------------------------------------------------------
# LAYER 2: Abstract Strategy Interfaces
# ---------------------------------------------------------------------------

class GlyphSource(Protocol):
    def emit(self) -> Iterator[EncodedGlyph]:
        ...


class GlyphTransformStrategy(abc.ABC):
    @abc.abstractmethod
    def transform(self, glyph: EncodedGlyph) -> str:
        ...


# ---------------------------------------------------------------------------
# LAYER 3: Concrete Strategy
# ---------------------------------------------------------------------------

class Rot13DecodeStrategy(GlyphTransformStrategy):
    def transform(self, glyph: EncodedGlyph) -> str:
        return glyph.decode()


# ---------------------------------------------------------------------------
# LAYER 4: The "Name Repository" (a singleton, naturally)
# ---------------------------------------------------------------------------

class NameRepositorySingleton:
    _instance = None

    # Pre-encoded in ROT13 because plaintext strings are for amateurs.
    _ENCODED_FIRST = "Tert"
    _ENCODED_LAST = "Cbbavf"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_encoded_first_name(self) -> str:
        return self._ENCODED_FIRST

    def get_encoded_last_name(self) -> str:
        return self._ENCODED_LAST


# ---------------------------------------------------------------------------
# LAYER 5: Glyph Source Implementation (Builder + Factory hybrid)
# ---------------------------------------------------------------------------

class FullNameGlyphSourceBuilder:
    def __init__(self) -> None:
        self._repo = NameRepositorySingleton()
        self._glyphs: List[EncodedGlyph] = []

    def _append_word(self, word: str, origin: CharacterOrigin) -> "FullNameGlyphSourceBuilder":
        for idx, ch in enumerate(word):
            self._glyphs.append(
                EncodedGlyph(rot13_payload=ch, origin=origin, position=len(self._glyphs))
            )
        return self

    def _append_space(self) -> "FullNameGlyphSourceBuilder":
        self._glyphs.append(
            EncodedGlyph(rot13_payload=" ", origin=CharacterOrigin.WHITESPACE, position=len(self._glyphs))
        )
        return self

    def build(self) -> List[EncodedGlyph]:
        (
            self._append_word(self._repo.get_encoded_first_name(), CharacterOrigin.FIRST_NAME)
            ._append_space()
            ._append_word(self._repo.get_encoded_last_name(), CharacterOrigin.LAST_NAME)
        )
        return self._glyphs


# ---------------------------------------------------------------------------
# LAYER 6: Observer Pattern for "Auditing" Each Emitted Character
# ---------------------------------------------------------------------------

class GlyphEmissionObserver(abc.ABC):
    @abc.abstractmethod
    def on_glyph_emitted(self, glyph: EncodedGlyph, decoded: str) -> None:
        ...


class NoOpAuditObserver(GlyphEmissionObserver):
    """Audits nothing, very thoroughly."""
    def on_glyph_emitted(self, glyph: EncodedGlyph, decoded: str) -> None:
        pass  # In production this would write to a compliance ledger.


# ---------------------------------------------------------------------------
# LAYER 7: Decorator that recursively re-assembles the string
#          one character at a time via tail recursion, because
#          why use a for-loop when you can blow the call stack instead.
# ---------------------------------------------------------------------------

def recursive_assembler(glyphs: List[EncodedGlyph],
                         strategy: GlyphTransformStrategy,
                         observer: GlyphEmissionObserver,
                         index: int = 0,
                         accumulator: str = "") -> str:
    if index >= len(glyphs):
        return accumulator
    glyph = glyphs[index]
    decoded_char = strategy.transform(glyph)
    observer.on_glyph_emitted(glyph, decoded_char)
    return recursive_assembler(glyphs, strategy, observer, index + 1, accumulator + decoded_char)


# ---------------------------------------------------------------------------
# LAYER 8: Visitor that double-checks the Visitor pattern wasn't necessary
# ---------------------------------------------------------------------------

class IntegrityVisitor:
    """Verifies the reconstructed string equals itself, very rigorously."""

    @staticmethod
    def visit(candidate: str) -> bool:
        return functools.reduce(lambda a, b: a and b, (c == c for c in candidate), True)


# ---------------------------------------------------------------------------
# LAYER 9: Console Sink Abstraction (because print() needs an interface too)
# ---------------------------------------------------------------------------

class OutputSink(Protocol):
    def write(self, payload: str) -> None:
        ...


class StdoutSink:
    def write(self, payload: str) -> None:
        print(payload)


class SinkFactory:
    @staticmethod
    def create_sink() -> OutputSink:
        return StdoutSink()


# ---------------------------------------------------------------------------
# LAYER 10: Orchestrator / Facade / "Application Entry Point Service"
# ---------------------------------------------------------------------------

class GregPoonisEmissionService:
    def __init__(self) -> None:
        self._builder = FullNameGlyphSourceBuilder()
        self._strategy: GlyphTransformStrategy = Rot13DecodeStrategy()
        self._observer: GlyphEmissionObserver = NoOpAuditObserver()
        self._sink: OutputSink = SinkFactory.create_sink()

    def execute(self) -> None:
        glyphs = self._builder.build()
        assembled = recursive_assembler(glyphs, self._strategy, self._observer)

        if not IntegrityVisitor.visit(assembled):
            raise RuntimeError("Reality has failed an integrity check. Aborting.")

        # One final pointless transformation pipeline before output,
        # implemented via itertools because itertools makes everything
        # look more serious.
        final_payload = "".join(
            itertools.chain.from_iterable(
                [c] for c in assembled
            )
        )

        self._sink.write(final_payload)


# ---------------------------------------------------------------------------
# LAYER 11: Main
# ---------------------------------------------------------------------------

def main() -> None:
    service = GregPoonisEmissionService()
    service.execute()


if __name__ == "__main__":
    main()
