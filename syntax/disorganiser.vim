" Disorganiser (org-mode alternative) syntax file.

if exists("b:current_syntax")
	finish
endif

syn cluster disInline contains=disTag,disTODO,disDONE,disLink,disDate,disFoldStart,disFoldEnd

syn match disTag ':[A-Za-z0-9._@:]\+:'
syn region disLink matchgroup=disSubtle start="\[\[" end="\]\]"
syn match disTODO 'TODO\>'
syn match disDONE 'DONE\>'
syn match disDate '<\d\d\d\d-\d\d-\d\d\( \a\a\a\)\?>'
syn match disFoldStart '{{{'
syn match disFoldEnd '}}}'
syn match disTableBar '|' contained

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

" Lists
syn region disUL start="^[ \t]\+[-+\*]" end="$" contains=@disInline

" Tables
syn region disTR start="^[ \t]*|" end="$" contains=@disInline,disTableBar

" Explicitly defining colours. Yes! Very naughty.
hi disH1 guifg=#FF7799
hi disH2 guifg=#FFCA91
hi disH3 guifg=#FF8BFA
hi disH4 guifg=#7390E8
hi disH5 guifg=#FDAD57
hi disH6 guifg=#F57CBB
hi disH7 guifg=#B2DABB
hi disH8 guifg=#707DE0
hi disUL guifg=#bc66ff
hi disTODO guifg=#000000 guibg=#E9954C gui=bold cterm=bold
hi disDONE guifg=#66EB66 gui=bold cterm=bold
hi disLink guifg=#EC9A40
hi disDate guifg=#00CECE
hi disTag guifg=#EA4C5A
hi disSubtle guifg=#444444
hi disHidden guifg=bg
hi disFoldStart guifg=bg
hi disFoldEnd guifg=bg
hi disTableBar guifg=#777777
hi disTR guifg=#778Ad6

let b:current_syntax = "disorganiser"
