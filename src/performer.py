# For the performer functionality of Sam's Ballad

import sys
sys.path.append('..')
from common.core import *
from common.audio import *
from common.clock import *
from common.metro import *
from common.gfxutil import *
from common.mixer import *
from common.wavegen import *
from common.wavesrc import WaveBuffer, WaveFile

from kivy.graphics import Translate

import rtmidi

# Lowest piano key : 21
# Highest piano key: 108

# global params
nowbar_w_pct = 0.33 
time_span = 10.0
lane_w_pct = 0.0125
square_h_pct = 0.01
slop_window = 0.1 # 100ms in either direction
circle_fifths = ['F', 'C', 'G', 'D', 'A', 'E', 'B']

# for clefs and keys, p for prime, s for subprime
bass_staff_line_notes = ['Gs', 'B', 'D', 'F', 'Ap']
all_bass_clef_notes = {'Gs':'A', 'A':'B', 'B':'C', 'C':'D', 'D':'E', 'E':'F', 'F':'G', 'G':'Ap', 'Ap':'Bp'}
treble_staff_line_notes = ['Es', 'Gs', 'B', 'D', 'Fp']
all_treble_clef_notes = {'Es': 'Fs', 'Fs':'Gs', 'Gs':'A', 'A':'B', 'B':'C', 'C':'D', 'D':'E', 'E':'F', 'F':'G'}
bass_anchor_note = ('A', 45, None) # letter, midi num, position
treble_anchor_note = ('A', 69, None)

clef_size = None
line_spacing = None

barline_scalar = 4 / 12
bottom_barline_scalar = .1

class PerformerWidget(BaseWidget):
    def __init__(self, end_callback, continue_callback):
        super(PerformerWidget, self).__init__()

        self.end_callback = end_callback # true end should also end music play and probably do other stuff like display 'You Lost'
        self.continue_callback = continue_callback

        song_base_path = '../data/pieces/chill_cycle/chill_cycle'

        # Getting song meta, for now assuming one key per piece
        self.clefs, self.key = parse_piece_meta('../data/pieces/chill_cycle/chill_cycle_meta.txt')
        # music part displays
        self.part_displays = {}
        for clef in self.clefs:
            m = MusicPartDisplay(clef=clef, key=self.key)
            self.part_displays[clef] = m
        
        self.song_data  = SongData(song_base_path)
        self.display    = GameDisplay(self.song_data, self.part_displays)
        self.audio_ctrl = AudioController(song_base_path)
        self.player     = Player(self.song_data, self.audio_ctrl, self.display, self.end_callback, self.continue_callback)

        self.canvas.add(self.display)

        # midi set up
        try:
            self.midi_in = open_midi_in("Digital Piano", self.on_midi_in)
            self.midi_out = open_midi_out("Digital Piano")
        except:
            print('NO KEYBOARD ATTACHED')

    def on_key_down(self, keycode, modifiers):
        # play / pause toggle
        if keycode[1] == 'p':
            self.audio_ctrl.toggle()

    def on_midi_in(self, message, data):
        # cmd = 144 means key down
        # cmd = 128 means key up
        cmd, key, vel = message[0]

        if cmd == 144:
            self.player.on_key_down(key)
        
        print("cmd: ", cmd)
        print("key: ", key)
        print("vel: ", vel)

    # handle changing displayed elements when window size changes
    def on_layout(self, win_size):
        w, h = win_size

        self.display.on_layout(win_size)
    
    def on_update(self):
        self.audio_ctrl.on_update()

        now = self.audio_ctrl.get_time()
        self.player.on_update(now)
        self.display.on_update(now)

def parse_piece_meta(path):
    load_clefs = False
    load_key = False
    clefs = []
    key = ()
    lines = open(path).readlines()
    for l in lines:
        l = l.strip()
        if l == "CLEFS":
            load_key = False
            load_clefs = True
            continue
        if l == 'KEY':
            load_clefs = False
            load_key = True
            continue
        
        if load_clefs:
            clefs.append(l)
        
        if load_key:
            l = l.split(',')
            key = (l[0], l[1])

    return clefs, key

def note_from_line(line):
    time, note, other = line.strip().split(',')
    return (float(time), int(note), other)

def bar_from_line(line):
    time, barnum, cont, end = line.strip().split(',')
    cont = cont == 'continue'
    end = end == 'end'

    return (float(time), int(barnum), cont, end)

