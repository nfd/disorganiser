import vim
import datetime
import re

from distable import dis_in_table, dis_table_tab, dis_table_cr

RE_UL = re.compile(r'[ \t]+[-+\*]')
RE_LEADING_SPACES = re.compile(r'^( *)')

def current_row_0indexed():
    return vim.current.window.cursor[0] - 1

def _count_stars(line):
    if not line.startswith('*'):
        return 0

    return line.split(' ')[0].count('*')

def _count_stars_nearest_outline_line_above(row):
    """
    does _count_stars for each line begining at (vim) row 'row' until we get a nonzero result.
    """
    while row > 0:
        stars = _count_stars(vim.current.buffer[row - 1])
        if stars > 0:
            return stars
        row -= 1

    return 0

def _indent_line(line):
    return '*' + line if line.startswith('*') else line

def dis_indent():
    """ Indent the current outline (just this line). """
    vim.current.line = _indent_line(vim.current.line)

def _subtree_op(callback, include_nonoutline_lines=True):
    """
    used to perform an operation on every line of a subtree (such as indent, dedent, or fold)

    include_nonoutline_lines: if True, consider lines not starting with * part of the subtree
    (at whatever level the most recent outline line was)

    returns the final row in vim (1-base) co-ordinates
    """
    stop_at = _count_stars(vim.current.line)
    if stop_at == 0:
        return  # Not on an outline.

    row, _col = vim.current.window.cursor
    buf = vim.current.window.buffer

    # Always change the current line.
    buf[row - 1] = callback(buf[row - 1])

    while len(buf) > row:
        line = buf[row]
        num_stars = _count_stars(line)
        if num_stars and num_stars <= stop_at and not (include_nonoutline_lines is False and num_stars == 0):
            break

        buf[row] = callback(buf[row])
        row += 1

    return row - 1

def dis_indent_subtree():
    _subtree_op(_indent_line)

def _dedent_line(line):
    return line[1:] if line.startswith('*') and not line.startswith('* ') else line

def dis_dedent():
    """ Dedent the current outline (just this line). """
    vim.current.line = _dedent_line(vim.current.line)

def dis_dedent_subtree():
    _subtree_op(_dedent_line)

def _insert_outline_and_append(row, num_stars, char='*'):
    """
    Inserts a line at "row" and enters append mode.

    Also used to insert lists, hence 'char'
    """
    if num_stars <= 0:
        num_stars = 1

    if char == '*':
        # Inserting an outline -- add the appropriate number of stars.
        line = '*' * num_stars + ' '
    else:
        # Inserting a list -- add the appropriate number of *spaces*, then the list character.
        line = ' ' * num_stars + char + ' '

    vim.current.buffer.append(line, row)
    vim.current.window.cursor = (row + 1, 1)  # move to that line
    vim.command('startinsert!')  # enter append mode

def _is_list():
    return RE_UL.match(vim.current.line)

def _count_leading_spaces():
    return len(RE_LEADING_SPACES.match(vim.current.line).group(1))

def dis_outline_insert_above_children():
    """
    Insert a new outline line at the same level as the current one, immediately after the current line.
    """
    if _is_list():
        num_spaces = _count_leading_spaces()
        _insert_outline_and_append(vim.current.window.cursor[0], num_spaces, char=vim.current.line[num_spaces])
    else:
        _insert_outline_and_append(vim.current.window.cursor[0], _count_stars_nearest_outline_line_above(vim.current.window.cursor[0]))

def dis_outline_insert_after_children():
    """
    Insert a new outline line at the same level as the current one, after any children.
    """
    current_stars = _count_stars_nearest_outline_line_above(vim.current.window.cursor[0])
    row = vim.current.window.cursor[0]

    while row < len(vim.current.buffer):
        num_stars = _count_stars(vim.current.buffer[row])

        if num_stars > 0 and num_stars < current_stars:
            break

        row += 1

    _insert_outline_and_append(row, current_stars)

def dis_outline_insert_above_current():
    """
    Insert a new outline line at the same level as the current one, immediately before the current line.
    """
    if _is_list():
        num_spaces = _count_leading_spaces()
        _insert_outline_and_append(vim.current.window.cursor[0] - 1, num_spaces, char=vim.current.line[num_spaces])
    else:
        _insert_outline_and_append(vim.current.window.cursor[0] - 1, _count_stars(vim.current.line))

def dis_list_insert_above_children():
    """
    Insert a list on the next line, indented one space more than the current list (or outline).
    """
    if _is_list():
        num_spaces = _count_leading_spaces() + 1
    else:
        num_spaces = _count_stars(vim.current.line)

    _insert_outline_and_append(vim.current.window.cursor[0], num_spaces, char='-')

def _append_text_if_not_present(vim_row, text):
    line = vim.current.window.buffer[vim_row - 1]
    if text not in line:
        vim.current.window.buffer[vim_row - 1] += text

def _remove_text_if_present(vim_row, text):
    if text in vim.current.window.buffer[vim_row - 1]:
        vim.current.window.buffer[vim_row - 1] = vim.current.window.buffer[vim_row - 1].replace(text, '')

def dis_fold_cycle():
    """
    Cycle fold state.

    Unlike orgmode, we use just two states here: open and closed.
    Open: this fold and all its children are open.
    Closed: this fold and all its children are closed.
    """
    # If we are opening, then remove fold markers from all lines and open the fold in Vim.
    # If we are closing, then remove fold markers from all lines, add them to the top and bottom lines, and close the fold.
    if not vim.current.line.startswith('*'):
        # Not an outline section.
        return

    fold_level = vim.eval('foldclosed(' + str(vim.current.window.cursor[0]) + ')')
    is_open = int(fold_level) == -1

    def remove_markers(line):
        line = line.replace('{{{', '')
        line = line.replace('}}}', '')
        return line

    final_row = _subtree_op(remove_markers)

    if is_open:
        # Desired behaviour: close all folds.
        vim.current.line += '{{{'
        vim.current.window.buffer[final_row] += '}}}'
        vim.command('foldclose')
    else:
        # Desired behaviour: open all folds (and remove markers)
        # Removing the markers does this for us.
        pass

def dis_tab():
    """
    Do the Disorganiser tab action, which is context-sensitive.

    In headings: cycle visibility
    In tables: reformat table
    """
    if vim.current.line.startswith('*'):
        dis_fold_cycle()
    elif dis_in_table():
        dis_table_tab()

def dis_cr():
    """
    Context-sensitive CR behaviour
    """
    if vim.current.line.startswith('*'):
        dis_outline_insert_after_children()
    elif dis_in_table():
        dis_table_cr()

def dis_date_insert():
    """
    Insert current date at current position.
    """
    time_str = '<' + datetime.datetime.now().strftime('%Y-%m-%d %a') + '>'
    row, col = vim.current.window.cursor
    vim.current.line = '%s%s%s' % (vim.current.line[:col + 1], time_str, vim.current.line[col + 1:])
    
    vim.current.window.cursor = (row, col + len(time_str))
