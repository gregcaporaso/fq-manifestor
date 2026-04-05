# fq-manifestor

`fq-manifestor` is a tool to assist with generating [QIIME 2 paired-end fastq manifest files](https://docs.qiime2.org/2022.2/tutorials/importing/#fastq-manifest-formats). This is not widely tested and likely not very general purpose, but is designed as a starting point to assist Illumina users with importing paired-end demultiplexed fastq files for use with QIIME 2. This tool does not actually import your data into QIIME 2, but rather generates a fastq manifest file and suggests an import command to use with QIIME 2. That increases portability of the tool as it can be run on systems without QIIME 2 installed on them.

This tool was originally developed to facilitate work with the [NAU Genetics Core Facility](https://in.nau.edu/gcf/).

## Why is this tool needed?

Importing can be hard. I talk a little about why [here](https://gregcaporaso.github.io/q2book/using/importing.html#importing-data-into-qiime-2).

## Installation

```
pip install fq-manifestor
```

For development:

```
git clone https://github.com/gregcaporaso/fq-manifestor
cd fq-manifestor
pip install -e ".[dev]"
```

Requires Python 3.10–3.12.

## Input data format

If you have a directory of files, `/sequence-data/humanure-run1`, containing demultiplexed paired end Illumina sequence data this tool will assume the directory is structured as follows:

```
$ tree /sequence-data/humanure-run1
/sequence-data/humanure-run1
├── 07717ac5_L001-ds.0795510ce4044fbab87b5c0b08aec105
│   ├── 07717ac5_S71_L001_R1_001.fastq.gz
│   └── 07717ac5_S71_L001_R2_001.fastq.gz
├── 08a10d08_L001-ds.060074faec87417b88e83d07470e7b10
│   ├── 08a10d08_S30_L001_R1_001.fastq.gz
│   └── 08a10d08_S30_L001_R2_001.fastq.gz
├── 091cbf06_L001-ds.9e1f729478e645bfa87b695aec93300d
│   ├── 091cbf06_S35_L001_R1_001.fastq.gz
│   └── 091cbf06_S35_L001_R2_001.fastq.gz
├── 10583739_1_L001-ds.0e7c88a021984a38b930ce5c60ddadfd
│   ├── 10583739-1_S72_L001_R1_001.fastq.gz
│   └── 10583739-1_S72_L001_R2_001.fastq.gz
```

In this case there are four samples, `07717ac5`, `08a10d08`, `091cbf06`, and `10583739-1`. The samples are grouped into per-sample directories, and there is a forward (R1) and reverse (R2) read file for each sample. This tool will assume that the text before the first `_` in the fastq filenames (not the directory names) is the sample id. Note that the sample ID preceding the first `_` must be the same for both forward (R1) and reverse (R2) read.

For example, the sample id that will be associated with the following files:

```
├── 10583739_1_L001-ds.0e7c88a021984a38b930ce5c60ddadfd
│   ├── 10583739-1_S72_L001_R1_001.fastq.gz
│   └── 10583739-1_S72_L001_R2_001.fastq.gz
```

is `10583739-1`. This is the text before the first `_` in the file name. Notice that the `-` in the sample id is replaced with an `_` in the directory name - this tool is building sample ids from the file names, not the directory names.

## Usage

```
fq-manifestor [OPTIONS] INPUT_DIR OUTPUT_FP
```

**Arguments:**

- `INPUT_DIR` — Directory to search recursively for fastq files.
- `OUTPUT_FP` — Path to write the manifest TSV file.

**Options:**

| Option | Default | Description |
| --- | --- | --- |
| `--fq-extensions TEXT` | `fastq.gz,fq.gz` | Comma-separated list of fastq file extensions to search for. |
| `--split-pattern TEXT` | `_` | Regex pattern used to split filenames to extract sample IDs. |
| `--f-read-pattern TEXT` | `_R1_` | Regex pattern identifying forward reads. |
| `--r-read-pattern TEXT` | `_R2_` | Regex pattern identifying reverse reads. |
| `--filter-pattern TEXT` | | Optional substring; only files containing this string are included. |
| `--verbose / --no-verbose` | `--verbose` | Print progress messages. |
| `--help` | | Show help and exit. |

**Example:**

```
fq-manifestor /sequence-data/humanure-run1 humanure-run1-fq-manifest.txt
```

This will either error with a hopefully-informative error message (but no guarantees!) or succeed with output that looks something like:

```
Searching directory: /sequence-data/humanure-run1
Found 160 fastq files.
To import, try running:
qiime tools import --type 'SampleData[PairedEndSequencesWithQuality]' --input-path humanure-run1-fq-manifest.txt --output-path demux.qza --input-format PairedEndFastqManifestPhred33V2
```

Try running that command in a QIIME 2 conda environment, and it should import successfully.

## Using the Python API

```python
from fq_manifestor import fq_manifestor

fq_manifestor(
    input_dir='/sequence-data/humanure-run1',
    output_fp='humanure-run1-fq-manifest.txt',
    f_read_pattern='_R1_',
    r_read_pattern='_R2_',
)
```

All parameters available through the CLI are also available in the Python API. See the source for full details.

## What if it doesn't work?

Let me know on the [issue tracker](https://github.com/gregcaporaso/fq-manifestor/issues), and I may be able to help. But this is very experimental so no promises!
