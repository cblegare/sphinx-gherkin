from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
)

from gherkin.parser import Parser

from sphinx_gherkin import SphinxGherkinError, keyword_to_objtype

K = TypeVar("K", bound="Keyword")
B = TypeVar("B", bound="DefinitionBuildah")


@dataclass(order=True, frozen=True)
class GherkinElement:
    location: CodeSpan


@dataclass(order=True, frozen=True)
class Keyword(GherkinElement):
    keyword: str

    @property
    def summary(self) -> str:
        raise NotImplementedError

    @property
    def objtype(self) -> str:
        return keyword_to_objtype(self.keyword)


def _no_op_matcher(keyword: K, document: Document) -> bool:
    return True


@dataclass()
class Document:
    name: str
    lines: Tuple[str, ...]
    feature: Feature
    comments: Tuple[Comment, ...]
    ancestry: Dict[GherkinElement, Optional[GherkinElement]] = field(
        default_factory=dict
    )

    def _find_all(self, cls: Type[K]) -> Iterator[K]:
        if issubclass(cls, Feature):
            yield self.feature  # type: ignore
        elif issubclass(cls, Comment):
            yield from self.comments
        else:
            for keyword in self.ancestry.keys():
                if isinstance(keyword, cls):
                    yield keyword

    def get_parent_keyword(self, element: GherkinElement) -> Keyword:
        parent = self.ancestry[element]
        if isinstance(parent, Keyword):
            return parent
        else:
            raise SphinxGherkinError(f"Ancestry is wrong for {element}.")

    def get_ancestry(self, element: Keyword) -> Sequence[Keyword]:
        ancestry = []
        ancestor = element
        while True:
            ancestry.append(ancestor)
            try:
                ancestor = self.get_parent_keyword(ancestor)
            except KeyError:
                break
        return ancestry

    def find(
        self,
        cls: Type[K],
        matcher: Optional[Callable[[K, Document], bool]] = None,
    ) -> Iterator[K]:
        if not matcher:
            matcher = _no_op_matcher
        for keyword in self._find_all(cls):
            if matcher(keyword, self):
                yield keyword

    def find_first(
        self,
        cls: Type[K],
        matcher: Optional[Callable[[K, Document], bool]] = None,
    ) -> K:
        return next(self.find(cls, matcher))


@dataclass(order=True, frozen=True)
class Comment(GherkinElement):
    text: str


@dataclass(order=True, frozen=True)
class BehaviorScope(Keyword):
    name: str
    description: str
    tags: Tuple[Tag, ...]

    @property
    def summary(self) -> str:
        return self.name.strip()


@dataclass(order=True, frozen=True)
class Feature(BehaviorScope):
    children: Tuple[BehaviorScope, ...]
    language: Language


@dataclass(order=True, frozen=True)
class Tag(GherkinElement):
    name: str


class Language(str):
    ...


@dataclass(order=True, frozen=True)
class Background(BehaviorScope):
    steps: Tuple[Step, ...]


@dataclass(order=True, frozen=True)
class CodeSpan:
    start: CodeLocation
    end: CodeLocation

    def clone(self) -> CodeSpan:
        return deepcopy(self)


@dataclass(order=True, frozen=True)
class CodeLocation:
    line: int
    column: int


@dataclass(order=True, frozen=True)
class Step(Keyword):
    text: str
    docstring: Optional[DocString]
    datatable: Optional[DataTable]

    @property
    def summary(self) -> str:
        return self.text.strip()


@dataclass(order=True, frozen=True)
class Scenario(BehaviorScope):
    steps: Tuple[Step, ...]
    examples: Tuple[Examples, ...]


@dataclass(order=True, frozen=True)
class DocString(GherkinElement):
    content: str
    mediatype: str
    delimiter: str


@dataclass(order=True, frozen=True)
class Rule(BehaviorScope):
    children: Tuple[BehaviorScope, ...]


