from scripts.validate_dataset import main as validate_dataset_main
from wasteDetection.components.data_ingestion import DataIngestionError, ingest_dataset
from wasteDetection.components.data_validation import DatasetValidationError, validate_dataset


def test_missing_dataset_source_is_clear(tmp_path):
    try:
        ingest_dataset(file_id="", destination=tmp_path / "dataset")
    except DataIngestionError as exc:
        assert "GDRIVE_FILE_ID" in str(exc)
    else:
        raise AssertionError("expected missing source failure")


def test_validation_cli_validates_dataset(tmp_path, capsys):
    dataset = tmp_path / "dataset"
    (dataset / "images" / "train").mkdir(parents=True)
    (dataset / "images" / "val").mkdir(parents=True)
    yaml_path = tmp_path / "data.yaml"
    yaml_path.write_text(
        "nc: 6\nnames: [glass, plastic, metal, paper, cardboard, trash]\ntrain: images/train\nval: images/val\n",
        encoding="utf-8",
    )

    assert validate_dataset_main([str(dataset), str(yaml_path)]) == 0
    assert "Dataset is valid" in capsys.readouterr().out


def test_validation_requires_dataset(tmp_path):
    try:
        validate_dataset(tmp_path / "missing", tmp_path / "data.yaml")
    except DatasetValidationError as exc:
        assert "does not exist" in str(exc)
    else:
        raise AssertionError("expected missing dataset failure")


def test_validation_checks_six_class_mapping(tmp_path):
    dataset = tmp_path / "dataset"
    (dataset / "images" / "train").mkdir(parents=True)
    (dataset / "images" / "val").mkdir(parents=True)
    yaml_path = tmp_path / "data.yaml"
    yaml_path.write_text(
        "nc: 6\nnames: [glass, plastic, metal, paper, cardboard, trash]\ntrain: images/train\nval: images/val\n",
        encoding="utf-8",
    )
    result = validate_dataset(dataset, yaml_path)
    assert result["nc"] == 6


def test_validation_rejects_class_count_mismatch(tmp_path):
    dataset = tmp_path / "dataset"
    (dataset / "images" / "train").mkdir(parents=True)
    (dataset / "images" / "val").mkdir(parents=True)
    yaml_path = tmp_path / "data.yaml"
    yaml_path.write_text(
        "nc: 5\nnames: [glass, plastic, metal, paper, cardboard, trash]\ntrain: images/train\nval: images/val\n",
        encoding="utf-8",
    )
    try:
        validate_dataset(dataset, yaml_path)
    except DatasetValidationError as exc:
        assert "class count" in str(exc)
    else:
        raise AssertionError("expected class mismatch failure")
