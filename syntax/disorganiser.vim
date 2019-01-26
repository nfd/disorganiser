" Disorganiser (org-mode alternative) syntax file.

if exists("b:current_syntax")
	finish
endif

let b:current_syntax = 'orgmode'

syn cluster orgmodeInline contains=orgmodeTODO,orgmodeDONE,orgmodeLink,orgmodeDate,orgmodeFoldStart,orgmodeFoldEnd

syn region orgmodeLink matchgroup=orgmodeSubtle start="\[\[" end="\]\]"

syn match orgmodeTODO 'TODO '
syn match orgmodeDONE 'DONE '
syn match orgmodeDate '<\d\d\d\d-\d\d-\d\d\( \a\a\a\)\?>'
syn match orgmodeFoldStart '{{{'
syn match orgmodeFoldEnd '}}}'

" Headings, highlighting all asterisks.
"syn region orgmodeH1 start="^\* " end="$" contains=@orgmodeInline
"syn region orgmodeH2 start="^\*\* " end="$" contains=@orgmodeInline
"syn region orgmodeH3 start="^\*\*\* " end="$" contains=@orgmodeInline
"syn region orgmodeH4 start="^\*\*\*\* " end="$" contains=@orgmodeInline
"syn region orgmodeH5 start="^\*\*\*\*\* " end="$" contains=@orgmodeInline
"syn region orgmodeH6 start="^\*\*\*\*\*\* " end="$" contains=@orgmodeInline
"syn region orgmodeH7 start="^\*\*\*\*\*\*\* " end="$" contains=@orgmodeInline
"syn region orgmodeH8 start="^\*\*\*\*\*\*\*\* " end="$" contains=@orgmodeInline

" Headings, hiding all but the final asterisk.
syn region orgmodeH1 start="^\* " end="$" contains=@orgmodeInline
syn region orgmodeH2 matchgroup=orgmodeHidden start="^\*\(\* \)\@=" end="$" contains=@orgmodeInline
syn region orgmodeH3 matchgroup=orgmodeHidden start="^\*\*\(\* \)\@=" end="$" contains=@orgmodeInline
syn region orgmodeH4 matchgroup=orgmodeHidden start="^\*\*\*\(\* \)\@=" end="$" contains=@orgmodeInline
syn region orgmodeH5 matchgroup=orgmodeHidden start="^\*\*\*\*\(\* \)\@=" end="$" contains=@orgmodeInline
syn region orgmodeH6 matchgroup=orgmodeHidden start="^\*\*\*\*\*\(\* \)\@=" end="$" contains=@orgmodeInline
syn region orgmodeH7 matchgroup=orgmodeHidden start="^\*\*\*\*\*\*\(\* \)\@=" end="$" contains=@orgmodeInline
syn region orgmodeH8 matchgroup=orgmodeHidden start="^\*\*\*\*\*\*\*\(\* \)\@=" end="$" contains=@orgmodeInline

" Explicitly defining colours. Yes! Very naughty.
hi orgmodeH1 guifg=#F645A0
hi orgmodeH2 guifg=#FCEF70
hi orgmodeH3 guifg=#369BED
hi orgmodeH4 guifg=#67EE67
hi orgmodeH5 guifg=#FDAD57
hi orgmodeH6 guifg=#F57CBB
hi orgmodeH7 guifg=#B2DABB
hi orgmodeH8 guifg=#707DE0
hi orgmodeTODO guifg=#000000 guibg=#E9954C gui=bold cterm=bold
hi orgmodeDONE guifg=#66EB66 gui=bold cterm=bold
hi orgmodeLink guifg=#EC9A40
hi orgmodeDate guifg=#079290
hi orgmodeSubtle guifg=#444444
hi orgmodeHidden guifg=bg
hi orgmodeFoldStart guifg=bg
hi orgmodeFoldEnd guifg=bg

