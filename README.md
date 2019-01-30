Disorganiser
===

A task management plug-in for Vim, heavily "inspired by" emacs org-mode and vim-orgmode (though not sharing any code with those projects).

Probably contains 1% of the functionality of vim-orgmode; on the other hand, runs at full speed even when your org file is larger than a few kilobytes.

Requires a recent Vim with Python 3 support.

License: Disorganiser is available under two sets of terms:

If public domain licensing is valid in your jurisdiction, you may use the code in any way you wish, no attribution required.

Alternatively, you may use this code under the terms of the [MIT license](https://opensource.org/licenses/MIT).

Installation
---

Vim 8 with native plugin support: clone this repository into your `~/.vim/pack/whatever/start` directory.

Mappings
---

In normal mode:

`CR` or `<leader>hn`     : Insert heading at same level as current, after any children  
`S-CR` or `<leader>hh`   : Insert heading at same level as current, immediately below current line (also works for lists)  
`C-S-CR` or `<leader>hN` : Insert heading at same level as current, immediately above current line (also works for lists)  
`<leader>ll`             : Insert list at level one lower than current list or heading  
`<<`                     : Dedent current heading  
`<ar`                    : Dedent current heading and all children  
`>>`                     : Indent current heading  
`>ar`                    : Indent current heading and all children  
`TAB`                    : Fold current heading and children (if not folded) or unfold current heading and children (if folded)  
`<leader>sa`             : Insert current date  

In insert mode:

`<S-CR>`                 : Insert heading at same level as current, immediately below current line (same as normal mode)
`<D-d>d`                 : Insert current date (same as <leader>sa)

When editing tables, in normal mode:

`<TAB>`                  : Reformat table and move to next cell, or next row (if at end), creating a new row if necessary
`<CR>`                   : Reformat table and move to first cell of next row, creating a new row if necessary

