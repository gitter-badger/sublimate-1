# -*- coding: utf-8 -*-
from .canvas import Canvas, SuperCanvas, UrwidCanvasAdapter
from .events import MouseEvent, KeyboardEvent


class Widget(object):

    parent, focus = None, None

    def create_widget(self, cls, *args, **kwargs):
        widget = cls(*args, **kwargs)
        widget.parent = self
        return widget

    @property
    def focused(self):
        parent, focus = self.parent, self.focus or self
        while parent:
            if parent.focus != focus:
                return False
            parent = parent.parent
        return True

    @property
    def has_focus(self):
        return (self.focus == self) and self.focused

    def capture_focus(self, widget=None):
        parent = self
        focus = widget or self.focus or self
        while parent:
            parent.focus = focus
            parent = parent.parent

    def take_focus(self):
        self.capture_focus(self)

    def on_keyboard(self, event):
        name = 'on_%s' % event.replace(' ', '_')
        method = getattr(self, name, None)
        if method and method():
            return True
        if self.parent:
            return self.parent.on_keyboard(event)

    def on_mouse(self, event):
        name = 'on_%s' % event.replace(' ', '_')
        method = getattr(self, name, None)
        if method and method():
            return True
        if self.parent:
            return self.parent.on_mouse(event)

    # def render_offset(self, canvas, offset_x, offset_y):
    #     self.render(SuperCanvas(canvas, 
    #                             offset_x, offset_y,
    #                             self.width, self.height))


class ContainerWidget(Widget):

    def __init__(cls, children):
        self.children = children
        for child in self.children:
            child.parent = self

    def add_widget(self, widget):
        widget.parent = self
        self.children.append(widget)


class UrwidWidgetAdapter(object):
    def __init__(self, widget):
        self.widget = widget

    def selectable(self):
        return True

    def sizing(self):
        return frozenset(['box', 'flow', 'fixed'])

    def rows(self, size, focus=False):
        return self.widget.get_height(size[0])

    def mouse_event(self, size, event, button, x, y, focus):
        if self.canvas:
            target = self.canvas.get_mouse_target(x, y)
            if target:
                return target.on_mouse(MouseEvent(event, button))
        return False

    def keypress(self, size, key):
        if self.widget.focus:
            return self.widget.focus.on_keyboard(KeyboardEvent(key))
        return False

    def render(self, size, focus=False):
        if len(size) == 2:  
            self.canvas = Canvas(size[0], size[1])
        elif len(size) == 1:
            self.canvas = Canvas(size[0], self.widget.get_height(size[0]))
        else:
            self.canvas = Canvas(self.widget.width, self.widget.height)
        self.widget.render(self.canvas)
        return UrwidCanvasAdapter(self.canvas)