# Stores bar and note data
class SongData(object):
    def __init__(self, song_base):
        super(SongData, self).__init__()
        self.notes = []
        self.barlines =[]

        notes_file = song_base + '_notes.txt'
        lines = open(notes_file).readlines()
        self.notes = [note_from_line(l) for l in lines]

        bars_file = song_base + '_bars.txt'
        lines = open(bars_file).readlines()
        self.barlines = [bar_from_line(l) for l in lines]

    def get_notes(self):
        return self.notes[:]

    def get_barlines(self):
        return self.barlines[:]

    # return a list indexes of the gems that match this time slice:
    def get_note_indexes_in_range(self, start_time, end_time):
        sublist = [i for i,g in enumerate(self.notes) if start_time <= g[0] < end_time]
        return sublist

# Handles everything about Audio.
#   creates the main Audio object
#   load and plays solo and bg audio tracks
#   creates audio buffers for sound-fx (miss sound)
#   functions as the clock (returns song time elapsed)
class AudioController(object):
    def __init__(self, song_path):
        super(AudioController, self).__init__()

        self.audio = Audio(2)
        self.mixer = Mixer()
        self.audio.set_generator(self.mixer)

        # song tracks
        self.solo_track = WaveGenerator(WaveFile(song_path + "_piano.wav"))
        self.mixer.add(self.solo_track)

        self.bg_track = WaveGenerator(WaveFile(song_path + "_other.wav"))
        self.mixer.add(self.bg_track)

        self.miss_sound = WaveBuffer('../data/game_audio/guitar_miss.wav', 0, 100000)

        self.solo_track.pause()
        self.bg_track.pause()

    # start / stop the song
    def toggle(self):
        self.solo_track.play_toggle()
        self.bg_track.play_toggle()

    # mute / unmute the solo track
    def set_mute(self, mute):
        g = 0 if mute else 1
        self.solo_track.set_gain(g)
        # self.bg_track.set_gain(g)

    # play a sound-fx (miss sound)
    def play_miss(self):
        self.mixer.add(WaveGenerator(self.miss_sound))

    # return current time (in seconds) of song
    def get_time(self):
        return self.solo_track.frame / Audio.sample_rate

    # needed to update audio
    def on_update(self):
        self.audio.on_update()

# convert a time value to a x-pixel value (where time==0 is on the nowbar)
def time_to_xpos(time):
    x_nowbar = (Window.width / 2) * nowbar_w_pct
    m = Window.width / time_span
    x = m * time + x_nowbar
    return x

# convert a lane to y-pixel position
def lane_to_ypos(lane):
    h = Window.height
    lane_height = h * lane_w_pct    
    return  (lane - 2) * lane_height

# converts midi note to y pos on appropiate staff line
def note_to_ypos(note, clef):
    anchor = bass_anchor_note if clef == 'bass' else treble_anchor_note

    if not anchor[2]:
        raise(Exception('Error: ' + clef + 'note not anchored.'))
    if not clef_size:
        raise(Exception('Error: ' + clef + 'size not anchored.'))
    if not line_spacing:
        raise(Exception('Error: line_spacing not anchored.'))

    difference = note - anchor[1]
    sign = 1
    if difference < 0:
        sign = -1
    anchor_y = anchor[2][1]
    ypos = anchor_y + difference * clef_size[1] * line_spacing / 2

    # hacky as fuck, ideally pngs would be better sized
    adjust = None
    abs_diff = abs(difference)
    if abs_diff < 5:
        if abs_diff == 4:
            if sign < 0:
                adjust = 1
            else:
                adjust = 2
        else:
            adjust = 1
    elif abs_diff < 7:
        adjust = 2
    elif abs_diff < 10:
        adjust = 3
    else:
        adjust = 4
    
    # print('note:', note)
    # print('anchor: ', anchor)
    # print('difference: ', difference)
    # print('ypos: ', ypos)

    # TODO: The flats are fucking things up, Db should be at staff line D when in a key with D flatted
    return ypos, sign, adjust

