from prologix_usb import Scope, ScopeSettings
from enum import Enum
from collections import namedtuple

_WaveformPreamble = namedtuple('WaveformPreamble', 'point_bytes bit_depth encoding binary_fmt byte_order num_points ch_info point_fmt x_timestep point_offset x_zero x_unit y_multiplier y_zero y_offset y_unit')
_WaveformID = namedtuple('WaveformID', 'name coupling vertical_scale horizontal_scale points mode')

class WaveformPreamble(_WaveformPreamble):
    # BYT_NR <NR1>;BIT_NR <NR1>;ENCDG { ASC | BIN };
    # BN_FMT { RI | RP };BYT_OR { LSB | MSB };NR_PT <NR1>;
    # WFID <QSTRING>;PT_FMT {ENV | Y};XINCR <NR3>;
    # PT_OFF <NR1>;XZERO <NR3>;XUNIT<QSTRING>;YMULT <NR3>;
    # YZERO <NR3>;YOFF <NR3>;YUNIT <QSTRING>
            
    @classmethod
    def from_str(cls, preamble):
        BYT_NR,BIT_NR,ENCDG,BN_FMT,BYT_OR,NR_PT,WFID,PT_FMT,XINCR,PT_OFF,XZERO,XUNIT,YMULT,YZERO,YOFF,YUNIT = list(map(str.strip,preamble.split(';')))
        # point_bytes 
        # bit_depth 
        # encoding 
        # binary_fmt 
        # byte_order 
        # num_points 
        # ch_info 
        # point_fmt 
        # x_timestep
        # point_offset
        # x_zero
        # x_unit
        # y_multiplier
        # y_zero
        # y_offset
        # y_unit
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

class WaveformID(_WaveformID):
    @classmethod
    def from_str(cls, line):
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

class TekBinFmt(Enum):
    ReversePolishSigned = 'RI'
    ReversePolishUnsigned = 'RP'

class TekByteOrder(Enum):
    MSB = 'MSB'
    LSB = 'LSB'

class TekEncoding(Enum):
    ASCII = 'ASCII'
    BIN = 'BIN'

class TekPointFmt(Enum):
    ENV = 'ENV'
    Y = 'Y'

class TekSettings(ScopeSettings):
    pass

DEFAULT_SETTINGS = TekSettings()

class TekScope(Scope):
    def __init__(self, settings:TekSettings=DEFAULT_SETTINGS,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self._settings = settings
        self._id = self.get_id()
        
    def capture_waveform(self, raw=False):
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

    @staticmethod
    def save_waveform_csv(outfile,preamble,data):
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