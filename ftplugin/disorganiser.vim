" Key mappings specific to .org files

noremap <buffer> << :python3 dis_dedent()<CR>
noremap <buffer> >> :python3 dis_indent()<CR>
noremap <buffer> >c :python3 dis_indent_subtree()<CR>
noremap <buffer> <c :python3 dis_dedent_subtree()<CR>
noremap <buffer> <CR> :python3 dis_cr()<CR>
noremap <buffer> <leader>ha :python3 dis_outline_insert_after_children()<CR>
noremap <buffer> <S-CR> :python3 dis_outline_insert_above_children()<CR>
inoremap <buffer> <S-CR> <ESC>:python3 dis_outline_insert_above_children()<CR>
noremap <buffer> <leader>hj :python3 dis_outline_insert_above_children()<CR>
noremap <buffer> <C-S-CR> :python3 dis_outline_insert_above_current()<CR>
noremap <buffer> <leader>hk :python3 dis_outline_insert_above_current()<CR>
noremap <buffer> <TAB> :python3 dis_tab()<CR>
noremap <buffer> <leader>ddc :python3 dis_date_insert()<CR>
inoremap <buffer> <D-d>d <ESC>:python3 dis_date_insert()<CR>a
noremap <buffer> <leader>dl :python3 dis_list_insert_above_children()<CR>
inoremap <buffer> <D-d>t <ESC>:python3 dis_table_reformat()<CR>a
noremap <buffer> <leader>dt :python3 dis_table_reformat()<CR>

" Compatibility: disable rainbow parentheses in org files (it steals the colouring for URLs)
if (exists('g:rainbow_active') && g:rainbow_active)
	auto syntax disorganiser call rainbow#clear()
endif

" Disorganiser uses {{{ and }}} to indicate folds, i.e. Vim's marker method.
set foldmethod=marker
