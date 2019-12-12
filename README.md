Disorganiser
===

A task management plug-in for Vim, heavily "inspired by" emacs org-mode and vim-orgmode (though not sharing any code with those projects).

Probably contains 1% of the functionality of vim-orgmode; on the other hand, runs at full speed even when your org file is larger than a few kilobytes.

Requires a recent Vim with Python 3 support.

License: Disorganiser is available under two sets of terms:

To the extent possible under law, Nicholas FitzRoy-Dale has waived all copyright and related or neighboring rights to this work.

As an alternative, you may use this code under the terms of the MIT license [[https://opensource.org/licenses/MIT]].

Installation
---

Vim 8 with native plugin support: clone this repository into your `~/.vim/pack/whatever/start` directory.

Usage
---

This section is just a sketch of what Disorganiser offers, but see the Mappings section for shortcuts for many of these commands.

**File extension**: Disorganiser files have the extension `.dis` rather than `.org`, because they're sufficiently different from Org-mode that keeping the same extension was getting confusing.

**Quotation**: Enclose text in backticks, `like this` to quote it and protect it from any other syntax highlighting.

**Headings**: Start a line with a single asterisk (`*`) to create a heading. Start a line with two asterisks to create a sub-heading, and so on. Press <TAB> on a heading to switch between hiding or showing it. Headings can be indented or dedented with `>>` and `<<`, and you can do the same for entire subtrees with `<leader><c` and `<leader>>c`.

**Dates**: Insert the current date with `<leader>ddc`.

**TODO** and **DONE** have special highlighting. Use `<leader>dt` when on a heading to cycle between TODO, DONE, and nothing.

**Tables** are created by starting the line with a pipe (optionally preceeded by whitespace). Tables can contain formulae and references to other cells.

**URLs**: Create a URL using `[[` and `]]`, e.g. `[[http://code.lardcave.net]]`. If you have mouse support, URLs are double-clickable; double-clicking a URL by default copies it to the anonymous register (as if it had been yanked) and opens the URL using the default system handler.

Mappings
---

Key                   | Mode   | Outcome
----------------------| ------ | -----------------------------------------------------------------------------------
CR or `<leader>ha`    | Normal | Insert heading at same level as current, after any children
S-CR or `<leader>hj`  | Normal | Insert heading at same level as current, below current line (also works for lists)
C-S-CR or `<leader>hk`| Normal | Insert heading at same level as current, above current line (also works for lists)
`<leader>dl`          | Normal | Insert list at level one lower than current list or heading
`<<`                  | Normal | Dedent current heading
`<c`                  | Normal | Dedent current heading and all children
`>>`                  | Normal | Indent current heading
`>c`                  | Normal | Indent current heading and all children
`<TAB>`               | Normal | Cycle fold level
`<leader>ddc`         | Normal | Insert current date
`<leader>dt`          | Normal | Cycle TODO
`<S-CR>`              | Insert | Insert heading below current (same as S-CR in normal mode)
`<D-d>d`              | Insert | Insert current date (same as <leader>ca in normal mode)
`>>`                  | Visual | Indent selected headings
`<<`                  | Visual | Dedent selected headings

When editing tables, some keys work differently:

Key                     | Mode   | Outcome
----------------------- | ------ | -----------------------------------------------------------------------------------
`<TAB>`                 | Normal | Reformat table and move to next cell, or next row (if at end), creating a new row if needed
`<CR>`                  | Normal | Reformat table and move to first cell of next row, creating a new row if needed
`<D-d>t`                | Insert | Reformat table
 
Configuration
---

`g:disorganiser_url_open_command`: Command to use to open URLs. If not specified, it is open on macOS, start on Windows, and xdg-open on other systems.  
`g:disorganiser_url_no_open`: Don't attempt to open URLs.

Tables
---

*Formulae*: In table cells, indicate that a cell contains a formula by starting it with the equals sign `=`. To evaluate (or re-evaluate) all cells in a table, use `<leader>dt` while inside a table. Disorganiser puts the result of the formula to the right of the formula, preceeded by an equals sign. For example, a cell containing the formula `=2 + 2` would, after evaluation with `<leader>dt`, become `=2 + 2=4`.

The `sum` function is supported, to sum a row or column of cells. For example, `=sum([1..before this])` sums all values in the column containing this cell, starting at row 1 and ending at the row just before this cell. See "Cell references in tables" for more information on cell references.

*Cell references in tables*: In formulae, you can reference other cells by using the syntax `[row column]`. Both `row` and `column` can be either absolute or relative references.

To specify an absolute reference, specify the index as a number starting from 0. For example, `[0 0]` references the first cell of the table, in the top left.

To specify a relative reference, write an at sign `@` followed by a number specifing the number of cells to move relative to the current cell. For example, `[@-1 @0]` specifies the cell above this one; `[@0 @-1]` specifies the cell to the left, `[@2 @3]` specifies the cell two cells below and three cells to the right, and so on.

*Ranges*: You can also specify cell ranges. To do so, write an absolute or relative reference, two dots `..`, and another absolute or relative reference. For example, `[1..@-1 @0]` specifies all cells in this cell's column, from the second row to the row just above this cell. This is useful for `sum`, where you can write `=sum([1..@-1 @0])` to sum the column of numbers above (excluding, presumably, the title).

For readability, you can specify `before` instead of `@-1`, `after` instead of `@1`, and `this` instead of `@0`. So the above formula could be rewritten as `=sum([1..before this])`.


