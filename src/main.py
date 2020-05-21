# Main control code for Sam's Ballad, a midi-piano performance
# dependant visual story, as produced by
# Juan Carlos Garcia and Robby Schieffer.

import sys
sys.path.append('..')
from common.core import *
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from performer import PerformerWidget
from story import StoryWidget


class MainWidget(BaseWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        # self.layout = BoxLayout(orientation='vertical')
        self.story_widget = StoryWidget()
        self.performer_widget = PerformerWidget(self.end_story_cb, self.continue_story_cb)
        # self.layout.add_widget(self.story_widget)
        # self.layout.add_widget(self.performer_widget)
        # self.add_widget(self.layout)

        self.add_widget(self.story_widget)
        self.add_widget(self.performer_widget)

        self.continue_story = True
        self.ended_story = False

    
    def continue_story_cb(self):
        self.continue_story = True

    def end_story_cb(self):
        self.continue_story = False
        self.ended_story = True

    def on_key_down(self, keycode, modifiers):
        pass

    def on_update(self):
        if not self.continue_story:
            self.story_widget.end_story()
        
        if self.continue_story and self.ended_story:
            self.ended_story = False
            self.story_widget.continue_story()



if __name__ == "__main__":
    run(MainWidget)
