python3 <<EOF
import sys
import os
import vim

plugin_dir = os.path.dirname(vim.eval('expand("<sfile>")'))
sys.path.insert(0, plugin_dir)

from disorganiser import dis_indent, dis_indent_subtree, dis_dedent, dis_dedent_subtree, \
	dis_outline_insert_above_children, dis_outline_insert_above_current, dis_fold_cycle

EOF

noremap << :python3 dis_dedent()<CR>
noremap >> :python3 dis_indent()<CR>
noremap >ar :python3 dis_indent_subtree()<CR>
noremap <ar :python3 dis_dedent_subtree()<CR>
noremap <S-CR> :python3 dis_outline_insert_above_children()<CR>
noremap <leader>hh :python3 dis_outline_insert_above_children()<CR>
noremap <C-S-CR> :python3 dis_outline_insert_above_current()<CR>
noremap <leader>hN :python3 dis_outline_insert_above_current()<CR>
noremap <TAB> :python3 dis_fold_cycle()<CR>

" TODO I think we can use foldmethod = marker and then manually add and remove
" markers. It means adding {{{ and }}} onto lines, which is a bit lame, but
" they can be automatically added and removed with <TAB> I guess.
" When we press tab on a line, remove any fold markers, then add one, then
" walk down the org tree until we get fewer stars (removing any nested folds
" along the way), add an end-fold marker, then do the fold.
" This might produce 'poos', especially with manual editing, but should be
" pretty fast -- two passes over the affected lines (one in python, one in
" vim), so O(N) with number of folded lines.

set foldmethod=marker