# display for a note at given time with given color
class NoteDisplay(InstructionGroup):
    def __init__(self, note, time, clef, hue): # TODO: Account for 1/4, 1/8, ... type note
        super(NoteDisplay, self).__init__()
        
        self.note = note # midi note number
        self.time = time
        self.clef = clef

        # note image setup
        img_num = self.note % 11
        self.duration = '4'
        self.source = '../data/img/notes/' + str(0) + '_' + self.duration + '.png'
        self.note_size = (clef_size[0]/3, clef_size[1]/2)
        x = time_to_xpos(self.time)
        y, sign, adjust = note_to_ypos(self.note, self.clef)

        small_adjust = .23
        med_low_adjust = 0.35
        med_high_adjust = .8
        big_adjust = 1.0

        adjust_used = None
        if adjust == 1:
            adjust_used = small_adjust
        elif adjust == 2:
            adjust_used = med_low_adjust
        elif adjust == 3:
            adjust_used = med_high_adjust
        else:
            adjust_used = big_adjust


        # print(note, adjust)

        self.y_adjust_factor = -sign * self.note_size[1] * adjust_used
        y += self.y_adjust_factor
        self.img = Rectangle(source=self.source, pos = (x, y), size = self.note_size)
        self.add(self.img)

        # self.color = Color(1,1,1)
        # self.circle = CEllipse(segments=10)
        # self.color2  = Color(hsv=(hue, .9, .7))
        # self.circle2 = CEllipse(segments=10)

        # self.add(self.color)
        # self.add(self.circle)
        # self.add(self.color2)
        # self.add(self.circle2)

        self.hit_start_time = 0
        # self.hit_anim = KFAnim((0, 1, 1), (.4, 0, 5))


    # change to display this gem as being hit
    def on_hit(self):
        self.hit_start_time = -1

    # change to display a passed or missed gem
    def on_pass(self):
        pass
    #     self.color.a = 0.3
    #     self.color2.a = 0.3

    # animate gem (position and animation) based on current time
    def on_update(self, now_time):
        w, h = Window.size

        y, sign, adjust = note_to_ypos(self.note, self.clef)
        y += self.y_adjust_factor
        x = time_to_xpos(self.time - now_time)
        sz = h * square_h_pct
        self.img.pos = (x, y)

        if self.hit_start_time == -1: # signal to trigger hit graphic response:
            self.hit_start_time = now_time

        # if self.hit_start_time != 0: # hit animation is happening now
        #     t = now_time - self.hit_start_time
        #     alpha, sz_factor = self.hit_anim.eval(t)
        #     self.color.a = alpha
        #     self.color2.a = alpha
        #     x = time_to_xpos(self.time - self.hit_start_time)
        #     sz *= sz_factor

        # self.circle.cpos = (x, y)
        # self.circle.size = (sz, sz)

        # self.circle2.cpos = (x, y)
        # self.circle2.size = (sz * .8, sz * .8)

# Displays a single barline on screen
class BarlineDisplay(InstructionGroup):
    def __init__(self, time, barnum, cont_tag=False, cont_cb=None, end_tag=False, end_cb=None):
        super(BarlineDisplay, self).__init__()

        self.time = time
        self.barnum = barnum

        self.color = Color(1,1,1)
        self.line = Line()

        self.cont_tag = cont_tag
        self.cont_cb = cont_cb
        self.end_tag = end_tag
        self.end_cb = end_cb

        self.add(self.color)
        self.add(self.line)

    # animate barline (position) based on current time
    def on_update(self, now_time):
        w, h = Window.size

        x = time_to_xpos(self.time - now_time)
        y = lane_to_ypos(108 - 21 + 1) * barline_scalar
        y1 = y * bottom_barline_scalar
        y2 = y

        # TODO: change story picture if barline is Story Point

        self.line.points = [x, y1, x, y2]
        self.line.width = .5

# Displays part of nowbar
class NowBarSquare(InstructionGroup):
    def __init__(self, note, hue):
        super(NowBarSquare, self).__init__()

        self.lane = note

        self.color  = Color(hsv=(hue,.666,.666))
        self.rect = CRectangle()

        self.on_layout(Window.size)

        self.add(self.color)
        self.add(self.rect)

    # displays when button is pressed down
    def on_down(self):
        pass

    # back to normal state
    def on_up(self):
        pass

    # modify object positions based on new window size
    def on_layout(self, win_size):
        w, h = win_size

        y = lane_to_ypos(self.lane) * barline_scalar
        x = time_to_xpos(0)        
        sz = h * square_h_pct

        self.rect.cpos = (x, y)
        self.rect.size = (sz * 1.2, sz * 1.2)

