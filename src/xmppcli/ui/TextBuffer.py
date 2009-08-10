import urwid
from xmppcli import log

class LineWalker(urwid.ListWalker):
    def __init__(self, limit = 1000):
        self.limit = limit
        self.lines = []
        self.focus = 0

    def get_focus(self):
        return self.get(self.focus)

    def set_focus(self, focus):
        self.focus = focus
        self._modified()

    def get_next(self, at):
        return self.get(at + 1)

    def get_prev(self, at):
        return self.get(at - 1)

    def get(self, at):
        if ((at < 0) or (len(self.lines) <= at)):
            return None, None
        else:
            return self.lines[at], at

    def append(self, line):
        if len(self.lines) > self.limit:
            del self.lines[:1]
        self.lines.append(urwid.Text(line))
        self.set_focus(len(self.lines) - 1)

class TextBuffer(urwid.ListBox):
    def __init__(self, name):
        self.name = name
        self.walker = LineWalker()
        urwid.ListBox.__init__(self, self.walker)

    def append(self, buff):
        self.walker.append(buff)

### File object interface for logging
class LogBuffer(TextBuffer):
    def __init__(self, name, layout):
        TextBuffer.__init__(self, name)
        self.layout = layout

    def write(self, buff):
        self.append(buff.rstrip("\r\n"))
        self.layout.wake()

    def flush(self):
        pass
