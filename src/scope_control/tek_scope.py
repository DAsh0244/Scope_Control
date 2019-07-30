from prologix_usb import Scope, ScopeSettings
from enum import Enum
from collections import namedtuple
from typing import (
    Sequence as _Sequence,
    NamedTuple as _NamedTuple
    )
from time import sleep
class TekBinFmt(Enum):
    SignedInt = 'RI'
    UnsignedInt = 'RP'

class TekByteOrder(Enum):
    MSB = 'MSB'
    LSB = 'LSB'

class TekEncoding(Enum):
    ASCII = 'ASCII'
    BIN = 'BIN'

class TekPointFmt(Enum):
    ENV = 'ENV'
    Y = 'Y'


class TekChannel(Enum):
    CH1 = 'CH1'
    CH2 = 'CH2'
    CH3 = 'CH3'
    CH4 = 'CH4'
    MATH = 'MATH'

class TekMeasurement(Enum):
    PERIOD = 'PERI'
    MIN = 'MINI'
    MAX = 'MAXI'
    FREQUENCY = 'FREQ'
    MEAN = 'MEAN'
    PK2PK = 'PK2pk'
    CRMS = 'CRMs'
    PHASE = 'PHAse'
    RISE = 'RISE'
    FALL = 'FALL'
    PWIDTH = 'PWIDTH'
    NWIDTH = 'NWIDTH'

# container initial declarations
_WaveformID = namedtuple('WaveformID', 'name coupling vertical_scale horizontal_scale points mode')
_WaveformPreamble = namedtuple('WaveformPreamble', 'point_bytes bit_depth encoding binary_fmt byte_order num_points ch_info point_fmt x_timestep point_offset x_zero x_unit y_multiplier y_zero y_offset y_unit')

# test str for waveform preamble and ID
# '1;8;BIN;RP;MSB;2500;"CH1, DC coupling, 1.0E1 V/div, 2.5e-7 s/div, 2500 points, Sample Mode",Y;1.0E-9;0;-3.2E-7;"s";4.0E-1;0.0E0,1.29E2;"Volts"\n'

class WaveformID(_WaveformID):
    @classmethod
    def from_str(cls, line:str):
        # "Ch1, DC coupling, 1.0E1 V/div, 2.5E-7 s/div, 2500 points, Sample mode";
        # 'name coupling vertical_scale horizontal_scale points mode
        ch,coupling,vertical_scale,horizontal_scale,points,mode = list(map(str.strip,line.strip('"').split(',')))
        return cls(
            ch,
            coupling[:2],
            vertical_scale,
            horizontal_scale,
            int(points.split()[0]),
            mode
        )

# BYT_NR <NR1>;BIT_NR <NR1>;ENCDG { ASC | BIN };
# BN_FMT { RI | RP };BYT_OR { LSB | MSB };NR_PT <NR1>;
# WFID <QSTRING>;PT_FMT {ENV | Y};XINCR <NR3>;
# PT_OFF <NR1>;XZERO <NR3>;XUNIT<QSTRING>;YMULT <NR3>;
# YZERO <NR3>;YOFF <NR3>;YUNIT <QSTRING>
# class WaveformPreamble(_NamedTuple):
#     point_bytes:int
#     bit_depth:int
#     encoding:TekEncoding
#     binary_fmt:TekBinFmt
#     byte_order:TekByteOrder
#     num_points:int
#     ch_info:WaveformID
#     point_fmt:TekPointFmt
#     x_timestep:float
#     point_offset:int
#     x_zero:float
#     x_unit:str
#     y_multiplier:float
#     y_zero:float
#     y_offset:float
#     y_unit:str     

#     @classmethod
#     def from_str(cls, preamble:str):
#         BYT_NR,BIT_NR,ENCDG,BN_FMT,BYT_OR,NR_PT,WFID,PT_FMT,XINCR,PT_OFF,XZERO,XUNIT,YMULT,YZERO,YOFF,YUNIT = list(map(str.strip,preamble.split(';')))
#         return cls(
#             int(BYT_NR),
#             int(BIT_NR),
#             TekEncoding(ENCDG),
#             TekBinFmt(BN_FMT),
#             TekByteOrder(BYT_OR),
#             int(NR_PT),
#             WaveformID.from_str(WFID),
#             TekPointFmt(PT_FMT),
#             float(XINCR),
#             int(PT_OFF),
#             float(XZERO),
#             XUNIT,
#             float(YMULT),
#             float(YZERO),
#             float(YOFF),
#             YUNIT
#         )


