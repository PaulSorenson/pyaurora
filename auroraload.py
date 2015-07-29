#!/usr/local/bin/python3.4


'''
Persistence model for pyaurora

.. moduleauthor:: paul sorenson

'''


import datetime as dt
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker


def makemodel(metadata):

    samples = sa.Table('samples', metadata,
        sa.Column('utc', sa.DateTime, primary_key=True),
        sa.Column('gridPowerAll', sa.Float),
        sa.Column('powerPeakToday', sa.Float),
        sa.Column('dailyEnergy', sa.Float),
        sa.Column('weeklyEnergy', sa.Float),
        sa.Column('partialEnergy', sa.Float),
        sa.Column('getEnergy10', sa.Float),
        sa.Column('frequencyAll', sa.Float),
        sa.Column('gridVoltageAll', sa.Float),
        sa.Column('gridVoltageAverage', sa.Float),
        sa.Column('gridCurrentAll', sa.Float),
        sa.Column('bulkVoltageDcDc', sa.Float),
        sa.Column('in1Voltage', sa.Float),
        sa.Column('in1Current', sa.Float),
        sa.Column('in2Voltage', sa.Float),
        sa.Column('in2Current', sa.Float),
        sa.Column('pin1All', sa.Float),
        sa.Column('pin2All', sa.Float),
        sa.Column('iLeakDcDc', sa.Float),
        sa.Column('iLeakInverter', sa.Float),
        sa.Column('boosterTemp', sa.Float)
        )

    return samples


def insert_csv(gp='aurora_2015-*.csv'):
    import glob
    import csv
    paths = glob.glob(gp)

    for path in paths:
        with open(path, 'r') as csvin:
            rdr = csv.DictReader(csvin)
            for d in rdr:
                d['utc'] = dt.datetime.strptime(d['utc'], 
                        '%Y-%m-%d %H:%M:%S.%f').replace(microsecond=0)
                yield d


def main():
    db = sa.create_engine('sqlite:///aurora.db')
    #db.echo = True
    metadata = sa.MetaData(db)
    model = makemodel(metadata)
    model.create()

    conn = db.connect()
    chunksize = 1000
    chunk = []
    for row in insert_csv():
        chunk.append(row)
        if len(chunk) >= chunksize:
            conn.execute(model.insert(), chunk)
            chunk = []
    if len(chunk) > 0:
        conn.execute(model.insert(), chunk)


if __name__ == '__main__':
    main()

