import base64
import io

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt



def build_b64_png(array, aspect_ratio=1, dpi=100):
    _ = plt.imshow(array, aspect=aspect_ratio)
    mem_file = io.BytesIO()
    plt.savefig(mem_file, format="png", bbox_inches='tight', pad_inches=0, dpi=dpi)
    mem_file.seek(0)
    return base64.b64encode(mem_file.read())