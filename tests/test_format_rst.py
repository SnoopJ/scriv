"""Tests for scriv/format_rst.py."""

import collections
import textwrap

import pytest

from scriv.config import Config
from scriv.format_rst import RstTools


@pytest.mark.parametrize(
    "text, parsed",
    [
        # Comments are ignored, and the section headers found.
        (
            """\
            .. Comments can be here
            .. and here.
            ..
            .. and here.
            Added
            -----

            - This thing was added.
              And we liked it.

            .. More comments can be here
            ..
            .. And here.

            """,
            {"Added": ["- This thing was added.\n  And we liked it."]},
        ),
        # Multiple section headers.
        (
            """\
            Added
            -----

            - This thing was added.
              And we liked it.


            Fixed
            -----

            - This thing was fixed.

            - Another thing was fixed.

            Added
            -----

            - Also added
              this thing
              that is very important.

            """,
            {
                "Added": [
                    "- This thing was added.\n  And we liked it.",
                    "- Also added\n  this thing\n  that is very important.",
                ],
                "Fixed": ["- This thing was fixed.", "- Another thing was fixed."],
            },
        ),
        # The specific character used for the header line is unimportant.
        (
            """\
            Added
            ^^^^^
            - This thing was added.

            Fixed
            ^^^^^
            - This thing was fixed.
            """,
            {"Added": ["- This thing was added."], "Fixed": ["- This thing was fixed."]},
        ),
        # You can even use periods as the underline, it won't be confused for a
        # comment.
        (
            """\
            Fixed
            .....
            - This thing was fixed.

            Added
            .....

            .. a comment.

            - This thing was added.
            """,
            {"Added": ["- This thing was added."], "Fixed": ["- This thing was fixed."]},
        ),
        # It's fine to have no header at all.
        (
            """\
            - No header at all.
            """,
            {None: ["- No header at all."]},
        ),
        # It's fine to have comments with no header, and multiple bulllets.
        (
            """\
            .. This is a scriv fragment.

            - No header at all.

            - Just plain bullets.
            """,
            {None: ["- No header at all.", "- Just plain bullets."]},
        ),
    ],
)
def test_parse_text(text, parsed):
    actual = RstTools().parse_text(textwrap.dedent(text))
    assert actual == parsed


def test_format_sections():
    sections = collections.OrderedDict(
        [
            (
                "Added",
                [
                    "- This thing was added.\n  And we liked it.",
                    "- Also added\n  this thing\n  that is very important.",
                ],
            ),
            ("Fixed", ["- This thing was fixed.", "- Another thing was fixed."]),
        ]
    )
    expected = """\

        Added
        ~~~~~

        - This thing was added.
          And we liked it.

        - Also added
          this thing
          that is very important.

        Fixed
        ~~~~~

        - This thing was fixed.

        - Another thing was fixed.
        """
    actual = RstTools(Config(rst_header_chars="#~")).format_sections(sections)
    assert actual == textwrap.dedent(expected)


@pytest.mark.parametrize(
    "config_kwargs, text, result",
    [
        ({}, "2020-07-26", "\n2020-07-26\n==========\n"),
        ({"rst_header_chars": "*-"}, "2020-07-26", "\n2020-07-26\n**********\n"),
    ],
)
def test_format_header(config_kwargs, text, result):
    actual = RstTools(Config(**config_kwargs)).format_header(text)
    assert actual == result
