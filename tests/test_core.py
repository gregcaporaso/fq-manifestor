import os
import pytest

from fq_manifestor import fq_manifestor


def _touch(path):
    """Create an empty file at path, creating parent dirs as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()


def _read_manifest(path):
    lines = path.read_text().splitlines()
    assert lines[0] == "sample-id\tforward-absolute-filepath\treverse-absolute-filepath"
    rows = {}
    for line in lines[1:]:
        if line:
            sid, fwd, rev = line.split("\t")
            rows[sid] = (fwd, rev)
    return rows


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_basic_paired_end(tmp_path):
    _touch(tmp_path / "sampleA_S1_L001_R1_001.fastq.gz")
    _touch(tmp_path / "sampleA_S1_L001_R2_001.fastq.gz")
    _touch(tmp_path / "sampleB_S2_L001_R1_001.fastq.gz")
    _touch(tmp_path / "sampleB_S2_L001_R2_001.fastq.gz")

    out = tmp_path / "manifest.tsv"
    fq_manifestor(str(tmp_path), str(out), verbose=False)

    rows = _read_manifest(out)
    assert set(rows) == {"sampleA", "sampleB"}
    assert os.path.isabs(rows["sampleA"][0])
    assert os.path.isabs(rows["sampleA"][1])


def test_recursive_search(tmp_path):
    sub = tmp_path / "sampleA_L001-ds.abc123"
    _touch(sub / "sampleA_S1_L001_R1_001.fastq.gz")
    _touch(sub / "sampleA_S1_L001_R2_001.fastq.gz")

    out = tmp_path / "manifest.tsv"
    fq_manifestor(str(tmp_path), str(out), verbose=False)

    rows = _read_manifest(out)
    assert "sampleA" in rows


def test_filter_pattern(tmp_path):
    _touch(tmp_path / "keep_S1_L001_R1_001.fastq.gz")
    _touch(tmp_path / "keep_S1_L001_R2_001.fastq.gz")
    _touch(tmp_path / "drop_S2_L001_R1_001.fastq.gz")
    _touch(tmp_path / "drop_S2_L001_R2_001.fastq.gz")

    out = tmp_path / "manifest.tsv"
    fq_manifestor(str(tmp_path), str(out), filter_pattern="keep", verbose=False)

    rows = _read_manifest(out)
    assert set(rows) == {"keep"}


def test_custom_extensions(tmp_path):
    _touch(tmp_path / "sampleA_S1_L001_R1_001.fq.gz")
    _touch(tmp_path / "sampleA_S1_L001_R2_001.fq.gz")

    out = tmp_path / "manifest.tsv"
    fq_manifestor(str(tmp_path), str(out), fq_extensions=["fq.gz"], verbose=False)

    rows = _read_manifest(out)
    assert "sampleA" in rows


def test_custom_split_pattern(tmp_path):
    _touch(tmp_path / "sampleA-S1-L001-R1-001.fastq.gz")
    _touch(tmp_path / "sampleA-S1-L001-R2-001.fastq.gz")

    out = tmp_path / "manifest.tsv"
    fq_manifestor(
        str(tmp_path), str(out), split_pattern="-",
        f_read_pattern="-R1-", r_read_pattern="-R2-", verbose=False
    )

    rows = _read_manifest(out)
    assert "sampleA" in rows


def test_custom_read_patterns(tmp_path):
    _touch(tmp_path / "sampleA_S1_L001_1.fastq.gz")
    _touch(tmp_path / "sampleA_S1_L001_2.fastq.gz")

    out = tmp_path / "manifest.tsv"
    fq_manifestor(
        str(tmp_path), str(out),
        f_read_pattern=r"_1\.fastq", r_read_pattern=r"_2\.fastq",
        verbose=False,
    )

    rows = _read_manifest(out)
    assert "sampleA" in rows


def test_verbose_false(tmp_path, capsys):
    _touch(tmp_path / "sampleA_S1_R1_001.fastq.gz")
    _touch(tmp_path / "sampleA_S1_R2_001.fastq.gz")

    out = tmp_path / "manifest.tsv"
    fq_manifestor(str(tmp_path), str(out), verbose=False)

    captured = capsys.readouterr()
    assert captured.out == ""


def test_output_file_written(tmp_path):
    _touch(tmp_path / "sampleA_S1_R1_001.fastq.gz")
    _touch(tmp_path / "sampleA_S1_R2_001.fastq.gz")

    out = tmp_path / "manifest.tsv"
    fq_manifestor(str(tmp_path), str(out), verbose=False)

    assert out.exists()
    assert out.stat().st_size > 0


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

def test_missing_forward_read(tmp_path):
    _touch(tmp_path / "sampleA_S1_R2_001.fastq.gz")  # only reverse

    out = tmp_path / "manifest.tsv"
    with pytest.raises(ValueError, match="Missing forward read for sample: sampleA"):
        fq_manifestor(str(tmp_path), str(out), verbose=False)


def test_missing_reverse_read(tmp_path):
    _touch(tmp_path / "sampleA_S1_R1_001.fastq.gz")  # only forward

    out = tmp_path / "manifest.tsv"
    with pytest.raises(ValueError, match="Missing reverse read for sample: sampleA"):
        fq_manifestor(str(tmp_path), str(out), verbose=False)


def test_no_read_pattern_match(tmp_path):
    # File name matches split pattern but neither R1 nor R2 pattern
    _touch(tmp_path / "sampleA_S1_L001_R3_001.fastq.gz")

    out = tmp_path / "manifest.tsv"
    with pytest.raises(ValueError, match="Forward/reverse patterns not found"):
        fq_manifestor(str(tmp_path), str(out), verbose=False)


# ---------------------------------------------------------------------------
# Warning case
# ---------------------------------------------------------------------------

def test_warning_mismatch(tmp_path, capsys):
    # Three files: two R1 for the same sample ID (second overwrites first),
    # plus one R2. sids_to_fps ends up with 1 complete record but 3 files
    # were found, so (1 != 3/2) triggers the WARNING.
    _touch(tmp_path / "sampleA_S1_R1_001.fastq.gz")
    _touch(tmp_path / "sampleA_S2_R1_002.fastq.gz")  # same sample id, overwrites
    _touch(tmp_path / "sampleA_S1_R2_001.fastq.gz")

    out = tmp_path / "manifest.tsv"
    fq_manifestor(str(tmp_path), str(out), verbose=True)

    captured = capsys.readouterr()
    assert "WARNING" in captured.out
