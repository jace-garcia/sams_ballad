import sys
sys.path.append('..')
from common.gfxutil import *
from menu import point_inbounds

class PauseMenu(InstructionGroup):
    def __init__(self, restart_game_cb, cont_game_cb, exit_game_cb, status=True):
        super(PauseMenu, self).__init__()
        w, h = Window.width, Window.height
        self.status = status # paused or unpaused
        self.restart_game_cb = restart_game_cb
        self.cont_game_cb = cont_game_cb
        self.exit_game_cb = exit_game_cb
        self.cont_img = '../data/img/text/continue.png'
        self.exit_img = '../data/img/text/exit.png'
        self.restart_img = '../data/img/text/restart.png'

        self.cont_boundaries = []
        self.exit_boundaries = []
        self.restart_boundaries = []

        self.anchor_pos = (w/4, h * 2/3)
        self.y_offset = - h/8
        self.img_height = h/12

        self.on_layout((w, h))

    def on_touch_down(self, touch):
        pos = touch.pos
        if point_inbounds(pos, self.cont_boundaries):
            print('continue clicked')
            self.cont_game_cb()
        if point_inbounds(pos, self.exit_boundaries):
            print('exit clicked')
            self.exit_game_cb()
        if point_inbounds(pos, self.restart_boundaries):
            print('restart clicked')
            self.restart_game_cb()

    def switch_status(self):
        self.status = not self.status
        self.on_layout((Window.width, Window.height))

    def on_layout(self, win_size):
        self.clear()
        w, h = win_size
        self.anchor_pos = (w/4, h * 3/4)
        self.y_offset = -h/8
        self.img_height = h/12

        if (self.status):
            self.add(Color(1, 0, 0))

            cont_pos = (self.anchor_pos[0] + w/12, self.anchor_pos[1])
            cont_size = (w * 1/3, self.img_height)
            self.add(Rectangle(source=self.cont_img, pos=cont_pos, size=cont_size))
            self.cont_boundaries = [(cont_pos[0], cont_pos[0] + cont_size[0]), (cont_pos[1], cont_pos[1] + cont_size[1])]

            restart_pos = (self.anchor_pos[0], self.anchor_pos[1] + self.y_offset)
            restart_size = (w * 1/2, self.img_height)
            self.add(Rectangle(source=self.restart_img, pos=restart_pos, size=restart_size))
            self.restart_boundaries = [(restart_pos[0], restart_pos[0] + restart_size[0]), (restart_pos[1], restart_pos[1] + restart_size[1])]

            exit_pos = (self.anchor_pos[0] + w*9/48, restart_pos[1] + self.y_offset)
            exit_size = (w * 1/8, h/12)
            self.add(Rectangle(source=self.exit_img, pos=exit_pos, size=exit_size))
            self.exit_boundaries = [(exit_pos[0], exit_pos[0] + exit_size[0]), (exit_pos[1], exit_pos[1] + exit_size[1])]
