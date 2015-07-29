#!/usr/local/bin/python3.4

'''
Simple cron scheduler with focus on "accurate" clock time.
'''


import time
import sched
import logging

log = logging.getLogger('aurora')


def scheduler(interval, func, offset=0, *args, **kwargs):
    '''
    Run func every interval seconds + offset.

    :param interval: run function at interval, the function is
        triggered when ``(clocktime % interval) == offset``.
    :param: func to be called.  Additional args can be passed in args
        and kwargs.
    :param offset: set this to non-zero to offset the trigger time.
    :param resolution: seconds between checking the clocktime.
    '''
    s = sched.scheduler()

    t = time.time()
    modt = (int(t) % interval) - offset
    deltat = interval - modt - (t - (int(t)))
    while True:
        log.debug('deltat: {0} seconds'.format(deltat))
        s.enter(deltat, 0, func, argument=args, kwargs=kwargs)
        s.run()
        t = time.time()
        modt = (int(t) % interval) - offset
        deltat = interval - modt - (t - (int(t))) 


def main():
    import datetime as dt
    def test():
        print(dt.datetime.now())
    scheduler(5, test, offset=3)


if __name__ == "__main__":
    main()

