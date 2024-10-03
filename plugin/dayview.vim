" How to add a custom module to python in vim
" from
" https://robertbasic.com/blog/import-custom-python-modules-in-vim-plugins/
let g:plugin_path = expand('<sfile>:p:h')

if !exists('g:orgclock_window_position')
    let g:orgclock_window_position = 'bottom'
endif


function OrgClockDayView(...)
    if a:0 < 1
        let dayspec = 'today'
    else
        let dayspec = a:1
    endif
    
python3 << endpython

import os, sys, vim

# Get the vim variable to Python
plugin_path = vim.eval('g:plugin_path')
# Get the absolute path to the module
python_module_path = os.path.abspath(plugin_path)
# Append it to the system paths
sys.path.append(python_module_path)

# now import
import dayview

dayspec = vim.eval('dayspec')
day = dayview.tellday(dayspec)
dayprev = dayview.tellday(day, -1)
daynext = dayview.tellday(day, +1)

cb = vim.current.buffer
clocks = dayview.read_buffer(cb)

report = dayview.ClockReport(clocks.select(day, day))
content = report.buffer()

vim.command('new')
cb = vim.current.buffer 
for line in content.split('\n'):
    cb.append(line)

header = f'Clocked time on {day}'
cb[0] = f'<< {dayprev}{header: ^46}{daynext} >>'

vim.command(f"map <buffer> H :q!<CR>:call OrgClockDayView('{dayprev}')<CR>")
vim.command(f"map <buffer> L :q!<CR>:call OrgClockDayView('{daynext}')<CR>")
endpython

nnoremap <buffer> q :q!<CR>

endfunction

command -nargs=? Dayview call OrgClockDayView(<f-args>)
