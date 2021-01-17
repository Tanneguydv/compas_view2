from typing import Tuple, Union
from OpenGL import GL

from PySide2 import QtCore, QtGui, QtWidgets

from ..camera import Camera
from ..mouse import Mouse


class View(QtWidgets.QOpenGLWidget):
    """Base OpenGL widget."""

    def __init__(self,
                 app,
                 color: Tuple[float, float, float] = (1, 1, 1, 1),
                 selection_color: Tuple[float, float, float] = (0.0, 0.0, 0.0),
                 mode: str = 'shaded'):
        super().__init__()
        self._opacity = 1.0
        self.shader = None
        self.app = app
        self.color = color
        self.mode = mode
        self.selection_color = selection_color
        self.camera = Camera()
        self.mouse = Mouse()
        self.objects = {}

    def clear(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

    def initializeGL(self):
        GL.glClearColor(* self.color)
        GL.glPolygonOffset(1.0, 1.0)
        GL.glEnable(GL.GL_POLYGON_OFFSET_FILL)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthFunc(GL.GL_LESS)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glEnable(GL.GL_POINT_SMOOTH)
        GL.glEnable(GL.GL_LINE_SMOOTH)
        GL.glEnable(GL.GL_POLYGON_SMOOTH)
        self.init()

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode):
        self._mode = mode
        if mode == 'ghosted':
            self._opacity = 0.7
        else:
            self._opacity = 1.0
        if self.shader:
            self.shader.bind()
            self.shader.uniform1f("opacity", self._opacity)
            self.shader.release()
            self.update()

    @property
    def opacity(self):
        return self._opacity

    def init(self):
        pass

    def resizeGL(self, w: int, h: int):
        GL.glViewport(0, 0, w, h)
        self.app.width = w
        self.app.height = h
        self.resize(w, h)

    def resize(self, w: int, h: int):
        pass

    def paintGL(self):
        self.clear()
        self.paint()

    def paint(self):
        pass

    def mouseMoveEvent(self, event):
        if not self.isActiveWindow() or not self.underMouse():
            return
        self.mouse.pos = event.pos()
        dx = self.mouse.dx()
        dy = self.mouse.dy()
        if event.buttons() & QtCore.Qt.LeftButton:
            self.camera.rotate(dx, dy)
            self.mouse.last_pos = event.pos()
            self.update()
        elif event.buttons() & QtCore.Qt.RightButton:
            self.camera.pan(dx, dy)
            self.mouse.last_pos = event.pos()
            self.update()

    def mousePressEvent(self, event):
        if not self.isActiveWindow() or not self.underMouse():
            return
        self.mouse.last_pos = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        if not self.isActiveWindow() or not self.underMouse():
            return
        self.update()

    def wheelEvent(self, event):
        if not self.isActiveWindow() or not self.underMouse():
            return
        degrees = event.delta() / 8
        steps = degrees / 15
        self.camera.zoom(steps)
        self.update()