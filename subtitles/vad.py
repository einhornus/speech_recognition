import matplotlib.pyplot as plt
import torch
import librosa
# import speechmetrics
from pyannote.audio.pipelines import VoiceActivityDetection
import math
import numpy as np
import subprocess
from scipy.io.wavfile import write
import os
from pathlib import Path
import json
from pyannote.audio import Pipeline
from pyannote.audio import Model
from pyannote.audio import Inference

SPEECH_THRESHOLD = 0.5
MIN_SPEECH_INTERVAL = 2000
MERGING_DISTANCE = 1000


class VAD:
    def __init__(self, wav_file):
        model = Model.from_pretrained("pyannote/brouhaha",
                                      use_auth_token="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", cache_dir="models")
        inference = Inference(model)
        output = inference(wav_file)

        self.starts = []
        self.mids = []
        self.ends = []
        self.vads = []
        self.snrs = []
        self.c50s = []
        self.first_frame_above_threshold = None

        for frame, (vad, snr, c50) in output:
            self.starts.append(round(frame.start * 1000))
            self.ends.append(round(frame.end * 1000))
            self.vads.append(vad)
            self.snrs.append(snr)
            self.c50s.append(c50)
            self.mids.append(round(frame.middle * 1000))
            if vad > 0.8 and self.first_frame_above_threshold is None:
                self.first_frame_above_threshold = round(frame.start * 1000)

    def is_music(self):
        return sum(self.snrs) / len(self.snrs) < 3

    def get_intervals_for_music(self):
        return [(self.first_frame_above_threshold, self.ends[-1])]

    def get_intervals(self, strictness=SPEECH_THRESHOLD, t=None):
        intervals = []

        start = None
        end_frame = None
        for i in range(len(self.vads)):
            if t is None or (t[0] <= self.mids[i] <= t[1]):
                is_speech = self.vads[i] > strictness
                if is_speech:
                    if start is None:
                        start = self.starts[i]
                else:
                    if start is not None:
                        end = self.ends[i]
                        intervals.append((start, end))
                        start = None
                end_frame = self.ends[i]
        if start is not None:
            intervals.append((start, end_frame))

        mergable = []
        for i in range(len(intervals) - 1):
            if intervals[i + 1][0] - intervals[i][1] <= MERGING_DISTANCE:
                mergable.append(True)
            else:
                mergable.append(False)
        mergable.append(False)

        merged_intervals = []
        start = None
        for i in range(len(intervals)):
            if not mergable[i]:
                if start is not None:
                    merged_intervals.append((start, intervals[i][1]))
                    start = None
                else:
                    merged_intervals.append(intervals[i])
            else:
                if start is None:
                    start = intervals[i][0]

        filtered_intervals = []
        for interval in merged_intervals:
            if interval[1] - interval[0] >= MIN_SPEECH_INTERVAL:
                filtered_intervals.append(interval)

        return filtered_intervals

    def plot(self):
        fig, ax1 = plt.subplots()
        color = 'tab:red'
        ax1.set_xlabel('Time (ms)')
        ax1.set_ylabel('VAD', color=color)
        ax1.plot(self.mids, self.vads, color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        ax2 = ax1.twinx()
        color = 'tab:blue'
        ax2.set_ylabel('SNR', color=color)
        ax2.plot(self.mids, self.snrs, color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        fig.tight_layout()
        plt.show()