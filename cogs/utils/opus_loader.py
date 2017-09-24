# Borrowing from https://github.com/Just-Some-Bots/MusicBot/blob/master/musicbot/opus_loader.py to test
from discord import opus


def load_opus_lib():

    opus_libs = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']

    if opus.is_loaded():
        print('Opus loaded')
        return True

    for opus_lib in opus_libs:
        try:
            opus.load_opus(opus_lib)
            print("Manually loaded {}".format(opus_lib))
            return
        except OSError:
            pass

    raise RuntimeError('Could not load an opus lib. Tried %s' % (', '.join(opus_libs)))