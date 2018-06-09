# Processing file for raw rgb blending.
# No flask here

import segyio
from scipy.signal import cwt, ricker
import numpy
from numpy import fft
import io

import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt

PRECOMPUTED_DATA_FILE_NAME = r"C:\Users\J0436735\Downloads\f3sub_hack_cwt_cube.npy"
PRECOMPUTED_DATA = None


def get_precomputed_data():
    global PRECOMPUTED_DATA
    if PRECOMPUTED_DATA is None:
        PRECOMPUTED_DATA = numpy.load(PRECOMPUTED_DATA_FILE_NAME)
    return PRECOMPUTED_DATA


def build_png(array, aspect_ratio=1):
    _ = plt.imshow(array, aspect=aspect_ratio)
    mem_file = io.BytesIO()
    plt.savefig(mem_file, format="png")
    mem_file.seek(0)
    return mem_file.read()


def clip_and_normalize(array):
    max_ = numpy.max(array)
    normalized_array = array / (abs(max_) + 1.e-12)
    clip_max = 0.5
    clipped_array = numpy.clip(normalized_array, 0, clip_max)
    return clipped_array / clip_max


def seismic_blend_png(direction, index, frequencies):
    precomputed_data = get_precomputed_data()
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
    return build_png(result)


def rgb_log_png(x, y, frequencies):
    precomputed_data = get_precomputed_data()
    slices = list(map(lambda freq: clip_and_normalize(precomputed_data[x, y, :, freq]), frequencies))
    r = numpy.swapaxes(numpy.dstack(slices), 0, 1)
    build_png(r, aspect_ratio=0.05)
    return


if __name__ == '__main__':
    rgb_log_png(5, 5, (10, 15, 20))


def compute(rbg):
    """
    Performs the rgb blending.
    :param rbg: rgb triplet (20, 40, 60) to be computed.
    :return:
    """
    pass


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
