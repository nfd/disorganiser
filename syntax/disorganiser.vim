" Disorganiser (org-mode alternative) syntax file.

if exists("b:current_syntax")
	finish
endif

syn cluster disInline contains=disTag,disTODO,disDONE,disLink,disDate,disFoldStart,disFoldEnd

syn match disTag ':[A-Za-z0-9._@:]\+:'
syn region disLiteral matchgroup=disSubtle start="`" end="`\|$"
syn region disLink matchgroup=disSubtle start="\[\[" end="\]\]"
syn match disTODO 'TODO\>'
syn match disDONE 'DONE\>'
syn match disDate '<\d\d\d\d-\d\d-\d\d\( \a\a\a\)\?>'
syn match disFoldStart '{{{'
syn match disFoldEnd '}}}'
syn region disQuote1 start="^>" end="$" contains=@disInline
syn region disQuote2 start="^> \?>" end="$" contains=@disInline
syn region disQuote3 start="^> \?> \?>" end="$" contains=@disInline

" Headings, highlighting all asterisks.
"syn region disH1 start="^\* " end="$" contains=@disInline
"syn region disH2 start="^\*\* " end="$" contains=@disInline
"syn region disH3 start="^\*\*\* " end="$" contains=@disInline
"syn region disH4 start="^\*\*\*\* " end="$" contains=@disInline
"syn region disH5 start="^\*\*\*\*\* " end="$" contains=@disInline
"syn region disH6 start="^\*\*\*\*\*\* " end="$" contains=@disInline
"syn region disH7 start="^\*\*\*\*\*\*\* " end="$" contains=@disInline
"syn region disH8 start="^\*\*\*\*\*\*\*\* " end="$" contains=@disInline

" Headings, hiding all but the final asterisk.
syn region disH1 start="^\* " end="$" contains=@disInline
syn region disH2 matchgroup=disHidden start="^\*\(\* \)\@=" end="$" contains=@disInline
syn region disH3 matchgroup=disHidden start="^\*\*\(\* \)\@=" end="$" contains=@disInline
syn region disH4 matchgroup=disHidden start="^\*\*\*\(\* \)\@=" end="$" contains=@disInline
syn region disH5 matchgroup=disHidden start="^\*\*\*\*\(\* \)\@=" end="$" contains=@disInline
syn region disH6 matchgroup=disHidden start="^\*\*\*\*\*\(\* \)\@=" end="$" contains=@disInline
syn region disH7 matchgroup=disHidden start="^\*\*\*\*\*\*\(\* \)\@=" end="$" contains=@disInline
syn region disH8 matchgroup=disHidden start="^\*\*\*\*\*\*\*\(\* \)\@=" end="$" contains=@disInline

" Unordered lists (start with - or *)
syn region disUL start="^[ \t]\+[-+\*]" end="$" contains=@disInline

" Tables
syn region disTR start="^[ \t]*|" end="$" contains=@disInline,disTableBar,disTableFormula
" ... 'end' in disTableFormula says: if we end with =, highlight it as part of
"      the formula. If we end with | (end of cell), don't highlight it.
syn region disTableFormula start="[ \t]*=" end="=\|\(|\)\@=" contained
syn match disTableBar '|' contained

" Explicitly defining colours. Yes! Very naughty.
" ctermfg colours are derived from the hex using this gist:
" https://gist.github.com/MicahElliott/719710#gistcomment-1442838
hi Normal ctermbg=0 ctermfg=231
hi disH1 ctermfg=210 guifg=#FF7799
hi disH2 ctermfg=222 guifg=#FFCA91
hi disH3 ctermfg=213 guifg=#FF8BFA
hi disH4 ctermfg=68 guifg=#7390E8
hi disH5 ctermfg=215 guifg=#FDAD57
hi disH6 ctermfg=211 guifg=#F57CBB
hi disH7 ctermfg=151 guifg=#B2DABB
hi disH8 ctermfg=68 guifg=#707DE0
hi disUL ctermfg=135 guifg=#bc66ff
hi disTODO ctermfg=0 ctermbg=173 guifg=#000000 guibg=#E9954C gui=bold cterm=bold
hi disDONE ctermfg=77 guifg=#66EB66 gui=bold cterm=bold
hi disLink ctermfg=209 guifg=#EC9A40
hi disDate ctermfg=44 guifg=#00CECE
hi disTag ctermfg=167 guifg=#EA4C5A
hi disSubtle ctermfg=59 guifg=#444444
hi disHidden ctermfg=bg guifg=bg
hi disFoldStart ctermfg=bg guifg=bg
hi disFoldEnd ctermfg=bg guifg=bg
hi disTableBar ctermfg=61 guifg=#6345A0
hi disTR ctermfg=104 guifg=#778Ad6
hi disTableFormula ctermfg=98 guifg=#7A67c6
hi disQuote1 ctermfg=73 guifg=#67b2a4
hi disQuote2 ctermfg=107 guifg=#8bb569
hi disQuote3 ctermfg=143 guifg=#a9b569
hi disLiteral ctermfg=157 guifg=#b4edb1

let b:current_syntax = "disorganiser"
