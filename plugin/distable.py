"""
Support for orgmode-style tables.
"""
import re
from itertools import zip_longest

import vim

TABLE_LINE_RE = re.compile(r'^[ \t]*\|')
TABLE_BAR_END = re.compile(r'.*\|[ \t]*$')

# Table cell matcher also matches pre-table space. Cells start with their bar.
# So "   | cell 1 | whatever" becomes, with .findall, ['   ', '| cell 1 ', '| whatever']
TABLE_CELLS = re.compile(r'(^[^|]*|\|[^|]*)') 

def dis_in_table():
    return TABLE_LINE_RE.match(vim.current.line)

def _enter_or_create_row_below(max_widths):
    """
    Move the cursor to the next table row, creating it if necessary.

    If there is a table row in the line below the cursor, then move the cursor
    to the first cell in that row.

    Otherwise, create the row and move the cursor to the first cell.

    max_widths: array of cell widths where the first entry is the width of the whitespace
    to the left of the table.
    """
    buffer_idx = vim.current.window.cursor[0] # implicitly adding 1

    if buffer_idx == len(vim.current.buffer) or not TABLE_LINE_RE.match(vim.current.buffer[buffer_idx]):
        table_row = '|'.join(' ' * width for width in max_widths)
        vim.current.buffer.append(table_row, buffer_idx)

    vim.current.window.cursor = (buffer_idx + 1, max_widths[0] + 1)

def _reformat():
    """
    Reformat the table

    Returns: array of cell widths where the first entry is the width of the whitespace
    to the left of the table (the 'max_widths' array)
    """
    # Close the final column.
    if not TABLE_BAR_END.match(vim.current.line):
        vim.current.line += '|'

    # Read in the entire table.
    table = []
    max_widths = []

    idx = vim.current.window.cursor[0] - 1

    # Find the start of the table.
    while idx >= 0:
        line = vim.current.buffer[idx]
        if not TABLE_LINE_RE.match(line):
            first_table_line_idx = idx + 1
            break
        idx -= 1
    else:
        first_table_line_idx = 0

    # ... walk down from the start of the table, calculating widths.
    idx = first_table_line_idx
    while idx < len(vim.current.buffer):
        line = vim.current.buffer[idx]
        if not TABLE_LINE_RE.match(line):
            last_table_line_idx = idx - 1
            break

        cells = TABLE_CELLS.findall(line)
        # The first column is pre-table padding. All other columns should be stripped.
        cells = [cells[0]] + [cell[1:].rstrip() for cell in cells[1:]]

        max_widths = [max(a, b) for a, b in zip_longest(max_widths, (len(cell) for cell in cells), fillvalue=0)]
        table.append(cells)

        idx += 1
    else:
        last_table_line_idx = len(vim.current.buffer) - 1

    # Generate format strings from the max widths.
    max_widths_fmt = ['%%-%ds' % (max_width,) for max_width in max_widths]

    # Reformat the table to the max widths.
    for idx, cells in enumerate(table):
        table[idx] = [max_width_fmt % cell for max_width_fmt, cell in zip_longest(max_widths_fmt, cells, fillvalue='')]

    # Reinsert the table, only overwriting if something changed (so that tabbing around the table
    # doesn't mark the file as changed)
    idx = first_table_line_idx
    for cells in table:
        table_row = '|'.join(cells)
        if vim.current.buffer[idx] != table_row:
            vim.current.buffer[idx] = table_row
        idx += 1

    return max_widths

def dis_table_tab():
    if not dis_in_table():
        return

    # Work out what column we're currently on so we can advance it after we
    # reformat the table.
    current_column = vim.current.line.count('|', 0, vim.current.window.cursor[1])

    # Reformat the table and get the max_widths array.
    max_widths = _reformat()

    # Move the cursor to the next column if we're not at the end.
    # TODO if we are at the end, move to the next row, possibly creating a new row.
    if current_column < len(max_widths) - 2: # 2 because we have an extra 'pre-table' column at the start.
        new_x = sum(max_widths[:current_column + 1]) + current_column  # the addition accounts for the | chars
        vim.current.window.cursor = (vim.current.window.cursor[0], new_x + 1)
    else:
        _enter_or_create_row_below(max_widths)

def dis_table_cr():
    """
    Move the cursor to the start of the next row, creating it if necessary.
    """
    if not dis_in_table():
        return

    max_widths = _reformat()
    _enter_or_create_row_below(max_widths)
