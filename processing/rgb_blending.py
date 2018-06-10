# Processing file for raw rgb blending.
# No flask here

import segyio
from scipy.signal import cwt, ricker
import numpy
from numpy import fft
import io
import bruges
import os
import base64

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

PRECOMPUTED_DATA_FILE_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), "..","..", "f3sub_hack_cwt_cube_well_f03-03.npy"))
SEISMIC_SGY = os.path.abspath(os.path.join(os.path.dirname(__file__), "..","..", "F03_Subcrop.sgy"))
print(PRECOMPUTED_DATA_FILE_NAME)
print(SEISMIC_SGY)
PRECOMPUTED_DATA = None


def get_precomputed_data():
    global PRECOMPUTED_DATA
    if PRECOMPUTED_DATA is None:
        PRECOMPUTED_DATA = numpy.load(PRECOMPUTED_DATA_FILE_NAME)
    return PRECOMPUTED_DATA


def build_b64_png(array, aspect_ratio=1, dpi=100):
    _ = plt.imshow(array, aspect=aspect_ratio)
    mem_file = io.BytesIO()
    plt.savefig(mem_file, format="png", bbox_inches='tight', pad_inches=0, dpi=dpi)
    mem_file.seek(0)
    return base64.b64encode(mem_file.read())


def clip_and_normalize(array):
    max_ = numpy.max(array)
    normalized_array = array / (abs(max_) + 1.e-12)
    clip_max = 0.5
    clipped_array = numpy.clip(normalized_array, 0, clip_max)
    return clipped_array / clip_max


def seismic_blend_png(direction, index, frequencies):
    precomputed_data = get_precomputed_data()
    freq_min, freq_max = 0, precomputed_data.shape[3] - 1
    if any(filter(lambda f: f < freq_min or f > freq_max, frequencies)):
        raise ValueError("Frequencies are supposed to rely in [%s, %s[." % (freq_min, freq_max))
    slices = []
    for freq in frequencies:
        if direction == 'x':
            freq_data = precomputed_data[index, :, :, freq]
        elif direction == 'y':
            freq_data = precomputed_data[:, index, :, freq]
        elif direction == 't':
            freq_data = precomputed_data[:, :, index, freq]
        slices.append(clip_and_normalize(freq_data.T))
    result = numpy.dstack(slices)
    return build_b64_png(result)


def rgb_log_png(x, y, frequencies, dpi):
    precomputed_data = get_precomputed_data()
    slices = list(map(lambda freq: clip_and_normalize(precomputed_data[x, y, :, freq]), frequencies))
    r = numpy.swapaxes(numpy.dstack(slices), 0, 1)
    return build_b64_png(r, aspect_ratio=0.05, dpi=dpi)


def compute_whole_sgy_file():
    seismic_sgy = ""
    with segyio.open(seismic_sgy, 'r') as f:
        trace = f.trace[500]

    widths = numpy.arange(1, 11, 0.1)
    Wf = []
    for w in widths:
        w = ricker(50, w)
        F = fft.fftshift(fft.fftfreq(256))
        W = fft.fftshift(fft.fft(numpy.real(w), 256))
        Wf.append(numpy.amax(numpy.abs(W)))

    p_trace = numpy.zeros(250)
    p_trace[0:len(trace)] = trace
    # cwt_tf = cwt(trace, ricker, numpy.arange(1, 11, 0.1))

    volume = segyio.tools.cube(seismic_sgy)
    cwt_cube = numpy.zeros((*volume.shape, len(Wf)))
    shape = cwt_cube.shape

    for i in range(0, shape[0]):
        for x in range(0, shape[1]):
            trace = numpy.squeeze(volume[i, x, :])
            c = cwt(trace, ricker, widths)
            cwt_cube[i, x, :, :] = numpy.fliplr(c).T

    return cwt_cube, volume

def slice_sgy(direction, index):
    seismic_sgy = SEISMIC_SGY
    with segyio.open(seismic_sgy, 'r') as f:
        if direction == 'x':
            line = f.iline[index]
        elif direction == 'y':
            line = f.xline[index]
    return line

def ricker_expansion(trace, Fc):
    expansion = numpy.zeros((len(trace), len(Fc)))
    for i, fc in enumerate(Fc):
        w = bruges.filters.ricker(f=fc, duration=0.512, dt=0.004)
        bandpass = numpy.squeeze(numpy.convolve(w, trace, mode='same'))
        expansion[:, i-1] = bandpass
    return expansion


def line_blend_png(direction, index, frequencies, dpi):
    line = slice_sgy(direction, index)
    shape = line.shape
    slices = []
    blend_line = numpy.zeros((*line.shape, 3))
    for x in range(0, shape[1]):
        trace = line[:,x]
        E = ricker_expansion(trace, frequencies)
        blend_line[:, x, :] = clip_and_normalize(E)
    return build_b64_png(numpy.swapaxes(blend_line, 0, 1), dpi=dpi)

def build_synth(rgb_array):
    synth = numpy.squeeze(rgb_array[:,:,1])

    t = numpy.arange(0, 1.8, 0.004) # hard coded...

    fig, ax = plt.subplots(figsize=(2,12))
    ax.plot(synth,-t[:-1], 'k')
    ax.fill_betweenx(-t[:-1], synth,  0,  synth > 0.0,  color='k', alpha = 1.0)
    ax.set_title('synthetic', size=18)
    ax.set_ylabel('time (ms)', size = 16)
    ax.get_xaxis().set_ticks([])

    mem_file = io.BytesIO()
    plt.savefig(mem_file, format="png")
    mem_file.seek(0)
    return mem_file.read()