# BYT_NR <NR1>;BIT_NR <NR1>;ENCDG { ASC | BIN };
# BN_FMT { RI | RP };BYT_OR { LSB | MSB };NR_PT <NR1>;
# WFID <QSTRING>;PT_FMT {ENV | Y};XINCR <NR3>;
# PT_OFF <NR1>;XZERO <NR3>;XUNIT<QSTRING>;YMULT <NR3>;
# YZERO <NR3>;YOFF <NR3>;YUNIT <QSTRING>
class WaveformPreamble(_WaveformPreamble):            
    @classmethod
    def from_str(cls, preamble:str):
        BYT_NR,BIT_NR,ENCDG,BN_FMT,BYT_OR,NR_PT,WFID,PT_FMT,XINCR,PT_OFF,XZERO,XUNIT,YMULT,YZERO,YOFF,YUNIT = list(map(str.strip,preamble.split(';')))
        return cls(
            int(BYT_NR),
            int(BIT_NR),
            TekEncoding(ENCDG),
            TekBinFmt(BN_FMT),
            TekByteOrder(BYT_OR),
            int(NR_PT),
            WaveformID.from_str(WFID),
            TekPointFmt(PT_FMT),
            float(XINCR),
            int(PT_OFF),
            float(XZERO),
            XUNIT,
            float(YMULT),
            float(YZERO),
            float(YOFF),
            YUNIT
        )

class TekSettings(ScopeSettings):
    pass

DEFAULT_SETTINGS = TekSettings()

class TekScope(Scope):
    def __init__(self, settings:TekSettings=DEFAULT_SETTINGS,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self._settings = settings
        self._id = self.get_id()
        
    def start_acquisition(self, single=False):
        if single:
            self.send_cmd('acquire:stopafter sequence')
            self.wait(0.08)
            self.send_cmd('acquire:state on')
        else:
            raise NotImplementedError('normal triggering not supported')

    def stop_acquisition(self):
        self.send_cmd('acquire:state OFF')

    def measure(self, ch:TekChannel,measurement:TekMeasurement):
        self.send_cmd('MEASU:IMM:SOURCE {}'.format(ch.value))
        self.wait(0.08)
        self.send_cmd('MEASU:IMM:TYPE {}'.format(measurement.value))
        self.send_cmd('*OPC?')
        while self.read_response().strip() != '1':
            self.read_response() 
        self.send_cmd('MEASU:IMM:VALU?')
        return float(self.read_response().strip())

    def set_encoding(self):
        pass

    def capture_waveform(self, raw:bool=False):
        # get preamble
        self.send_cmd('WFMPre?')
        preamble = self.read_response().strip()
        # get data
        self.send_cmd('CURVE?')
        data = bytearray(self._ser.readline().strip())
        if not raw:
            # parse preamble
            preamble = WaveformPreamble.from_str(preamble)
        return preamble, data

    # @staticmethod
    # def calculate_voltages(raw_samples:_Sequence,preamble:WaveformPreamble):
    #     return [preamble.y_zero + (preamble.y_multiplier*(entry-preamble.y_offset)) for entry in raw_samples]

    # @staticmethod
    # def calculate_timesteps(samples:_Sequence,preamble:WaveformPreamble):
    #     return [preamble.x_zero + preamble.x_timestep*(i - preamble.point_offset) for i in range(len(samples))]

    @staticmethod
    def convert_raw_samples(raw_samples:_Sequence,preamble:WaveformPreamble,return_raw:bool=False):
        voltages = []
        times = []
        for idx, entry in enumerate(raw_samples):
                # XZEro + XINcr (n -- PT_OFf)
                # ((curve_in_dl – YOFF_in_dl) * YMUlt) + YZERO_in_YUNits
                times.append(preamble.x_zero + preamble.x_timestep*(idx - preamble.point_offset))
                voltages.append(preamble.y_zero + (preamble.y_multiplier*(entry-preamble.y_offset)))
        if return_raw:
            idxs = [i for i in range(len(raw_samples))]
            return raw_samples,idxs,times,voltages
        else:
            return times,voltages
        
    @staticmethod
    def save_waveform_csv(outfile:str,preamble:WaveformPreamble,data:_Sequence):
        with open(outfile,'w') as f:
            for entry in preamble:
                f.write('{}\n'.format(entry))
            f.write('index,raw,time (s),voltage (V)\n')
            for idx, entry in enumerate(data):
                # XZEro + XINcr (n -- PT_OFf)
                # ((curve_in_dl – YOFF_in_dl) * YMUlt) + YZERO_in_YUNits
                time = preamble.x_zero + preamble.x_timestep*(idx - preamble.point_offset)
                voltage = preamble.y_zero + (preamble.y_multiplier*(entry-preamble.y_offset))
                f.write('{},{},{},{}\n'.format(idx,entry,time,voltage))
