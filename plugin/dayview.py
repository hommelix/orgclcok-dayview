import datetime as dt
import re
from dataclasses import dataclass, field
from typing import List, Optional
import time


def tellday(dayspec=None, dayoffset=0):
    """
    convert a dayspec into a date in isoformat

    accept following dayspec
    'today'
    'yesterday'
    'tomorrow'
    '-3d'
    '+5d'
    'YYYY-mm-dd'
    """

    if dayspec == None or dayspec == 'today':
        day = dt.date.today()
    elif dayspec == 'yesterday':
        day = dt.date.today() + dt.timedelta(days=-1)
    elif dayspec == 'tomorrow':
        day = dt.date.today() + dt.timedelta(days=+1)
    elif dayspec.startswith('-') or dayspec.startswith('+'):
        offset = int(dayspec[0:-1])
        if dayspec[-1] == 'd':
            day = dt.date.today() + dt.timedelta(days=offset)
    elif re.fullmatch(r'\d{4}-\d{2}-\d{2}', dayspec):
        day = dt.date.fromisoformat(dayspec)
    day = day + dt.timedelta(days=dayoffset)
    return day.isoformat()


# dayview report
# --------------
#
# 4 lines per hour, each line is 15 mins
# a line may look like
# -- hh:mm - PJN - Task ---------------
#
# For longer task it may look like
# -- hh:mm - PJN - Task ---------------
#  |
#  +-> hh:mm


@dataclass
class ProjectClock:
    start: dt.datetime
    end: dt.datetime
    pjn: str
    description: str

    @property
    def duration(self):
        return (self.end - self.start).seconds / 3600


class ProjectClocks(list):  # List['ProjectClock']
    @property
    def thismonth(self):
        today = dt.datetime.now()
        monthstart = dt.datetime(today.year, today.month, 1)
        if today.month < 12:
            monthend = dt.datetime(
                today.year, today.month + 1, 1, 23, 59
            ) - dt.timedelta(days=1)
        else:
            monthend = dt.datetime(today.year + 1, 1, 1, 23, 59) - dt.timedelta(days=1)
        return ProjectClocks(
            [c for c in self if ((monthstart <= c.start) and (c.start <= monthend))]
        )

    @property
    def thisweek(self):
        today = dt.datetime.now()
        weekstart = dt.datetime(today.year, today.month, today.day) - dt.timedelta(
            days=today.weekday()
        )
        weekend = weekstart + dt.timedelta(days=6, hours=23, minutes=59)
        return ProjectClocks(
            [c for c in self if ((weekstart <= c.start) and (c.start <= weekend))]
        )

    @property
    def today(self):
        today = dt.datetime.now()
        daystart = dt.datetime(today.year, today.month, today.day)
        dayend = dt.datetime(today.year, today.month, today.day, 23, 59)
        return ProjectClocks(
            [c for c in self if ((daystart <= c.start) and (c.start <= dayend))]
        )

    def select(self, after: str, before: str, pjns: Optional[List[str]] = None):
        start = dt.datetime(*(time.strptime(after, '%Y-%m-%d')[0:3]), 0, 0)
        end = dt.datetime(*(time.strptime(before, '%Y-%m-%d')[0:3]), 23, 59)
        if pjns is None:
            return ProjectClocks(
                [c for c in self if ((start <= c.start) and (c.start <= end))]
            )
        else:
            return ProjectClocks(
                [
                    c
                    for c in self
                    if ((start <= c.start) and (c.start <= end) and (c.pjn in pjns))
                ]
            )


ORGCLKREGEXP = r'CLOCK:\s\[(.*)\]--\[(.*)\].*'


def read_org(filepath):
    clocks: ProjectClocks = ProjectClocks()
    with open(filepath) as orgf:
        buffer = orgf.readlines()
    return read_buffer(buffer)


def read_buffer(buffer):
    clocks: ProjectClocks = ProjectClocks()
    lineno = 0
    for line in buffer:
        lineno = lineno + 1
        if line.startswith('*'):
            [description] = re.findall(r'^\*+ (.*)\s*$', line)
        elif ':PJN:' in line:
            pjn = line.split(':PJN:')[1].strip()[4:]
            if pjn == '':
                print(f'PJN parsing error {lineno}: {line}')
        elif ':CLOCK:' in line:
            try:
                [(startstr, endstr)] = re.findall(ORGCLKREGEXP, line)
            except ValueError:
                print(f'CLOCK parsing error {lineno}: {line}')
            startday = startstr.split(' ')
            startclk = dt.datetime(
                *(time.strptime(startday[0], '%Y-%m-%d')[0:3]),
                *(time.strptime(startday[2], '%H:%M')[3:5]),
            )
            endday = endstr.split(' ')
            endclk = dt.datetime(
                *(time.strptime(endday[0], '%Y-%m-%d')[0:3]),
                *(time.strptime(endday[2], '%H:%M')[3:5]),
            )
            clock = ProjectClock(startclk, endclk, pjn, description)
            clocks.append(clock)
    return clocks


@dataclass
class ClockReport:
    _clocks: 'ProjectClocks'

    def buffer(self):
        lastend = None
        result = ''
        # sort _clocks in start order
        clocks = sorted(self._clocks, key=lambda c: c.start)
        for c in clocks:
            if c.start != lastend:
                result = result + '\n'
                startstr = f'{c.start:%Y-%m-%d %H:%M}'
                result = result + f'{startstr:-^72}\n'
            result = result + f'{c.pjn}: {c.description}\n'
            endstr = f'{c.end:%Y-%m-%d %H:%M}'
            result = result + f'{endstr:-^72}\n'
            lastend = c.end
        if result.startswith('\n'):
            result = result[1:]
        hours = sum([c.duration for c in clocks])
        result = result + f'\nWorked hours: {hours}\n'
        return result
