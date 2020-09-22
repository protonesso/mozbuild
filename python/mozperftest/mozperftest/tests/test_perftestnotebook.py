import json
import mozunit
import pathlib
from mozperftest.metrics.notebook.analyzer import NotebookAnalyzer
from mozperftest.metrics.notebook.constant import Constant
from mozperftest.metrics.notebook.transformer import Transformer
from mozperftest.metrics.notebook.transforms.single_json import SingleJsonRetriever


def test_init(ptnbs):
    for ptnb in ptnbs.values():
        assert isinstance(ptnb.fmt_data, dict)
        assert isinstance(ptnb.file_groups, dict)
        assert isinstance(ptnb.config, dict)
        assert isinstance(ptnb.sort_files, bool)
        assert isinstance(ptnb.const, Constant)
        assert isinstance(ptnb.analyzer, NotebookAnalyzer)
        assert isinstance(ptnb.transformer, Transformer)


def test_parse_file_grouping(ptnbs):
    def _check_files_created(ptnb, expected_files):
        actual_files = set(ptnb.parse_file_grouping(expected_files))
        expected_files = set(expected_files)

        # Check all parsed files are regular files.
        assert all([pathlib.Path(file).is_file for file in actual_files])
        # Check parse_file_grouping function returns correct result.
        assert actual_files - expected_files == set()

    # If file_grouping is a list of files.
    ptnb = ptnbs["ptnb_list"]
    expected_files = ptnb.file_groups["group_1"]
    _check_files_created(ptnb, expected_files)

    # If file_grouping is a directory string.
    ptnb = ptnbs["ptnb_str"]
    expected_path = ptnb.file_groups["group_1"]
    expected_files = [
        f.resolve().as_posix() for f in pathlib.Path(expected_path).iterdir()
    ]
    _check_files_created(ptnb, expected_files)


def test_process(ptnbs, files):
    # Temporary resource files.
    files, _, output = files
    file_1 = files["file_1"]
    file_2 = files["file_2"]

    # Create expected output.
    expected_output = [
        {
            "data": [
                {"value": 101, "xaxis": 1, "file": file_1},
                {"value": 102, "xaxis": 1, "file": file_1},
                {"value": 103, "xaxis": 1, "file": file_1},
                {"value": 201, "xaxis": 2, "file": file_2},
                {"value": 202, "xaxis": 2, "file": file_2},
                {"value": 203, "xaxis": 2, "file": file_2},
            ],
            "name": "group_1",
            "subtest": "browserScripts.timings.firstPaint",
        }
    ]

    ptnb = ptnbs["ptnb_str"]

    # Set a custom transformer.
    ptnb.transformer = Transformer([], SingleJsonRetriever())

    # Create expected result.
    expected_result = {
        "data": expected_output,
        "file-output": output,
    }

    # Check return value.
    actual_result = ptnb.process()
    assert actual_result == expected_result

    # Check output file.
    with pathlib.Path(output).open() as f:
        actual_output = json.load(f)

    assert expected_output == actual_output


if __name__ == "__main__":
    mozunit.main()
