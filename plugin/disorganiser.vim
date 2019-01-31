python3 <<EOF
import sys
import os
import vim

plugin_dir = os.path.dirname(vim.eval('expand("<sfile>")'))
sys.path.insert(0, plugin_dir)

from disorganiser import dis_indent, dis_indent_subtree, dis_dedent, dis_dedent_subtree, \
	dis_outline_insert_above_children, dis_outline_insert_after_children, \
	dis_outline_insert_above_current,  dis_list_insert_above_children, dis_tab, \
	dis_date_insert, dis_cr, dis_table_reformat

EOF