# defines midi note to note letter standard
class KeyDisplay(InstructionGroup):
    def __init__(self, key, clef, staff_lines, line_spacing, clef_size, clef_x):
        super(KeyDisplay, self).__init__()
        self.type = key[0]
        self.num = int(key[1])
        self.clef = clef
        self.line_spacing = line_spacing
        self.clef_size = clef_size
        self.source = '../data/img/notation/' + self.type + '.png'
        self.accidental_size = (self.clef_size[0]/3, self.clef_size[1]/2)
        self.clef_x = clef_x

        # staff_lines lists data points for staff lines, bottom -> up
        # for bass: G, B, D, F, A
        # for treble: E, G, B, D, F
        self.staff_lines = staff_lines[:]
        #assert(len(staff_lines) == 5)

        # accessing global staff / note data
        if self.clef == 'bass':
            staff_line_notes, clef_notes = bass_staff_line_notes[:], all_bass_clef_notes.copy()
        elif self.clef == 'treble':
            staff_line_notes, clef_notes = treble_staff_line_notes[:], all_treble_clef_notes.copy()

        # get dictionary mapping notes to positions
        note_to_pos = {}
        for l in range(len(self.staff_lines)):
            staff_line_note = staff_line_notes[l]
            note_to_pos[staff_line_note] = self.staff_lines[l]

            if l != len(self.staff_lines) - 1:
                inbetween_next = clef_notes[staff_line_note]
                pos = self.staff_lines[l][:] # [f_x, i, Window.width, i]
                new_y = pos[1] + self.clef_size[1] * self.line_spacing / 2
                pos[1], pos[3] = new_y, new_y
                note_to_pos[inbetween_next] = pos

        # draw accidentals, TODO: do sharps
        for i in range(self.num):
            note = circle_fifths[len(circle_fifths) - 1 - i]
            pos_y = note_to_pos[note][1] - self.clef_size[1] / 5
            pos_x = self.clef_x + self.clef_size[0] * 5 / 7 + 25 * (i + 1)
            accidental = Rectangle(source=self.source, pos = (pos_x, pos_y), size = self.accidental_size)
            self.add(accidental)

        # setting global note anchor value
        global bass_anchor_note
        global treble_anchor_note
        anchor = bass_anchor_note if self.clef == 'bass' else treble_anchor_note
        anchor_pos = note_to_pos[anchor[0]]
        anchor = (anchor[0], anchor[1], anchor_pos)
        if self.clef == 'bass':
            bass_anchor_note = anchor
        else:
            treble_anchor_note = anchor

    def on_layout(self):
        # TODO:
        pass

