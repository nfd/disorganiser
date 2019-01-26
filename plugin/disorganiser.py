import vim

def current_row_0indexed():
    return vim.current.window.cursor[0] - 1

def _count_stars(line):
    if not line.startswith('*'):
        return 0

    return line.split(' ')[0].count('*')

def _indent_line(line):
    return '*' + line if line.startswith('*') else line

def dis_indent():
    """ Indent the current outline (just this line). """
    vim.current.line = _indent_line(vim.current.line)

def _subtree_op(callback):
    """
    used to perform an operation on every line of a subtree (such as indent, dedent, or fold)

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
        if _count_stars(line) <= stop_at:
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

def _insert_outline_and_append(row, num_stars):
    """
    Inserts a line at "row" and enters append mode.
    """
    if num_stars <= 0:
        return

    line = '*' * num_stars + ' '

    vim.current.buffer.append(line, row)
    vim.current.window.cursor = (row + 1, 1)  # move to that line
    vim.command('startinsert!')  # enter append mode

def dis_outline_insert_above_children():
    """
    Insert a new outline line at the same level as the current one, immediately after the current line.
    """
    _insert_outline_and_append(vim.current.window.cursor[0], _count_stars(vim.current.line))

def dis_outline_insert_above_current():
    """
    Insert a new outline line at the same level as the current one, immediately after the current line.
    """
    _insert_outline_and_append(vim.current.window.cursor[0] - 1, _count_stars(vim.current.line))

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

