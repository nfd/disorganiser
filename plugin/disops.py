import vim

def dis_visual_perline_op(fn):
    orig_row, orig_col = vim.current.window.cursor
    first_line = int(vim.eval('getpos("\'<")')[1])
    last_line = int(vim.eval('getpos("\'>")')[1])

    for line in range(first_line, last_line + 1):
        vim.current.window.cursor = (line, orig_row)
        fn()

    vim.current.window.cursor = (orig_row, orig_col)