class MusicPartDisplay(InstructionGroup):
    def __init__(self, clef, key):
        super(MusicPartDisplay, self).__init__()
        self.clef = clef
        self.key = key
        self.source = "../data/img/notation/" + self.clef + ".png"
        self.split_screen_pct = .7
        self.size = (Window.width/7 * self.split_screen_pct, Window.height/4 * self.split_screen_pct) #!!!
        self.line_width = 3 * self.split_screen_pct
        self.line_spacing = (3 / 16) * self.split_screen_pct

        global clef_size
        global line_spacing
        clef_size = self.size
        line_spacing = self.line_spacing

        # colors
        self.grey = Color(141 / 255, 141 / 255, 141 / 255)

        self.staff_lines = []
        self.clef_x_pos = None
        # clef and staff line drawing
        if self.clef == 'treble':
            self.staff_lines, self.clef_x_pos = self.treble_setup()
        elif self.clef == 'bass':
            self.staff_lines, self.clef_x_pos = self.bass_setup()
        
        # key drawing
        self.key_display = KeyDisplay(self.key, self.clef, self. staff_lines, self.line_spacing, self.size, self.clef_x_pos)
        self.add(self.key_display)

    def treble_setup(self):
        treble_x, treble_y = Window.width/1000, Window.height * 3/14
        size = self.size
        staff_lines = self.draw_treble_staff_lines((treble_x, treble_y), size)
        self.clef_display = Rectangle(source=self.source, pos = (treble_x, treble_y), size = size)
        self.add(self.clef_display)

        return staff_lines, treble_x

    def draw_treble_staff_lines(self, clef_pos, clef_size):
        # points for g staff line exactly
        g_x, g_y = 0, clef_pos[1] + clef_size[1] * 7 / 16
        g_points = [g_x, g_y, Window.width, g_y]

        # points for staff line below g exactly
        below_g_y = g_y - clef_size[1] * self.line_spacing
        below_g_points = [g_x, below_g_y, Window.width, below_g_y]

        # points for staff lines above g
        others_y = []
        prev = g_y
        for i in range(3):
            prev += clef_size[1] * self.line_spacing
            others_y.append(prev)

        # add staff lines to canvas
        self.add(self.grey)
        self.add(Line(points = g_points, width = self.line_width))
        self.add(Line(points = below_g_points, width = self.line_width))
        staff_lines = []
        for i in others_y:
            points = [g_x, i, Window.width, i]
            staff_lines.append(points)
            self.add(Line(points = points, width = self.line_width))

        staff_lines.insert(0, g_points)
        staff_lines.insert(0, below_g_points)
        return staff_lines


    def bass_setup(self):
        bass_x, bass_y = Window.width/1000, Window.height * 1/14
        size = self.size
        staff_lines = self.draw_bass_staff_lines((bass_x, bass_y), size)
        self.clef_display = Rectangle(source=self.source, pos = (bass_x, bass_y), size = size)
        self.add(self.clef_display)

        return staff_lines, bass_x

    # TODO: idea, separate getting staff line positions and drawing them, definitely more modular
    def draw_bass_staff_lines(self, clef_pos, clef_size):
        # points for f staff line exactly
        f_x, f_y = 0, clef_pos[1] + clef_size[1] * 23 / 32
        f_points = [f_x, f_y, Window.width, f_y]

        # points for staff line above f exactly
        above_f_y = f_y + clef_size[1] * self.line_spacing
        above_f_points = [f_x, above_f_y, Window.width, above_f_y]

        # points for staff lines below f
        others_y = []
        prev = f_y
        for i in range(3):
            prev -= clef_size[1] * self.line_spacing
            others_y.append(prev)

        # add staff lines to canvas
        self.add(self.grey)
        self.add(Line(points = f_points, width = self.line_width))
        self.add(Line(points = above_f_points, width = self.line_width))
        staff_lines = []
        for i in others_y:
            points = [f_x, i, Window.width, i]
            staff_lines.append(points)
            self.add(Line(points = points, width = self.line_width))
        
        staff_lines.reverse()
        staff_lines.append(f_points)
        staff_lines.append(above_f_points)
        return staff_lines


    def on_layout(self):
        self.clear()
        if self.clef == 'treble':
            self.staff_lines, self.clef_x_pos = self.treble_setup()
        elif self.clef == 'bass':
            self.staff_lines, self.clef_x_pos = self.bass_setup()

        self.key_display = KeyDisplay(self.key, self.clef, self. staff_lines, self.line_spacing, self.size, self.clef_x_pos)
        self.add(self.key_display)
        

# Displays all game elements, nowbar, keyboard, notes, barlines
# TODO: idea have GameDisplay take Piece object
class GameDisplay(InstructionGroup):
    def __init__(self, song_data, music_part_displays):
        super(GameDisplay, self).__init__()

        # TODO MusicPartDisplay before note and barline generation
        #      MusicPartDisplay needs to do Key as well
        #      Use song_data to get necessary information
        #      Part's staff line data needs to be accessible
        #      Maybe hardcode staff line midi keys
        #      Option to change MusicPartDisplay's Key, for different keys in same piece

        self.gem_data = song_data.get_notes()
        self.barlines = song_data.get_barlines()
        self.part_displays = music_part_displays

        # add music parts to display
        for part in self.part_displays:
            self.add(self.part_displays[part])

        hues  = []
        num_keys = 108 - 21
        increment_by = 1 / num_keys
        hue = 0
        for i in range(num_keys):
            hue += increment_by
            hues.append(hue)

        # TODO: pass in arguments to Barline Display for Story Points, get call backs
        self.barlines = [BarlineDisplay(b[0], b[1], b[2], None, b[3], None) for b in self.barlines]
        for b in self.barlines:
            self.add(b)

        self.notes = [NoteDisplay(g[1], g[0], g[2], hues[g[1]]) for g in self.gem_data]
        for n in self.notes:
            self.add(n)

        # drawing now bar

        self.squares = [NowBarSquare(n, hues[n]) for n in range(12, 108 - 21)]
        for s in self.squares:
            self.add(s)

        # self.score = CLabelRect((Window.width - 100, Window.height - 50), text='0', font_size=50)
        # self.add(Color(1,1,1))
        # self.add(self.score)

        # For testing purposes. Player Performance Evaluation.
        # self.progress_circle_color = Color(1,1,1) # white
        # self.progress_circle = CEllipse(segments=20)
        # self.progress_circle.cpos = (Window.width / 2, Window.height * 9 / 16)
        # self.add(self.progress_circle_color)
        # self.add(self.progress_circle)

    # called by Player when succeeded in hitting this gem.
    def note_hit(self, note_idx):
        print('NOTE:', note_idx, 'HIT')
        # self.progress_circle_color.rgb = (0,1,0) # green
        # self.notes[note_idx].on_hit()

    # called by Player on pass or miss.
    def note_pass(self, note_idx):
        print('NOTE:', note_idx, 'MISSED')
        # self.progress_circle_color.rgb = (1,0,0) # red
        # self.notes[note_idx].on_pass()

    # called by Player on button down
    def on_key_down(self, midi_note):
        pass

    # called by Player on button up
    def on_key_up(self, midi_note):
        pass

    # called by Player to update score
    # def set_score(self, score):
    #     self.score.set_text('{}'.format(score))

    # for when the window size changes
    def on_layout(self, win_size):
        # update music part displays
        for part in self.part_displays:
            self.part_displays[part].on_layout()

        for s in self.squares:
            s.on_layout(win_size)

        # self.score.set_cpos((win_size[0] - 100, win_size[1] - 50))

    # call every frame to handle animation needs
    def on_update(self, now_time) :
        for b in self.barlines:
            b.on_update(now_time)

        for n in self.notes:
            n.on_update(now_time)

