'''
Aurora PV Commands

See C language aurora utility from curtronics.com.

.. moduleauthor:: paul sorenson
'''


from enum import IntEnum
from .protocol import getlong, getfloat, getstring, bytes2hex, gettime


def floatfmt(f):
    return '{0:8.2f}'.format(f)


class Cmd(IntEnum):
    '''
    These attributes define commands that can be issued
    to the Aurora PV inverter.  Many of them have subcommands.
    '''

    getState = 50
    getPartNumber = 52
    getUnknown01 = 56
    getVersion = 58
    getDsp = 59
    getSerial = 63
    getMfrWeekYear = 65
    getCumFloatEnergy = 68
    getTime = 70
    setTime = 71
    getFirmwareRel = 72
    # getEnergySent = 75 01
    # getCumDay = 75 02
    getCumEnergy10 = 76
    getConfig = 77
    getCumEnergy = 78
    getCumEnergyDay = 79
    getCounters = 80
    getUnknown02 = 82
    getUnknown03 = 83
    getLastAlarms = 86
    getPartNumberC = 105


class DspOp(IntEnum):
    '''
    Operations for getDsp
    '''

    gridVoltageAll  = 1        # Grid Voltage (All)
    gridCurrentAll  = 2        # Grid Currrent (All)
    gridPowerAll    = 3        # Grid Power (All)
    frequencyAll    = 4        # Frequency All)
    vBulk           = 5        # VBulk was Ileak (Dc/Dc) reading All)
    iLeakDcDc       = 6        # Ileak (Dc/Dc) was Ileak (Inverter) Reading
    iLeakInverter   = 7        # Ileak (Inverter)
    pin1All         = 8        # Pin 1 (All)
    pin2All         = 9        # Pin 2

    inverterTemp    = 21      # Inverter Temperature (Grid-Tied)
    boosterTemp     = 22      # Booster Temperatuer (Grid-Tied)
    in1Voltage      = 23      # Input 1 Voltage
    in1Current      = 25      # Input 1 Current (All)
    in2Voltage      = 26      # Input 2 Voltage (Grid-Tied)
    in2Current      = 27      # Input 2 Current (Grid-Tied)
    gridVoltageDcDc = 28      # Grid Voltage (Dc/Dc) (Grid-Tied)
    gridFrequencyDcDc   = 29      # Grid Frequency (Dc/Dc) (Grid-Tied)
    rIsoRes         = 30      # Isolation Resistance (Riso) (All)
    bulkVoltageDcDc = 31      # Vbulk (Dc/Dc) (Grid-Tied)
    gridVoltageAverage  = 32      # Average Grid Voltage (VgridAvg) (Grid-Tied)
    bulkVoltageMid  = 33      # Vbulk Mid (Grid-Tied)
    powerPeakAll    = 34      # Power Peak (All)
    powerPeakToday  = 35      # Power Peak Today (All)
    gridVoltageNeutral  = 36      # Grid Voltage neutral (Grid-Tied)
    windGeneratorFrequency  = 37      # Wind Generator Frequency
    ToM38 = 38      # Grid Voltage neutral-phase (Central)
    ToM39 = 39      # Grid Current phase r (Central & 3 Phase)
    ToM40 = 40      # Grid Current phase s (Central & 3 Phase)
    ToM41 = 41      # Grid Current phase t (Central & 3 Phase)
    ToM42 = 42      # Frequency phase r (Central & 3 Phase)
    ToM43 = 43      # Frequency phase s (Central & 3 Phase)
    ToM44 = 44      # Frequency phase t (Central & 3 Phase)
    ToM45 = 45      # Vbulk + (Central & 3 Phase)
    ToM46 = 46      # Vbulk - (Central)
    supervisorTemp  = 47      # Supervisor Temperature (Central)
    alimTemp        = 48      # Alim Temperature (Central)
    heatsinkTemp    = 49      # Heak Sink Temperature (Central)
    ToM50 = 50      # Temperature 1 (Central)
    ToM51 = 51      # Temperature 2 (Central)
    ToM52 = 52      # Temperature 3 (Central)
    ToM53 = 53      # Fan 1 Speed (Central)
    ToM54 = 54      # Fan 2 Speed (Central)
    ToM55 = 55      # Fan 3 Speed (Central)
    ToM56 = 56      # Fan 4 Speed (Central)
    ToM57 = 57      # Fan 5 Speed (Central)
    ToM58 = 58      # Power Saturation limit (Der.) (Central)
    ToM59 = 59      # Reference Ring Bulk (Central)
    ToM60 = 60      # Vpanel micro (Central)
    ToM61 = 61      # Grid Voltage phase r (Central & 3 Phase)
    ToM62 = 62      # Grid Voltage phase s (Central & 3 Phase)
    ToM63 = 63      # Grid Voltage phase t (Central & 3 Phase)
    ToM95 = 95      # Fan 1 Speed (rpm) (Central)
    ToM96 = 96      # Fan 2 Speed (rpm) (Central)
    ToM97 = 97      # Fan 3 Speed (rpm) (Central)
    ToM98 = 98      # Fan 4 Speed (rpm) (Central)
    ToM99 = 99      # Fan 5 Speed (rpm) (Central)
    ToM100 = 100        # Fan 6 Speed (rpm) (Central)
    ToM101 = 101        # Fan 7 Speed (rpm) (Central)


class CumulatedEnergy(IntEnum):
    '''
    See op 78, getCumEnergy.
    '''
    dailyEnergy = 0
    weeklyEnergy = 1
    last7Energy = 2
    monthlyEnergy = 3
    yearlyEnergy = 4
    totalEnergy = 5
    partialEnergy = 6   # since last reset
    

allops = {
    'getFirmwareRel': (Cmd.getFirmwareRel, None, (getstring, str)),
    'getTime': (Cmd.getTime, None, (gettime, str)),
    'getEnergy10': (Cmd.getCumEnergy10, 2, (getlong, floatfmt)),
    }

allops.update({ssc: (Cmd.getDsp, 
        getattr(DspOp, ssc), (getfloat, floatfmt))
        for ssc in  DspOp.__members__.keys()})

allops.update({ssc: (Cmd.getCumEnergy, 
        getattr(CumulatedEnergy, ssc), (getlong, floatfmt))
        for ssc in  CumulatedEnergy.__members__.keys()})

