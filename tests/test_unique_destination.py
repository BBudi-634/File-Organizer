from main import unique_destination

def test_returns_same_path_when_free(tmp_path):
    dest = tmp_path / "report.docx"
    assert unique_destination(str(dest)) == str(dest)


def test_appends_underscore_1_when_file_exists(tmp_path):
    dest = tmp_path / "report.docx"
    dest.write_text("original")

    result = unique_destination(str(dest))

    assert result == str(tmp_path / "report_1.docx")


def test_increments_until_free(tmp_path):
    (tmp_path / "report.docx").write_text("a")
    (tmp_path / "report_1.docx").write_text("b")
    (tmp_path / "report_2.docx").write_text("c")

    result = unique_destination(str(tmp_path / "report.docx"))

    assert result == str(tmp_path / "report_3.docx")


def test_handles_files_without_extension(tmp_path):
    (tmp_path / "README").write_text("hello")

    result = unique_destination(str(tmp_path / "README"))

    assert result == str(tmp_path / "README_1")


def test_handles_multi_part_extension(tmp_path):
    (tmp_path / "archive.tar.gz").write_text("data")

    result = unique_destination(str(tmp_path / "archive.tar.gz"))

    assert result == str(tmp_path / "archive.tar_1.gz")