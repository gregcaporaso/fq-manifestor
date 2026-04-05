from __future__ import annotations

import os.path
from typing import Annotated, Optional

import typer

from fq_manifestor._core import fq_manifestor

app = typer.Typer(
    help="Generate a QIIME 2 paired-end fastq manifest from a directory of demultiplexed reads."
)


@app.command()
def main(
    input_dir: Annotated[
        str,
        typer.Argument(help="Directory to search recursively for fastq files."),
    ],
    output_fp: Annotated[
        str,
        typer.Argument(help="Path to write the manifest TSV file."),
    ],
    fq_extensions: Annotated[
        str,
        typer.Option(
            "--fq-extensions",
            help="Comma-separated list of fastq file extensions to search for.",
        ),
    ] = "fastq.gz,fq.gz",
    split_pattern: Annotated[
        str,
        typer.Option(
            "--split-pattern",
            help="Regex pattern used to split filenames to extract sample IDs.",
        ),
    ] = "_",
    f_read_pattern: Annotated[
        str,
        typer.Option(
            "--f-read-pattern",
            help="Regex pattern identifying forward reads.",
        ),
    ] = "_R1_",
    r_read_pattern: Annotated[
        str,
        typer.Option(
            "--r-read-pattern",
            help="Regex pattern identifying reverse reads.",
        ),
    ] = "_R2_",
    filter_pattern: Annotated[
        Optional[str],
        typer.Option(
            "--filter-pattern",
            help="Optional substring; only files containing this string are included.",
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose/--no-verbose",
            help="Print progress messages.",
        ),
    ] = True,
) -> None:
    extensions = [e.strip() for e in fq_extensions.split(",") if e.strip()]

    fq_manifestor(
        input_dir=input_dir,
        output_fp=output_fp,
        fq_extensions=extensions,
        split_pattern=split_pattern,
        f_read_pattern=f_read_pattern,
        r_read_pattern=r_read_pattern,
        filter_pattern=filter_pattern,
        verbose=verbose,
    )

    abs_output_fp = os.path.abspath(output_fp)
    typer.echo("To import, try running:")
    typer.echo(
        f"qiime tools import "
        f"--type 'SampleData[PairedEndSequencesWithQuality]' "
        f"--input-path {abs_output_fp} --output-path demux.qza "
        f"--input-format PairedEndFastqManifestPhred33V2"
    )
