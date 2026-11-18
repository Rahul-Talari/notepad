"""Tests for the text logic in notepad.py (no display needed).

Run with:  python3 tests/test_markdown.py     (or: pytest tests/)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import notepad as n  # noqa: E402


def parse(text):
    ghosts, runs = [], []
    spans, markers = n.parse_markdown(text, ghosts, runs)
    return ([(tag, text[a:b]) for tag, a, b in spans],
            [text[a:b] for a, b, _ in markers],
            [text[a:b] for a, b, _ in ghosts])


def visible(text):
    """Text as displayed in formatted view (cursor elsewhere)."""
    ghosts, runs = [], []
    _, markers = n.parse_markdown(text, ghosts, runs)
    hide = set()
    for a, b, _ in markers:
        hide.update(range(a, b))
    for run in runs:
        for a, b, _ in run[:len(run) - len(run) // 2]:
            hide.update(range(a, b))
    return "".join(ch for i, ch in enumerate(text) if i not in hide)


def toggle(full, sel, mark):
    so = full.index(sel)
    a, b, rep, _, _ = n.toggle_wrap_text(full, so, so + len(sel), mark)
    return full[:a] + rep + full[b:]


def test_inline_styles():
    s, _, _ = parse("# Title\nSome **bold** and *it* and ***both*** ~~x~~ `c` [t](http://a.b) http://x.y")
    for want in [("h1", "# Title"), ("bold", "bold"), ("italic", "it"), ("bold", "both"),
                 ("italic", "both"), ("strike", "x"), ("code", "c"), ("link", "t"), ("link", "http://x.y")]:
        assert want in s, want


def test_no_false_italics():
    s, _, _ = parse("snake_case_name and file_v2_final.txt")
    assert s == []


def test_blocks():
    s, _, _ = parse("- item\n1. first\n> q **b**\n---\n```\ncode **no**\n```")
    assert ("listmark", "-") in s and ("listmark", "1.") in s
    assert ("bold", "b") in s and ("hr", "---") in s
    assert ("bold", "no") not in s, "no formatting inside code blocks"


def test_escapes_and_entities():
    assert parse(r"\[RAW DOCUMENT]")[1] == ["\\"]
    s, m, _ = parse(r"1\. PDF PARSER")
    assert m == ["\\"] and not any(t == "listmark" for t, _ in s)
    _, m, g = parse("&#x20;  ├─ Text")
    assert m == ["&#x20"] and g == [";"]
    assert parse("Tom &amp; Jerry")[1] == ["amp;"]
    s, _, _ = parse(r"\*not italic\* and `code \*x\*`")
    assert not any(t == "italic" for t, _ in s) and ("code", r"code \*x\*") in s


def test_setext_headings():
    s, m, _ = parse("Title\n=====\n\nSub\n---\n\nPara\n\n---")
    assert ("h1", "Title") in s and ("h2", "Sub") in s and ("hr", "---") in s and "=====" in m


def test_windows_paragraph_breaks():
    assert visible("A\n\nB\n\nC") == "A\nB\nC"
    assert visible("A\n\n\n\nB") == "A\n\nB"
    assert visible("A\n\n\n\n\n\n\n\nB") == "A\n\n\n\nB"
    assert visible("A\nB") == "A\nB"
    assert visible("```\nx\n\ny\n```").count("\n\n") == 1, "blank lines inside code are kept"


def test_toggle_wrap():
    assert toggle("hello world", "world", "**") == "hello **world**"
    assert toggle("hello **world**", "world", "**") == "hello world"
    assert toggle("hello **world**", "**world**", "**") == "hello world"
    assert toggle("hello **world**", "world", "*") == "hello ***world***"
    assert toggle("hello ***world***", "world", "*") == "hello **world**"
    assert toggle("- one\n- two", "- one\n- two", "**") == "- **one**\n- **two**"
    assert toggle("# Head", "# Head", "**") == "# **Head**"


def test_line_transforms():
    assert n.set_heading_lines(["hello"], 2) == ["## hello"]
    assert n.set_heading_lines(["### hello"], 0) == ["hello"]
    assert n.toggle_bullet_lines(["a", "", "b"]) == ["- a", "", "- b"]
    assert n.toggle_bullet_lines(["- a", "- b"]) == ["a", "b"]
    assert n.toggle_number_lines(["a", "- b"]) == ["1. a", "2. b"]
    assert n.clear_formatting_lines(["## **Hi** *there* [l](http://x) `c` ~~s~~"]) == ["Hi there l c s"]


def test_links_and_titles():
    assert n.find_link_at("see [docs](https://d.io) here", 6) == "https://d.io"
    assert n.find_link_at("go www.example.com now", 5) == "https://www.example.com"
    assert n.derive_title("\n## My **notes**\nmore") == "My notes"
    assert n.safe_filename('a/b:c?') == "abc"


def test_encodings_round_trip():
    text = "héllo\nwörld\n"
    for enc in ["utf-8", "utf-8-sig", "utf-16-le", "utf-16-be", "cp1252"]:
        for eol in ["\r\n", "\n", "\r"]:
            back, enc2, eol2 = n.decode_bytes(n.encode_text(text, enc, eol))
            assert (back, eol2) == (text, eol), (enc, eol)
            if enc != "cp1252":
                assert enc2 == enc
    assert n.decode_bytes("héllo".encode("cp1252"))[1] == "cp1252"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
        print("ok  ", t.__name__)
    print(f"{len(tests)} tests passed")
