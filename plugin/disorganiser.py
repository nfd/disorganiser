import sys
import datetime
import re
import subprocess

import vim

from distable import dis_in_table, dis_table_tab, dis_table_cr, dis_table_reformat, dis_make_table_visual
from disops import dis_visual_perline_op

# General annoyance here is the difference between vim.current.window.cursor, which returns
# 1-indexed rows, and vim.current.buffer, which is 0-indexed. It makes for a lot of row - 1
# type statements.

RE_UL = re.compile(r'[ \t]+[-+\*]')
RE_LEADING_SPACES = re.compile(r'^( *)')
RE_TODO = re.compile(r'^(\*+)([ \t]*)(TODO |DONE )?(.*$)')

TODO_CYCLE = {'': 'TODO ', 'TODO ': 'DONE ', 'DONE ': ''}

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

def _find_nearest_outline_row_idx_above():
    """
    Returns the index of the closest outline row at or above the current line.

    Returns -1 if there is no outline at or above.
    """
    row, _col = vim.current.window.cursor
    while row >= 1:
        if vim.current.buffer[row - 1].startswith('*'):
            return row - 1

        row -= 1

    return -1

def _indent_line(line):
    if line.startswith('*'):
        return '*' + line
    elif _is_list(line):
        return ' ' + line
    else:
        return line

def dis_indent():
    """ Indent the current outline (just this line). """
    vim.current.line = _indent_line(vim.current.line)

def dis_indent_visual():
    dis_visual_perline_op(dis_indent)

def dis_dedent_visual():
    dis_visual_perline_op(dis_dedent)

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
    if line.startswith('*') and not line.startswith('* '):
        return line[1:]
    elif _is_list(line) and _is_list(line[1:]):
        return line[1:]
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

def _is_list(line=None):
    if line is None:
        line = vim.current.line

    return RE_UL.match(line)

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

def dis_itab():
    """
    Insert-mode tab -- jump to next cell if in table.
    """
    if dis_in_table():
        dis_table_tab(insert_mode=True)

def dis_cr():
    """
    Context-sensitive CR behaviour
    """
    if dis_in_table():
        dis_table_cr()
    else:
        dis_outline_insert_after_children()

def dis_date_insert(offset=0):
    """
    Insert current date at current position.

    You can use 'offset' to change the insertion point relative to the cursor. This lets you insert after the cursor
    in insert mode and before the cursor in normal mode.
    """
    time_str = '<' + datetime.datetime.now().strftime('%Y-%m-%d %a') + '>'
    row, col = vim.current.window.cursor

    vim.current.line = '%s%s%s' % (vim.current.line[:col + offset], time_str, vim.current.line[col + offset:])
    
    vim.current.window.cursor = (row, col + len(time_str))

def dis_cycle_todo():
    """
    Insert TODO or DONE at the start of the current outline
    """
    buffer_idx = _find_nearest_outline_row_idx_above()
    if buffer_idx == -1:
        print("No outline lines at or above the cursor.")
        return

    # The todo matcher only requires an outline, so will always match at this point.
    todo_match = RE_TODO.match(vim.current.buffer[buffer_idx])
    stars, whitespace, todo, therest = todo_match.groups()
    if todo is None:
        todo = ''

    next_todo = TODO_CYCLE[todo]
    vim.current.buffer[buffer_idx] = stars + whitespace + next_todo + therest.lstrip()

    # update the cursor position if we're on the line in question and past the insertion point.
    row, col = vim.current.window.cursor
    if buffer_idx == row - 1 and col > len(stars) + len(whitespace):
        col += (len(next_todo) - len(todo))
        vim.current.window.cursor = (row, col)

def dis_cycle_todo_or_reformat_table():
    """
    Context-sensitive <leader>dt -- reformat table if in a table, cycle TODO otherwise.
    """
    if dis_in_table():
        dis_table_reformat()
    else:
        dis_cycle_todo()

def _vim_config_exists(name):
    return vim.eval(f'exists("{name}")') != '0'

def _vim_get_config(name, default=None):
    if _vim_config_exists(name):
        return vim.eval(name)
    return default

URL_OPEN_BY_PLATFORM = {'darwin': 'open', 'win32': 'start', 'default': 'xdg-open'}
def _vim_get_url_open_command():
    """
    Return the command to open URLs on this system, or None.
    """
    # If we don't want to open URLs, then don't.
    if _vim_config_exists('g:disorganiser_url_no_open'):
        return None
    else:
        open_cmd = _vim_get_config('g:disorganiser_url_open_command', None)

        if open_cmd is None:
            open_cmd = URL_OPEN_BY_PLATFORM.get(sys.platform, URL_OPEN_BY_PLATFORM['default'])

        return open_cmd

def _mouse_open_url():
    # Are we in a url?
    current_line = vim.current.line
    current_cursor = vim.current.window.cursor[1]

    url_start = current_line.rfind('[[', 0, current_cursor)
    url_end = current_line.find(']]', current_cursor)

    if url_start != -1 and url_start <= current_cursor and url_end != -1 and url_end >= current_cursor:
        url = current_line[url_start + 2:url_end]

        # Copy the URL to the unnamed register, as if we'd yanked this URL.
        vim.command('let @" = "%s"' % (url.replace('"', r'\"'),))

        if '://' not in url:
            url = 'http://' + url

        # Invoke whatever is registered on this system to handle URLs.
        url_open_command = _vim_get_url_open_command()
        if url_open_command:
            subprocess.call([url_open_command, url])
        return True  # Event was handled, don't bubble up to Vim.

    return False # Event was not handled, invoke default Vim behaviour.

def dis_mouse(event_name):
    handled = False

    if event_name == '2-LeftMouse':
        # double click: open link
        handled = _mouse_open_url()

    if not handled:
        # Get Vim to handle the event without mappings.
        vim.command(r'execute "normal! \<%s>"' % (event_name,))