# Handles game logic
# Controls GameDisplay and AudioCtrl based on what happens
class Player(object):
    def __init__(self, song_data, audio_ctrl, display, end_callback, continue_callback):
        super(Player, self).__init__()

        self.continue_callback = continue_callback
        self.end_callback = end_callback
        self.song_data = song_data
        self.audio_ctrl = audio_ctrl
        self.display = display
        self.notes = self.song_data.get_notes()
        self.notes_alive = [True] * len(self.notes)

        self.score = 0
        self.last_time = 0

    def on_key_down(self, midi_note):
        # self.display.on_button_down(lane)
        print('in Player on key down')
        print('midi_note:', midi_note)
        now = self.audio_ctrl.get_time()

        notes_in_window = self.song_data.get_note_indexes_in_range(now - slop_window, now + slop_window)

        did_hit = False
        # look for gems that are hittable (still alive)
        for ni in notes_in_window:
            if self.notes_alive[ni] and self.notes[ni][1] == midi_note:
                self.notes_alive[ni] = False
                self.score += 1
                # self.display.set_score(self.score)
                self.display.note_hit(ni)
                self.continue_callback()
                did_hit = True
                break

        # if a hit did not happen, the remaining gems in the window are considered misses:
        if not did_hit:
            self.audio_ctrl.play_miss()
            self.end_callback()
            for ni in notes_in_window:
                if self.notes_alive[ni]:
                    self.notes_alive[ni] = False
                    self.display.note_pass(ni)

        # audio control:
        self.audio_ctrl.set_mute(not did_hit)

    def on_key_up(self, midi_note):
        # TODO
        pass
    
    def on_update(self, time):
        notes_in_window = self.song_data.get_note_indexes_in_range(self.last_time - slop_window, time - slop_window)
        self.last_time = time

        # check for alive gems that just passed the slow window, set mute alive note passes
        for ni in notes_in_window:
            if self.notes_alive[ni]:
                self.notes_alive[ni] = False
                self.display.note_pass(ni)
                self.audio_ctrl.set_mute(True)
                self.end_callback()


# helper for opening a midi port by name
def open_midi_out(name):
    midi_out = rtmidi.MidiOut()
    for i, port_name in enumerate(midi_out.get_ports()):
        if name in port_name:
            midi_out.open_port(i)
            return midi_out
    raise Exception ("Error: Can't find Midi Out port with name " + name)

# helper for opening a midi port by name
def open_midi_in(name, callback):
    midi_in = rtmidi.MidiIn()
    for i, port_name in enumerate(midi_in.get_ports()):
        if name in port_name:
            midi_in.open_port(i)
            midi_in.set_callback(callback)
            return midi_in
    raise Exception ("Error: Can't find Midi In port with name " + name)

# if __name__ == "__main__":
#     run(PerformerWidget)