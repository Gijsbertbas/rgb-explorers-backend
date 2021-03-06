import os
from scipy.signal import hilbert
from welly import Well
import bruges
import numpy as np

from processing.png import build_b64_png
from processing.rgb_blending import ricker_expansion, clip_and_normalize

path = '../rgb-explorers/logs/'
#'F02-01_F02-01_Set.las'
#'F03-03_F03-03_Set.las'

def las_to_rc(path_to_las):

    w = Well.from_las(path_to_las)
    wdf = w.df()
    wdf = wdf.loc[~np.isnan(wdf['DT']),:]
    wdf['AI'] = w.df()['RHOB']*1e6/w.df()['DT']

    # kb and wd are assumened for the time being
    kb = 35.9
    wd = 44.5
    top_log = wdf.index.values[0]

    w_vel = 1480  # velocity of sea water [m/s]
    repl_vel = 1600 # m/s

    water_twt = 2.0 * wd / w_vel
    repl_time = 2.0 * (top_log - wd) / repl_vel
    log_start_time = water_twt + repl_time

    # ignored for now
    def tvdss(md):
        "assumes a vertical well"
        return md - kb

    # two-way-time to depth relationship
    interval = wdf.index.values[1]-wdf.index.values[0]
    scaled_dt = interval * np.nan_to_num(wdf['DT']) / 1e6

    tcum = 2 * np.cumsum(scaled_dt)
    tdr = tcum + log_start_time

    # RESAMPLING FUNCTION
    dt = 0.004
    mint = 0.0
    maxt = 1.8

    t = np.arange(mint, maxt, dt)
    Z_t = np.interp(x = t, xp = tdr, fp = wdf['AI'])

    RC_t = (Z_t[1:] - Z_t[:-1]) / (Z_t[1:] + Z_t[:-1])
    return np.nan_to_num(RC_t)


def las_to_spec(path_to_las):

    RC_t = las_to_rc(path_to_las)

    Cf = np.arange(3,80,2)

    synth = np.zeros((len(RC_t),len(Cf)))

    for i, cf in enumerate(Cf):
        w = bruges.filters.ricker(f=cf, duration = 0.512, dt = 0.004)
        synth[:,i] = np.convolve(w, RC_t, mode='same')

#    np.save('well_spectrum.npy',synth)
    return synth


LAS_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..","..", "F03-03_F03-03_Set.las"))


def rgb_log(frequencies, dpi):
    return build_b64_png(__rgb_log2(LAS_FILE_PATH, frequencies), aspect_ratio=0.01, dpi=dpi)


def __rgb_log(path_to_las, frequencies):
    RC_t = las_to_rc(path_to_las)

    clipping = 0.9
    f_power = .5

    synth = np.zeros((len(RC_t),3))

    for i, f in enumerate(frequencies):
        w = bruges.filters.ricker(f=f, duration = 0.512, dt = 0.004)
        bandpass = np.convolve(w, RC_t, mode='same')
        synth[:,i] = np.abs(hilbert(bandpass))

    c_1 = synth[:,0] / np.amax(synth[:,0])
    c_1 = c_1**f_power
    c_1 = np.where(c_1 >= clipping, 1.0, c_1/clipping)

    c_2 = synth[:,1] / np.amax(synth[:,1])
    c_2 = c_2**f_power
    c_2 = np.where(c_2 >= clipping, 1.0, c_2/clipping)

    c_3 = synth[:,2] / np.amax(synth[:,2])
    c_3 = c_3**f_power
    c_3 = np.where(c_3 >= clipping, 1.0, c_3/clipping)

    rgb_array = np.zeros((len(RC_t),1, 3))
    rgb_array[:,:,0] = c_1[:,np.newaxis]
    rgb_array[:,:,1] = c_2[:,np.newaxis]
    rgb_array[:,:,2] = c_3[:,np.newaxis]

#    fig, axes = plt.subplots(1,2,figsize=(10,10))
#    axes[0].plot(synth[:,1],-t[:-1], 'k')
#    axes[0].fill_betweenx(-t[:-1], synth[:,1],  0,  synth[:,1] > 0.0,  color='k', alpha = 1.0)
#    axes[0].set_title('synthetic', size=20)
#    axes[0].set_ylabel('time (ms)', size = 20)
#    axes[0].get_xaxis().set_ticks([])
#    axes[1].imshow(rgb_blend, aspect='auto')
#    axes[1].set_title('RGB blend', size=20)
#    axes[1].get_xaxis().set_ticks([])
#    axes[1].get_yaxis().set_ticks([])

#    wellname = filename.split('.')[0]
#    plt.savefig('RGB_log_'+wellname+'.png')

    return rgb_array

def __rgb_log2(path_to_las, frequencies):
    RC_t = las_to_rc(path_to_las)

    clipping = 0.9
    f_power = .5

    synth = np.zeros((len(RC_t),3))
    for i, f in enumerate(frequencies):
        w = bruges.filters.ricker(f=f, duration = 0.512, dt = 0.004)
        bandpass = np.convolve(w, RC_t, mode='same')
        synth[:,i] = np.abs(hilbert(bandpass))

    synth = clip_and_normalize(synth)

    return synth[:,np.newaxis,:]

if __name__ == '__main__':
    pass
