import os
from pydub import AudioSegment


def max_length(speed, *files):
    length = 0
    for file in files:
        beat = AudioSegment.from_file(file, format='wav')
        if beat.duration_seconds * speed > length:
            length = beat.duration_seconds * speed
    return length


def clear_file(path):
    if os.path.isfile(path):
        f = open(path, 'r+')
        f.seek(0)
        f.truncate()


class Track:

    def __init__(self):
        self.track_overlay = None
        self.files = None

    def set_track(self, filename):
        self.track_overlay = filename
        if filename:
            track = AudioSegment.from_file(self.track_overlay, format='wav')
            return track.frame_rate, track.duration_seconds

    def set_files(self, *files):
        self.files = files

    def make_track(self, filename, speed, length, volume, *track_files):
        clear_file(filename)
        beats = self.get_beats(100 / speed, *track_files)
        track = AudioSegment.empty()
        while track.duration_seconds < length:
            track += beats
        track += volume
        if track.duration_seconds > length:
            track = track[:1000 * length]
        if self.track_overlay:
            track_overlay = AudioSegment.from_file(self.track_overlay, format='wav')
            if track.duration_seconds > track_overlay.duration_seconds:
                track_overlay += AudioSegment.silent(duration=track.duration_seconds - track_overlay.duration_seconds)
            track = track.overlay(track_overlay)
        track.export(out_f=filename, format='wav')

    def get_beats(self, speed, *track_files):
        beats = None
        for track in track_files:
            beat_track = AudioSegment.empty()
            for file in track:
                try:
                    beat = AudioSegment.from_file(file, format='wav')
                    silence = max_length(speed, *self.files) - beat.duration_seconds
                    beat_track += beat + AudioSegment.silent(duration=silence * 1000)
                except FileNotFoundError:
                    silence = max_length(speed, *self.files)
                    beat_track += AudioSegment.silent(duration=silence * 1000)
            beats = beats.overlay(beat_track) if beats else beat_track
        return beats