@dataclass(order=True, frozen=True)
class Examples(BehaviorScope):
    datatable: DataTable


@dataclass(order=True, frozen=True)
class DataTable:
    values: Tuple[Tuple[str, ...], ...]


class DefinitionBuildah:
    def __init__(self, name: str, raw_code: str):
        self.name = name
        self.raw_code = raw_code
        self.lines = tuple(self.raw_code.splitlines())

    @classmethod
    def from_path(cls: Type[B], filepath: Path) -> B:
        return cls(str(filepath), filepath.read_text())

    def parse(self, gherkin_parser: Optional[Parser] = None) -> Document:
        parser = gherkin_parser or Parser()
        raw_definition = parser.parse(self.raw_code)

        code_span = CodeSpan(
            start=CodeLocation(line=0, column=0),
            end=CodeLocation(line=len(self.lines), column=len(self.lines[-1])),
        )

        self.document = Document(
            name=self.name, lines=self.lines, feature=None, comments=tuple()  # type: ignore
        )

        root_elements = {}
        for typename, definition in raw_definition.items():
            method = getattr(self, f"visit_{typename}")
            element = method(definition, code_span.end)
            root_elements[typename] = element

        for name, element in root_elements.items():
            setattr(self.document, name, element)

        return self.document

    def visit_feature(
        self,
        raw_definition: Dict[str, Any],
        farthest_code_location: CodeLocation,
    ) -> Feature:
        tags = self.visit_tags(raw_definition["tags"], farthest_code_location)

        location = self.visit_location(
            raw_definition["location"], farthest_code_location
        )

        if tags:
            first_tag = tags[0]
            location = CodeSpan(
                start=first_tag.location.start, end=location.end
            )

        language = self.visit_language(raw_definition["language"])

        children = self.visit_children(raw_definition["children"], location.end)

        feature = Feature(
            name=raw_definition["name"],
            description=raw_definition["description"],
            keyword=raw_definition["keyword"],
            language=language,
            tags=tags,
            children=children,
            location=location,
        )

        for tag in feature.tags:
            self._register_ancestry(tag, feature)

        for child in feature.children:
            self._register_ancestry(child, feature)

        return feature

    def visit_children(
        self,
        raw_definition: List[Dict[str, Dict[str, Any]]],
        farthest_code_location: CodeLocation,
    ) -> Tuple[BehaviorScope, ...]:
        children = []

        children_definitions = sorted(
            raw_definition,
            key=lambda child: next(iter(child.values()))["location"]["line"],  # type: ignore
            reverse=True,
        )

        for raw_child in children_definitions:
            typename, definition = next(iter(raw_child.items()))
            method = getattr(self, f"visit_{typename}")
            child = method(definition, farthest_code_location)
            children.append(child)
            farthest_code_location = self.find_closer_farthest_location(
                child.location.start
            )

        return tuple(reversed(children))

    def visit_location(
        self,
        raw_definition: Dict[str, Any],
        farthest_code_location: CodeLocation,
    ) -> CodeSpan:
        start = CodeLocation(
            line=raw_definition["line"] - 1,
            column=raw_definition["column"] - 1,
        )
        end = self.find_closer_farthest_location(farthest_code_location)
        location = CodeSpan(
            start=start,
            end=end,
        )
        return location

    def visit_tags(
        self,
        raw_definition: List[Dict[str, Any]],
        farthest_code_location: CodeLocation,
    ) -> Tuple[Tag, ...]:
        return tuple(
            self.visit_tag(raw_tag, farthest_code_location)
            for raw_tag in sorted(
                raw_definition,
                key=lambda child: child["location"]["line"],  # type: ignore
                reverse=True,
            )
        )

    def visit_tag(
        self,
        raw_definition: Dict[str, Any],
        farthest_code_location: CodeLocation,
    ) -> Tag:
        return Tag(
            name=raw_definition["name"],
            location=self.visit_location(
                raw_definition["location"],
                CodeLocation(line=raw_definition["location"]["line"], column=0),
            ),
        )

    def visit_language(self, raw_definition: str) -> Language:
        return Language(raw_definition)

    def visit_background(
        self,
        raw_definition: Dict[str, Any],
        farthest_code_location: CodeLocation,
    ) -> Background:
        location = self.visit_location(
            raw_definition["location"], farthest_code_location
        )

        background = Background(
            name=raw_definition["name"],
            description=raw_definition["description"],
            keyword=raw_definition["keyword"],
            steps=self.visit_steps(raw_definition["steps"], location.end),
            tags=tuple(),
            location=location,
        )

        for tag in background.tags:
            self._register_ancestry(tag, background)

        for step in background.steps:
            self._register_ancestry(step, background)

        return background

    def visit_scenario(
        self,
        raw_definition: Dict[str, Any],
        farthest_code_location: CodeLocation,
    ) -> Scenario:
        tags = self.visit_tags(raw_definition["tags"], farthest_code_location)

        location = self.visit_location(
            raw_definition["location"], farthest_code_location
        )

        if tags:
            first_tag = tags[0]
            location = CodeSpan(
                start=first_tag.location.start, end=location.end
            )

        examples = self.visit_examples(raw_definition["examples"], location.end)
        farthest_code_location = self.find_closer_farthest_location(
            examples[-1].location.start if examples else location.end
        )

        steps = self.visit_steps(
            raw_definition["steps"], farthest_code_location
        )

        scenario = Scenario(
            name=raw_definition["name"],
            description=raw_definition["description"],
            keyword=raw_definition["keyword"],
            tags=tags,
            steps=steps,
            examples=examples,
            location=location,
        )

        for tag in scenario.tags:
            self._register_ancestry(tag, scenario)

        for step in scenario.steps:
            self._register_ancestry(step, scenario)

        for one_examples in scenario.examples:
            self._register_ancestry(one_examples, scenario)

        return scenario

    def visit_rule(
        self,
        raw_definition: Dict[str, Any],
        farthest_code_location: CodeLocation,
    ) -> Rule:
        tags = self.visit_tags(raw_definition["tags"], farthest_code_location)

        location = self.visit_location(
            raw_definition["location"], farthest_code_location
        )

        if tags:
            first_tag = tags[0]
            location = CodeSpan(
                start=first_tag.location.start, end=location.end
            )

        rule = Rule(
            name=raw_definition["name"],
            description=raw_definition["description"],
            keyword=raw_definition["keyword"],
            tags=tags,
            children=self.visit_children(
                raw_definition["children"], location.end
            ),
            location=location,
        )

        for tag in rule.tags:
            self._register_ancestry(tag, rule)

        for child in rule.children:
            self._register_ancestry(child, rule)

        return rule

    def visit_steps(
        self,
        raw_definition: List[Dict[str, Any]],
        farthest_code_location: CodeLocation,
    ) -> Tuple[Step, ...]:
        steps = []
        for raw_step in sorted(
            raw_definition,
            key=lambda child: child["location"]["line"],  # type: ignore
            reverse=True,
        ):
            step = self.visit_step(raw_step, farthest_code_location)
            farthest_code_location = self.find_closer_farthest_location(
                step.location.start
            )
            steps.append(step)

        return tuple(reversed(steps))

    def visit_step(
        self,
        raw_definition: Dict[str, Any],
        farthest_code_location: CodeLocation,
    ) -> Step:
        location = self.visit_location(
            raw_definition["location"], farthest_code_location
        )

        docstring = self.maybe_visit_docstring(
            raw_definition, farthest_code_location
        )

        datatable = self.maybe_visit_datatable(
            raw_definition, farthest_code_location
        )

        step = Step(
            keyword=raw_definition["keyword"],
            text=raw_definition["text"],
            location=location,
            docstring=docstring,
            datatable=datatable,
        )

        if step.docstring:
            self._register_ancestry(step.docstring, step)

        return step  #

    def maybe_visit_docstring(
        self,
        raw_definition: Dict[str, Any],
        farthest_code_location: CodeLocation,
    ) -> Optional[DocString]:
        try:
            docstring_definition = raw_definition["docString"]
        except KeyError:
            return None

        return DocString(
            content=docstring_definition["content"],
            mediatype=docstring_definition["mediaType"],
            delimiter=docstring_definition["delimiter"],
            location=self.visit_location(
                docstring_definition["location"], farthest_code_location
            ),
        )

    def maybe_visit_datatable(
        self,
        raw_definition: Dict[str, Any],
        farthest_code_location: CodeLocation,
    ) -> Optional[DataTable]:
        try:
            datatable_definition = raw_definition["dataTable"]
        except KeyError:
            return None
        return DataTable(
            tuple(
                tuple(cell["value"] for cell in row["cells"])
                for row in datatable_definition["rows"]
            )
        )

    def visit_examples(
        self,
        raw_definition: List[Dict[str, Any]],
        farthest_code_location: CodeLocation,
    ) -> Tuple[Examples, ...]:
        examples = []
        for raw_examples in reversed(raw_definition):
            one_examples = self.visit_one_examples(
                raw_examples, farthest_code_location
            )
            farthest_code_location = self.find_closer_farthest_location(
                one_examples.location.start
            )
            examples.append(one_examples)

        return tuple(reversed(examples))

    def visit_one_examples(
        self,
        raw_definition: Dict[str, Any],
        farthest_code_location: CodeLocation,
    ) -> Examples:
        first_row = [
            cell["value"] for cell in raw_definition["tableHeader"]["cells"]
        ]
        other_rows = [
            [cell["value"] for cell in row["cells"]]
            for row in raw_definition["tableBody"]
        ]

        tags = self.visit_tags(raw_definition["tags"], farthest_code_location)
        location = self.visit_location(
            raw_definition["location"], farthest_code_location
        )

        if tags:
            first_tag = tags[0]
            location = CodeSpan(
                start=first_tag.location.start, end=location.end
            )

        rows = []
        rows.append(first_row)
        rows.extend(other_rows)

        examples = Examples(
            name=raw_definition["name"],
            description=raw_definition["description"],
            keyword=raw_definition["keyword"],
            tags=tags,
            location=location,
            datatable=DataTable(
                tuple(tuple(cell for cell in row) for row in rows)
            ),
        )

        for child in examples.tags:
            self._register_ancestry(child, examples)

        return examples

    def visit_comments(
        self,
        raw_definition: List[Dict[str, Any]],
        farthest_code_location: CodeLocation,
    ) -> Tuple[Comment, ...]:
        comments = []
        for raw_comment in raw_definition:
            start = CodeLocation(
                line=raw_comment["location"]["line"] - 1,
                column=raw_comment["location"]["column"] - 1,
            )

            comment = Comment(
                text=raw_comment["text"],
                location=CodeSpan(
                    start=start,
                    end=CodeLocation(
                        line=start.line, column=len(self.lines[start.line])
                    ),
                ),
            )

            comments.append(comment)

            self._register_ancestry(comment, None)

        return tuple(comments)

    def find_closer_farthest_location(
        self, farther: CodeLocation
    ) -> CodeLocation:
        inspected_line_number = farther.line - 1

        while inspected_line_number >= 0:
            inspected_line = self.lines[inspected_line_number].strip()
            if inspected_line and not inspected_line[0] in ("#", "@"):
                break
            inspected_line_number -= 1

        return CodeLocation(line=inspected_line_number + 1, column=0)

    def _register_ancestry(
        self, child: GherkinElement, parent: Optional[GherkinElement]
    ) -> None:
        self.document.ancestry[child] = parent
