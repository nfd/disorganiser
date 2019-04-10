"""
Support for orgmode-style tables.
"""
import re
from itertools import zip_longest

import vim

from disexpr import Cell as CellParser, dis_eval, DEFAULT_CONTEXT, unlist

TABLE_LINE_RE = re.compile(r'^[ \t]*\|')
TABLE_BAR_END = re.compile(r'.*\|[ \t]*$')
TABLE_CELL_FORMULA = re.compile(r'[ \t]*=([^|=]+)')

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

def _get_table_start_line():
    idx = vim.current.window.cursor[0] - 1

    # Find the start of the table.
    while idx >= 0:
        line = vim.current.buffer[idx]
        if not TABLE_LINE_RE.match(line):
            return idx + 1
        idx -= 1

    return 0

def _get_table():
    " return first_table_line_idx, table "
    # TODO: Copied from _reformat; share this.
    # Read in the entire table.
    table = []

    first_table_line_idx = _get_table_start_line()

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

        table.append(cells)
        idx += 1
    else:
        last_table_line_idx = len(vim.current.buffer) - 1

    return first_table_line_idx, table

def _reinsert_table(first_table_line_idx, table):
    # Reinsert the table, only overwriting if something changed (so that tabbing around the table
    # doesn't mark the file as changed)
    idx = first_table_line_idx
    for cells in table:
        table_row = '|'.join(cells)
        if vim.current.buffer[idx] != table_row:
            vim.current.buffer[idx] = table_row
        idx += 1

def _recalc_get_cell_rel(context, offset, is_row):
    return context['cell_idx'][0] + offset if is_row else context['cell_idx'][1] + offset

def _recalc_get_cell_idx_range(context, col_or_row_ref, is_row):
    """
    Returns a list of indices referenced by a ColOrRowRef.

    Always returns a list, which is single-element if the reference is not a range.
    """

    if col_or_row_ref[0] == 'range':
        first = _recalc_get_cell_idx_range(context, col_or_row_ref[1][0], is_row)
        last = _recalc_get_cell_idx_range(context, col_or_row_ref[1][1], is_row)
        if len(first) != 1 or len(last) != 1:
            return '?ROR'  # Don't support ranges of ranges
        return list(range(first[0], last[0] + 1))
    elif col_or_row_ref[0] == 'abs':
        return [col_or_row_ref[1][0]]
    elif col_or_row_ref[0] == 'rel':
        offset = col_or_row_ref[1][0]
        return [_recalc_get_cell_rel(context, offset, is_row)]
    else:
        return ['?UNKREF']

def _recalc_get_cell_value(context, row, col):
    """
    Return the values of a cell reference (in square brackets).

    Returns: a single-element list (one cell reference) or multi-element list (range reference)
    """
    rows = _recalc_get_cell_idx_range(context, row, True)
    cols = _recalc_get_cell_idx_range(context, col, False)

    results = []
    formulas = context['formulas']
    values = context['values']

    for row in rows:
        for col in cols:
            idx = (row, col)
            results.append(_recalc_one(idx, formulas, values, context))

    return results

def _recalc_one(idx, formulas, values, context):
    if idx not in values:
        with context.newscope(cell_idx=idx):
            values[idx] = '?SELF'  # Prevent recursion if we self-reference.
            try:
                value = dis_eval(formulas[idx], context)
            except Exception as e:
                raise
                value = '?EXC' + str(e)

            if isinstance(value, list):
                # The result of _recalc_get_cell_value
                assert len(value) == 1
                value = value[0]

            values[idx] = value

    return values[idx]

def _recalc_sum(context, *args):
    result = 0
    for arg in args:
        arg_value = dis_eval(arg, context) 
        if isinstance(arg_value, list):
            result += sum(arg_value)
        else:
            result += arg_value

    return result

SPREADSHEET_CONTEXT = DEFAULT_CONTEXT.copy()
SPREADSHEET_CONTEXT.push({
    'sum': _recalc_sum,
})

def _recalc():
    """
    Table: a list of lists, each containing a string.

    Updates 'table' with the results of each expression.
    """
    if not dis_in_table():
        return

    first_table_line_idx, table = _get_table()

    values = {}  # maps (y, x) to value (both 0 indexed)
    formulas = {}  # maps (y, x) to parsed formula
    formula_strs = {} # The original string, for replacement.
    context = SPREADSHEET_CONTEXT.copy()
    context.push({
        'table': table,
        'cell': _recalc_get_cell_value,  # for evaluating cell references
        'values': values,
        'formulas': formulas,
    })

    # Find and parse all the formulas.
    needs_evaluation = set()

    for row_idx, row in enumerate(table):
        for cell_idx, cell in enumerate(row[1:]):  # skip the initial pre-table portion
            formula_match = TABLE_CELL_FORMULA.match(cell)

            idx = (row_idx, cell_idx)

            if formula_match:
                formula_str = formula_match.group(1)
                needs_evaluation.add(idx)
            else:
                formula_str = cell
                
            try:
                formulas[idx] = CellParser.parse(formula_str)
            except Exception:
                formulas[idx] = '?PARSE' + formula_str

            formula_strs[idx] = formula_str

    # Evaluate all the formulas.
    for idx in needs_evaluation:
        value = _recalc_one(idx, formulas, values, context)

        # Update the table with the value.
        table[idx[0]][idx[1] + 1] = '=' + formula_strs[idx] + '=' + str(value)

    context.pop()
    _reinsert_table(first_table_line_idx, table)

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

    first_table_line_idx = _get_table_start_line()

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

    _reinsert_table(first_table_line_idx, table)

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

def dis_table_reformat():
    """
    Reformat table (and recalculate any formulae)
    """
    if not dis_in_table():
        return

    _recalc()
    _reformat()
