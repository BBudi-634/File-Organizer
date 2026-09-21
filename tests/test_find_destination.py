from main import find_destination


def test_matches_word_document():
    assert find_destination("report.docx") == ("Documents", "Word")


def test_matches_pdf():
    assert find_destination("paper.pdf") == ("Documents", "PDF")


def test_matches_image():
    assert find_destination("photo.jpg") == ("Images", "Photos")


def test_unknown_extension_returns_none():
    assert find_destination("strange.xyz") is None

def test_case_insensitive():
    assert find_destination("REPORT.DOCX") == ("Documents", "Word")