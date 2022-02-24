import sys

import GPUtil


def get_avail_gpus():
    avail_gpus = GPUtil.getAvailable(order='load',
                                     limit=1,
                                     maxLoad=0.5,
                                     maxMemory=0.5,
                                     includeNan=False,
                                     excludeID=[],
                                     excludeUUID=[])
    use_gpus = ','.join([str(x) for x in avail_gpus])
    return use_gpus


if __name__ == '__main__':
    if '--gpus' in sys.argv:
        print(get_avail_gpus())
