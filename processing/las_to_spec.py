from welly import Well
import bruges
import numpy as np

path = '../rgb-explorers/logs/'
#'F02-01_F02-01_Set.las'


def las_to_spec(lasfile):
    w = Well.from_las(lasfile)# path+'F03-03_F03-03_Set.las'
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
    interval = 2*(wdf.index.values[1]-wdf.index.values[0]) # factor 2 is added to create realistic velocities, to be sorted out...
    scaled_dt = interval * np.nan_to_num(wdf['DT']) / 1e6

    tcum = 2 * np.cumsum(scaled_dt)
    tdr = tcum + log_start_time

    # RESAMPLING FUNCTION
    dt = 0.004
    maxt = 2.5

    t = np.arange(0, maxt, dt)
    Z_t = np.interp(x = t, xp = tdr, fp = wdf['AI'])

    RC_t = (Z_t[1:] - Z_t[:-1]) / (Z_t[1:] + Z_t[:-1])
    RC_t = np.nan_to_num(RC_t)
    Cf = np.arange(3,80,2)

    synth = np.zeros((len(RC_t),len(Cf)))

    for i, cf in enumerate(Cf):
        w = bruges.filters.ricker(f=cf, duration = 0.512, dt = 0.004)
        synth[:,i] = np.convolve(w, RC_t, mode='same')

    np.save('well_spectrum.npy',synth)

    return
