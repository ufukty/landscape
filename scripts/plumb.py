from typing import List
import argparse
import csv
import os
import pdfplumber


def read_args():
    parser = argparse.ArgumentParser(description="Extract tables from PDF files")
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="PDF file path",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Path to output directory, needs to exist.",
    )
    return parser.parse_args()


def read_tables(path):
    tables: List[List[List[List[str | None]]]] = []
    with pdfplumber.open(path) as input:
        for page in input.pages:
            try:
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
            except Exception:
                pass
    return tables


def check_cell_types(tables):
    for i, table in enumerate(tables):
        for j, row in enumerate(table):
            for k, cell in enumerate(row):
                if not isinstance(cell, str):
                    print(f"table {i} row {j} column {k} is not string but {type(cell).__name__}")
    return tables


def stringify_cells(tables) -> List[List[List[List[str | None]]]]:
    for i, table in enumerate(tables):
        for j, row in enumerate(table):
            for k, cell in enumerate(row):
                tables[i][j][k] = cell if cell is not None else ""
    return tables


def reverse_line_wrap(tables) -> List[List[List[List[str | None]]]]:
    for i, table in enumerate(tables):
        for j, row in enumerate(table):
            for k, cell in enumerate(row):
                tables[i][j][k] = cell.replace("\r\n", "\n").replace("\n", " " if j == 0 else "; ")
    return tables


def continued_tables(tables: List[List[List[List[str | None]]]]):
    contd_tables: List[List[List[List[str | None]]]] = [[]]
    last_table_header = []
    for table in tables:
        header, content = table[0], table[1:]
        if header == last_table_header:
            contd_tables[-1].extend(content)
        else:
            last_table_header = header
            contd_tables.append(table)

    return contd_tables


def filter_short_tables(tables, threshold) -> List[List[List[List[str | None]]]]:
    filtered = []
    for table in tables:
        if len(table) >= threshold:
            filtered.append(table)
    return filtered


def filter_empty_header_cell_tables(tables: List[List[List[List[str | None]]]]):
    filtered = []
    for table in tables:
        if table[0].count("") == 0:
            filtered.append(table)
    return filtered


def print_table_headers(tables):
    for i, table in enumerate(tables):
        print(f"#{i} [ {" | ".join(table[0])} ] rows={len(table) - 1}")


def write_table_csv(dst, table):
    with open(dst, "w", newline="", encoding="utf-8") as output:
        writer = csv.writer(output)
        for row in table:
            writer.writerow(row)


args = read_args()
tables = read_tables(args.input)
tables = stringify_cells(tables)
check_cell_types(tables)
tables = reverse_line_wrap(tables)
tables = continued_tables(tables)
tables = filter_short_tables(tables, threshold=10)
tables = filter_empty_header_cell_tables(tables)
print_table_headers(tables)

for i, table in enumerate(tables):
    base = os.path.basename(args.input).replace(".pdf", "")
    write_table_csv(f"{args.output_dir}/{base}.table{i}.csv", table)
