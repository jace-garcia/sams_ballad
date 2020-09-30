# Main control code for Sam's Ballad, a midi-piano performance
# dependant visual story, as produced by
# Juan Carlos Garcia and Robby Schieffer.

import sys
sys.path.append('..')
from common.core import *
from common.gfxutil import *
from game import GameWidget
from menu import MenuWidget

class MainWidget(BaseWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        self.menu = MenuWidget(self.load_game_cb)
        self.add_widget(self.menu)

        self.load_game = False
        self.game = None

    def load_game_cb(self):
        self.remove_widget(self.menu)
        self.menu = None
        self.load_game = True
        self.game = GameWidget(restart_cb=self.restart_game_cb, exit_cb=self.exit_game_cb)
        self.add_widget(self.game)

    def exit_game_cb(self):
        # TODO: Fix audio toggle bug, music still plays after you exit
        self.remove_widget(self.game)
        self.game = None
        self.load_game = False
        self.menu = MenuWidget(self.load_game_cb)
        self.add_widget(self.menu)

    def restart_game_cb(self):
        self.remove_widget(self.game)
        self.game = GameWidget(restart_cb=self.restart_game_cb, exit_cb=self.exit_game_cb)
        self.add_widget(self.game)

    def on_update(self):
        if self.load_game and self.game:
            self.game.on_update()
        else:
            if self.menu:
                self.menu.on_update()

if __name__ == "__main__":
    run(MainWidget)