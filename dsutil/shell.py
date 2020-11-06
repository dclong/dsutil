import os
import re
import pandas as pd
import subprocess as sp
from typing import List, Sequence, Union


def to_frame(
    cmd="",
    split: str = r"  +",
    header: Union[int, List[str], None] = None,
    skip: Union[int, List[int]] = (),
    lines: List[str] = (),
    split_by_title: bool = False
) -> pd.DataFrame:
    if split_by_title:
        return to_frame_title(cmd=cmd, split=split, lines=lines)
    return to_frame_space(cmd=cmd, split=split, header=header, skip=skip, lines=lines)


def to_frame_space(
    cmd="",
    split: str = r"  +",
    header: Union[int, List[str], None] = None,
    skip: Union[int, List[int]] = (),
    lines: List[str] = ()
) -> pd.DataFrame:
    """Construct a pandas DataFrame from a List with the first row as header.

    :param lines: The output of the shell command.
    :param split: A regular expression pattern for splitting a line into fields.
    :param header: An integer, list of string or None specifiying the header of the data frame.
        If header is an integer, the corresponding row of lines after removing empty and skipped rows is used as header of the data frame; 
        if header is a list of string then it is used as the header of the data frame.
        if header is None, then default header is used for the data frame.
    :param cmd: A shell command.
    :return: A pandas DataFrame.
    """
    if not lines:
        lines = sp.check_output(cmd, shell=True).decode().strip().split("\n")
    if isinstance(skip, int):
        skip = [skip]
    data = [
        re.split(split, line.strip())
        for index, line in enumerate(lines) if line.strip() != "" and index not in skip
    ]
    if isinstance(header, int):
        columns = [re.sub(r"\s+", "_", col.lower()) for col in data[header]]
        data = (row for idx, row in enumerate(data) if idx != header)
        frame = pd.DataFrame(data, columns=columns)
    elif isinstance(header, list):
        frame = pd.DataFrame(data, columns=header)
    else:
        frame = pd.DataFrame(data)
    return frame.astype(str)


def to_frame_title(cmd="", split=r"  +", lines: List[str] = ()):
    """Convert the result of a shell command to a DataFrame.
    The headers are splitted by a regular expression
    while the columns are splitted by the right-most position of the headers.

    :param lines: The output of the shell command.
    :param split: A regular expression pattern for splitting headers.
    :param cmd: A shell command.
    """
    if not lines:
        lines = sp.check_output(cmd, shell=True).decode().strip().split("\n")
    headers = re.split(split, lines[0])
    n = len(headers)
    data = {}
    for idx in range(n - 1):
        start = lines[0].index(headers[idx])
        end = lines[0].index(headers[idx + 1])
        data[headers[idx]] = [line[start:end].strip() for line in lines[1:]]
    start = lines[0].index(headers[-1])
    data[headers[-1]] = [line[start:].strip() for line in lines[1:]]
    frame = pd.DataFrame(data)
    frame.columns = [col.strip().lower().replace(" ", "_") for col in frame.columns]
    return frame.astype(str)
