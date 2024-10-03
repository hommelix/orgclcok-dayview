# OrgClock-DayView

An agenda view for daily clocked time in orgmode. This is a plugin for my VimOrganizer setup, to parse the current buffer and list the time clocked in a day.

It works for any buffer with an orgmode file with clocks defined as

    :LOGBOOK:
    :CLOCK: [yyyy-mm-dd Mon ha:ma]--[yyyy-mm-dd Mon hb:mb] => hh:mm
    :END: 

This line will be represented as below in the daily view

    ------- ha:ma --------------
    Task blabla
    ------- hb:mb --------------

So that a complete timeline of the day is visualised like in some paper agenda.

The view can be closed with ``q``.
Previous day can be viewed with ``H``.
Next day can be viewed with ``L``.

# Requirements

This plugin works with vim8 with +python3 and VimOrganizer for example.
It may work with other orgmode vim plugin, but I haven't tested that.

# How to install

## vim-plug

Include the following in the [vim-plug](https://github.com/junegunn/vim-plug)
section of your `~/.vimrc`:

    Plug 'hommelix/orgclock-dayview', { 'for': 'org' }

