"""
Import TMY2 and TMY3 data.
"""

import logging
pvl_logger = logging.getLogger('pvlib')

import pdb
import re
import datetime
import dateutil
import csv 

import pandas as pd
import numpy as np

from pvlib import pvl_tools



def readtmy3(filename=None):
    '''
    Read a TMY3 file in to a pandas dataframe

    Read a TMY3 file and make a pandas dataframe of the data. Note that values
    contained in the struct are unchanged from the TMY3 file (i.e. units 
    are retained). In the case of any discrepencies between this
    documentation and the TMY3 User's Manual ([1]), the TMY3 User's Manual
    takes precedence.

    If a filename is not provided, the user will be prompted to browse to
    an appropriate TMY3 file.

    Parameters
    ----------

    filename : string 
    An optional argument which allows the user to select which
    TMY3 format file should be read. A file path may also be necessary if
    the desired TMY3 file is not in the MATLAB working path.

    Returns
    -------

    TMYDATA : DataFrame

    A pandas dataframe, is provided with the components in the table below. Note
    that for more detailed descriptions of each component, please consult
    the TMY3 User's Manual ([1]), especially tables 1-1 through 1-6. 

    meta : struct
    struct of meta data is created, which contains all 
    site metadata available in the file

    Notes
    -----

    ===============   ======  ===================  
    meta field        format  description
    ===============   ======  ===================  
    meta.altitude     Float   site elevation
    meta.latitude     Float   site latitudeitude
    meta.longitude    Float   site longitudeitude
    meta.Name         String  site name
    meta.State        String  state
    meta.TZ           Float   timezone
    meta.USAF         Int     USAF identifier
    ===============   ======  ===================  

    =============================       ======================================================================================================================================================
    TMYData field                       description
    =============================       ======================================================================================================================================================
    TMYData.Index                       A pandas datetime index. NOTE, the index is currently timezone unaware, and times are set to local standard time (daylight savings is not indcluded)
    TMYData.ETR                         Extraterrestrial horizontal radiation recv'd during 60 minutes prior to timestamp, Wh/m^2
    TMYData.ETRN                        Extraterrestrial normal radiation recv'd during 60 minutes prior to timestamp, Wh/m^2
    TMYData.GHI                         Direct and diffuse horizontal radiation recv'd during 60 minutes prior to timestamp, Wh/m^2
    TMYData.GHISource                   See [1], Table 1-4
    TMYData.GHIUncertainty              Uncertainty based on random and bias error estimates                        see [2]
    TMYData.DNI                         Amount of direct normal radiation (modeled) recv'd during 60 mintues prior to timestamp, Wh/m^2
    TMYData.DNISource                   See [1], Table 1-4
    TMYData.DNIUncertainty              Uncertainty based on random and bias error estimates                        see [2]
    TMYData.DHI                         Amount of diffuse horizontal radiation recv'd during 60 minutes prior to timestamp, Wh/m^2
    TMYData.DHISource                   See [1], Table 1-4
    TMYData.DHIUncertainty              Uncertainty based on random and bias error estimates                        see [2]
    TMYData.GHillum                     Avg. total horizontal illuminance recv'd during the 60 minutes prior to timestamp, lx
    TMYData.GHillumSource               See [1], Table 1-4
    TMYData.GHillumUncertainty          Uncertainty based on random and bias error estimates                        see [2]
    TMYData.DNillum                     Avg. direct normal illuminance recv'd during the 60 minutes prior to timestamp, lx
    TMYData.DNillumSource               See [1], Table 1-4
    TMYData.DNillumUncertainty          Uncertainty based on random and bias error estimates                        see [2]
    TMYData.DHillum                     Avg. horizontal diffuse illuminance recv'd during the 60 minutes prior to timestamp, lx
    TMYData.DHillumSource               See [1], Table 1-4
    TMYData.DHillumUncertainty          Uncertainty based on random and bias error estimates                        see [2]
    TMYData.Zenithlum                   Avg. luminance at the sky's zenith during the 60 minutes prior to timestamp, cd/m^2
    TMYData.ZenithlumSource             See [1], Table 1-4
    TMYData.ZenithlumUncertainty        Uncertainty based on random and bias error estimates                        see [1] section 2.10
    TMYData.TotCld                      Amount of sky dome covered by clouds or obscuring phenonema at time stamp, tenths of sky
    TMYData.TotCldSource                See [1], Table 1-5, 8760x1 cell array of strings
    TMYData.TotCldUnertainty            See [1], Table 1-6
    TMYData.OpqCld                      Amount of sky dome covered by clouds or obscuring phenonema that prevent observing the sky at time stamp, tenths of sky
    TMYData.OpqCldSource                See [1], Table 1-5, 8760x1 cell array of strings
    TMYData.OpqCldUncertainty           See [1], Table 1-6
    TMYData.DryBulb                     Dry bulb temperature at the time indicated, deg C
    TMYData.DryBulbSource               See [1], Table 1-5, 8760x1 cell array of strings
    TMYData.DryBulbUncertainty          See [1], Table 1-6
    TMYData.DewPoint                    Dew-point temperature at the time indicated, deg C
    TMYData.DewPointSource              See [1], Table 1-5, 8760x1 cell array of strings
    TMYData.DewPointUncertainty         See [1], Table 1-6
    TMYData.RHum                        Relatitudeive humidity at the time indicated, percent
    TMYData.RHumSource                  See [1], Table 1-5, 8760x1 cell array of strings
    TMYData.RHumUncertainty             See [1], Table 1-6
    TMYData.Pressure                    Station pressure at the time indicated, 1 mbar
    TMYData.PressureSource              See [1], Table 1-5, 8760x1 cell array of strings
    TMYData.PressureUncertainty         See [1], Table 1-6
    TMYData.Wdir                        Wind direction at time indicated, degrees from north (360 = north; 0 = undefined,calm) 
    TMYData.WdirSource                  See [1], Table 1-5, 8760x1 cell array of strings
    TMYData.WdirUncertainty             See [1], Table 1-6
    TMYData.Wspd                        Wind speed at the time indicated, meter/second
    TMYData.WspdSource                  See [1], Table 1-5, 8760x1 cell array of strings
    TMYData.WspdUncertainty             See [1], Table 1-6
    TMYData.Hvis                        Distance to discernable remote objects at time indicated (7777=unlimited), meter
    TMYData.HvisSource                  See [1], Table 1-5, 8760x1 cell array of strings
    TMYData.HvisUncertainty             See [1], Table 1-6
    TMYData.CeilHgt                     Height of cloud base above local terrain (7777=unlimited), meter
    TMYData.CeilHgtSource               See [1], Table 1-5, 8760x1 cell array of strings
    TMYData.CeilHgtUncertainty          See [1], Table 1-6
    TMYData.Pwat                        Total precipitable water contained in a column of unit cross section from earth to top of atmosphere, cm
    TMYData.PwatSource                  See [1], Table 1-5, 8760x1 cell array of strings
    TMYData.PwatUncertainty             See [1], Table 1-6
    TMYData.AOD                         The broadband aerosol optical depth per unit of air mass due to extinction by aerosol component of atmosphere, unitless
    TMYData.AODSource                   See [1], Table 1-5, 8760x1 cell array of strings
    TMYData.AODUncertainty              See [1], Table 1-6
    TMYData.Alb                         The ratio of reflected solar irradiance to global horizontal irradiance, unitless
    TMYData.AlbSource                   See [1], Table 1-5, 8760x1 cell array of strings
    TMYData.AlbUncertainty              See [1], Table 1-6
    TMYData.Lprecipdepth                The amount of liquid precipitation observed at indicated time for the period indicated in the liquid precipitation quantity field, millimeter
    TMYData.Lprecipquantity             The period of accumulatitudeion for the liquid precipitation depth field, hour
    TMYData.LprecipSource               See [1], Table 1-5, 8760x1 cell array of strings
    TMYData.LprecipUncertainty          See [1], Table 1-6
    =============================       ======================================================================================================================================================  

    References
    ----------

    [1] Wilcox, S and Marion, W. "Users Manual for TMY3 Data Sets".
    NREL/TP-581-43156, Revised May 2008.

    [2] Wilcox, S. (2007). National Solar Radiation Database 1991 2005 
    Update: Users Manual. 472 pp.; NREL Report No. TP-581-41364.

    See also
    ---------

    pvl_makelocationstruct
    pvl_readtmy2

    '''
    
    if filename is None: 					#If no filename is input
        try:
            filename = interactive_load()
        except:
            raise Exception('Interactive load failed. Tkinter not supported on this system. Try installing X-Quartz and reloading')

    head = ['USAF','Name','State','TZ','latitude','longitude','altitude']
    headerfile = open(filename,'r')
    meta = dict(zip(head,headerfile.readline().rstrip('\n').split(","))) #Read in file metadata
    meta['altitude'] = float(meta['altitude'])
    meta['latitude'] = float(meta['latitude'])
    meta['longitude'] = float(meta['longitude'])
    meta['TZ'] = float(meta['TZ'])
    meta['USAF'] = int(meta['USAF'])

    TMYData = pd.read_csv(filename, header=1,
                          parse_dates={'datetime':['Date (MM/DD/YYYY)','Time (HH:MM)']},
                          date_parser=parsedate, index_col='datetime')

    TMYData = recolumn(TMYData) #rename to standard column names

    TMYData = TMYData.tz_localize(int(meta['TZ']*3600))

    return TMYData, meta



def interactive_load():
    import Tkinter 
    from tkFileDialog import askopenfilename
    Tkinter.Tk().withdraw() #Start interactive file input
    return askopenfilename() 



def parsedate(ymd, hour):
    # stupidly complicated due to TMY3's usage of hour 24
    # and dateutil's inability to handle that. 
    offset_hour = int(hour[:2]) - 1
    offset_datetime = '{} {}:00'.format(ymd, offset_hour)
    offset_date = dateutil.parser.parse(offset_datetime)
    true_date = offset_date + dateutil.relativedelta.relativedelta(hours=1)
    return true_date



def parsetz(UTC):
    #currently not used, need to make these daylight savings unaware
    TZinfo = {-5:'EST',
              -6:'CST',
              -7:'MST',
              -8:'PST',
              -9:'AKST',
              -10:'HAST'}
    return TZinfo[UTC]



def recolumn(TMY3):
    TMY3.columns = ('ETR','ETRN','GHI','GHISource','GHIUncertainty',
    'DNI','DNISource','DNIUncertainty','DHI','DHISource','DHIUncertainty',
    'GHillum','GHillumSource','GHillumUncertainty','DNillum','DNillumSource',
    'DNillumUncertainty','DHillum','DHillumSource','DHillumUncertainty',
    'Zenithlum','ZenithlumSource','ZenithlumUncertainty','TotCld','TotCldSource',
    'TotCldUnertainty','OpqCld','OpqCldSource','OpqCldUncertainty','DryBulb',
    'DryBulbSource','DryBulbUncertainty','DewPoint','DewPointSource',
    'DewPointUncertainty','RHum','RHumSource','RHumUncertainty','Pressure',
    'PressureSource','PressureUncertainty','Wdir','WdirSource','WdirUncertainty',
    'Wspd','WspdSource','WspdUncertainty','Hvis','HvisSource','HvisUncertainty',
    'CeilHgt','CeilHgtSource','CeilHgtUncertainty','Pwat','PwatSource',
    'PwatUncertainty','AOD','AODSource','AODUncertainty','Alb','AlbSource',
    'AlbUncertainty','Lprecipdepth','Lprecipquantity','LprecipSource',
    'LprecipUncertainty') 

    return TMY3
    
    
    
#########################
#
#   TMY2 below
#
#########################



def readtmy2(filename):
    '''
    Read a TMY2 file in to a DataFrame

    Note that valuescontained in the DataFrame are unchanged from the TMY2 
    file (i.e. units  are retained). Time/Date and Location data imported from the 
    TMY2 file have been modified to a "friendlier" form conforming to modern
    conventions (e.g. N latitude is postive, E longitude is positive, the
    "24th" hour of any day is technically the "0th" hour of the next day).
    In the case of any discrepencies between this documentation and the 
    TMY2 User's Manual ([1]), the TMY2 User's Manual takes precedence.

    If a filename is not provided, the user will be prompted to browse to
    an appropriate TMY2 file.

    Parameters
    ----------
    filename : string

          an optional argument which allows the user to select which
          TMY2 format file should be read. A file path may also be necessary if
          the desired TMY2 file is not in the working path. If filename
          is not provided, the user will be prompted to browse to an
          appropriate TMY2 file.

    Returns
    -------

    TMYData : DataFrame 

          A dataframe, is provided with the following components.  Note
          that for more detailed descriptions of each component, please consult
          the TMY2 User's Manual ([1]), especially tables 3-1 through 3-6, and 
          Appendix B. 

    meta : struct

         A struct containing the metadata from the TMY2 file.

    Notes
    -----

    The structures have the following fields

    ============================     ============================================================ 
    meta Field
    ============================     ============================================================
    meta.SiteID                      Site identifier code (WBAN number), scalar unsigned integer
    meta.StationName                 Station name, 1x1 cell string
    meta.StationState                Station state 2 letter designator, 1x1 cell string
    meta.SiteTimeZone                Hours from Greenwich, scalar double
    meta.latitude                    Latitude in decimal degrees, scalar double
    meta.longitude                   Longitude in decimal degrees, scalar double
    meta.SiteElevation               Site elevation in meters, scalar double
    ============================     ============================================================

    ============================   ==========================================================================================================================================================================
    TMYData Field                       Meaning
    ============================   ==========================================================================================================================================================================
    index                           Pandas timeseries object containing timestamps
    year                              
    month                            
    day                   
    hour
    ETR                             Extraterrestrial horizontal radiation recv'd during 60 minutes prior to timestamp, Wh/m^2
    ETRN                            Extraterrestrial normal radiation recv'd during 60 minutes prior to timestamp, Wh/m^2
    GHI                             Direct and diffuse horizontal radiation recv'd during 60 minutes prior to timestamp, Wh/m^2
    GHISource                       See [1], Table 3-3
    GHIUncertainty                  See [1], Table 3-4
    DNI                             Amount of direct normal radiation (modeled) recv'd during 60 mintues prior to timestamp, Wh/m^2
    DNISource                       See [1], Table 3-3
    DNIUncertainty                  See [1], Table 3-4
    DHI                             Amount of diffuse horizontal radiation recv'd during 60 minutes prior to timestamp, Wh/m^2
    DHISource                       See [1], Table 3-3
    DHIUncertainty                  See [1], Table 3-4
    GHillum                         Avg. total horizontal illuminance recv'd during the 60 minutes prior to timestamp, units of 100 lux (e.g. value of 50 = 5000 lux)
    GHillumSource                   See [1], Table 3-3
    GHillumUncertainty              See [1], Table 3-4
    DNillum                         Avg. direct normal illuminance recv'd during the 60 minutes prior to timestamp, units of 100 lux
    DNillumSource                   See [1], Table 3-3
    DNillumUncertainty              See [1], Table 3-4
    DHillum                         Avg. horizontal diffuse illuminance recv'd during the 60 minutes prior to timestamp, units of 100 lux
    DHillumSource                   See [1], Table 3-3
    DHillumUncertainty              See [1], Table 3-4
    Zenithlum                       Avg. luminance at the sky's zenith during the 60 minutes prior to timestamp, units of 10 Cd/m^2 (e.g. value of 700 = 7,000 Cd/m^2)
    ZenithlumSource                 See [1], Table 3-3
    ZenithlumUncertainty            See [1], Table 3-4
    TotCld                          Amount of sky dome covered by clouds or obscuring phenonema at time stamp, tenths of sky
    TotCldSource                    See [1], Table 3-5, 8760x1 cell array of strings
    TotCldUnertainty                See [1], Table 3-6
    OpqCld                          Amount of sky dome covered by clouds or obscuring phenonema that prevent observing the sky at time stamp, tenths of sky
    OpqCldSource                    See [1], Table 3-5, 8760x1 cell array of strings
    OpqCldUncertainty               See [1], Table 3-6
    DryBulb                         Dry bulb temperature at the time indicated, in tenths of degree C (e.g. 352 = 35.2 C).
    DryBulbSource                   See [1], Table 3-5, 8760x1 cell array of strings
    DryBulbUncertainty              See [1], Table 3-6
    DewPoint                        Dew-point temperature at the time indicated, in tenths of degree C (e.g. 76 = 7.6 C).
    DewPointSource                  See [1], Table 3-5, 8760x1 cell array of strings
    DewPointUncertainty             See [1], Table 3-6
    RHum                            Relative humidity at the time indicated, percent
    RHumSource                      See [1], Table 3-5, 8760x1 cell array of strings
    RHumUncertainty                 See [1], Table 3-6
    Pressure                        Station pressure at the time indicated, 1 mbar
    PressureSource                  See [1], Table 3-5, 8760x1 cell array of strings
    PressureUncertainty             See [1], Table 3-6
    Wdir                            Wind direction at time indicated, degrees from east of north (360 = 0 = north; 90 = East; 0 = undefined,calm) 
    WdirSource                      See [1], Table 3-5, 8760x1 cell array of strings
    WdirUncertainty                 See [1], Table 3-6
    Wspd                            Wind speed at the time indicated, in tenths of meters/second (e.g. 212 = 21.2 m/s)
    WspdSource                      See [1], Table 3-5, 8760x1 cell array of strings
    WspdUncertainty                 See [1], Table 3-6
    Hvis                            Distance to discernable remote objects at time indicated (7777=unlimited, 9999=missing data), in tenths of kilometers (e.g. 341 = 34.1 km).
    HvisSource                      See [1], Table 3-5, 8760x1 cell array of strings
    HvisUncertainty                 See [1], Table 3-6
    CeilHgt                         Height of cloud base above local terrain (7777=unlimited, 88888=cirroform, 99999=missing data), in meters
    CeilHgtSource                   See [1], Table 3-5, 8760x1 cell array of strings
    CeilHgtUncertainty              See [1], Table 3-6
    Pwat                            Total precipitable water contained in a column of unit cross section from Earth to top of atmosphere, in millimeters
    PwatSource                      See [1], Table 3-5, 8760x1 cell array of strings
    PwatUncertainty                 See [1], Table 3-6
    AOD                             The broadband aerosol optical depth (broadband turbidity) in thousandths on the day indicated (e.g. 114 = 0.114)
    AODSource                       See [1], Table 3-5, 8760x1 cell array of strings
    AODUncertainty                  See [1], Table 3-6
    SnowDepth                       Snow depth in centimeters on the day indicated, (999 = missing data).
    SnowDepthSource                 See [1], Table 3-5, 8760x1 cell array of strings
    SnowDepthUncertainty            See [1], Table 3-6
    LastSnowfall                    Number of days since last snowfall (maximum value of 88, where 88 = 88 or greater days; 99 = missing data)
    LastSnowfallSource              See [1], Table 3-5, 8760x1 cell array of strings
    LastSnowfallUncertainty         See [1], Table 3-6
    PresentWeather                  See [1], Appendix B, an 8760x1 cell array of strings. Each string contains 10 numeric values. The string can be parsed to determine each of 10 observed weather metrics.
    ============================   ==========================================================================================================================================================================

    References
    ----------

    [1] Marion, W and Urban, K. "Wilcox, S and Marion, W. "User's Manual
    for TMY2s". NREL 1995.

    See also
    --------

    pvl_makelocationstruct 
    pvl_maketimestruct  
    pvl_readtmy3

    '''
    
    if filename is None: 					#If no filename is input
        try:
            filename = interactive_load()
        except:
            raise Exception('Interactive load failed. Tkinter not supported on this system. Try installing X-Quartz and reloading')

    string='%2d%2d%2d%2d%4d%4d%4d%1s%1d%4d%1s%1d%4d%1s%1d%4d%1s%1d%4d%1s%1d%4d%1s%1d%4d%1s%1d%2d%1s%1d%2d%1s%1d%4d%1s%1d%4d%1s%1d%3d%1s%1d%4d%1s%1d%3d%1s%1d%3d%1s%1d%4d%1s%1d%5d%1s%1d%10d%3d%1s%1d%3d%1s%1d%3d%1s%1d%2d%1s%1d'
    columns='year,month,day,hour,ETR,ETRN,GHI,GHISource,GHIUncertainty,DNI,DNISource,DNIUncertainty,DHI,DHISource,DHIUncertainty,GHillum,GHillumSource,GHillumUncertainty,DNillum,DNillumSource,DNillumUncertainty,DHillum,DHillumSource,DHillumUncertainty,Zenithlum,ZenithlumSource,ZenithlumUncertainty,TotCld,TotCldSource,TotCldUnertainty,OpqCld,OpqCldSource,OpqCldUncertainty,DryBulb,DryBulbSource,DryBulbUncertainty,DewPoint,DewPointSource,DewPointUncertainty,RHum,RHumSource,RHumUncertainty,Pressure,PressureSource,PressureUncertainty,Wdir,WdirSource,WdirUncertainty,Wspd,WspdSource,WspdUncertainty,Hvis,HvisSource,HvisUncertainty,CeilHgt,CeilHgtSource,CeilHgtUncertainty,PresentWeather,Pwat,PwatSource,PwatUncertainty,AOD,AODSource,AODUncertainty,SnowDepth,SnowDepthSource,SnowDepthUncertainty,LastSnowfall,LastSnowfallSource,LastSnowfallUncertaint'
    hdr_columns='WBAN,City,State,TZ,latitude,longitude,altitude'

    TMY2, TMY2_meta = readTMY(string, columns, hdr_columns, filename)	

    return TMY2, TMY2_meta



def parsemeta(columns,line):
    """Retrieves metadata from the top line of the tmy2 file.

    Parameters
    ----------

    Columns : string
          String of column headings in the header

    line : string
          Header string containing DataFrame

    Returns
    -------

    meta : Dict of metadata contained in the header string

    """
    rawmeta=" ".join(line.split()).split(" ") #Remove sduplicated spaces, and read in each element
    meta=rawmeta[:3] #take the first string entries
    meta.append(int(rawmeta[3]))
    longitude=(float(rawmeta[5])+float(rawmeta[6])/60)*(2*(rawmeta[4]=='N')-1)#Convert to decimal notation with S negative
    latitude=(float(rawmeta[8])+float(rawmeta[9])/60)*(2*(rawmeta[7]=='E')-1) #Convert to decimal notation with W negative
    meta.append(longitude)
    meta.append(latitude)
    meta.append(float(rawmeta[10]))	
    
    meta_dict = dict(zip(columns.split(','),meta)) #Creates a dictionary of metadata
    pvl_logger.debug('meta: {}'.format(meta_dict))
    
    return meta_dict



def readTMY(string, columns, hdr_columns, fname):
    head=1
    date=[]
    with open(fname) as infile:
        fline=0
        for line in infile:
            #Skip the header
            if head!=0:
                meta=parsemeta(hdr_columns,line)
                head-=1
                continue
            #Reset the cursor and array for each line    
            cursor=1
            part=[]
            for marker in string.split('%'):
                #Skip the first line of markers
                if marker=='':
                    continue
            
                #Read the next increment from the marker list    
                increment=int(re.findall('\d+',marker)[0])

                #Extract the value from the line in the file
                val=(line[cursor:cursor+increment])
                #increment the cursor by the length of the read value
                cursor=cursor+increment
         

                # Determine the datatype from the marker string
                if marker[-1]=='d':
                    try:
                        val=float(val)
                    except:
                        raise Exception('WARNING: In'+__name__+' Read value is not an integer" '+val+' " ')
                elif marker[-1]=='s':
                    try:
                        val=str(val)
                    except:
                        raise Exception('WARNING: In'+__name__+' Read value is not a string" '+val+' " ')
                else: 
                    raise Exception('WARNING: In'+__name__+'Improper column DataFrameure " %'+marker+' " ')
                
                part.append(val)
            
            if fline==0:
                axes=[part]
                year=part[0]+1900
                fline=1
            else:
                axes.append(part)
            
            #Create datetime objects from read data
            date.append(datetime.datetime(year=int(year),month=int(part[1]),day=int(part[2]),hour=int(part[3])-1))

    TMYData = pd.DataFrame(axes, index=date, columns=columns.split(',')).tz_localize(int(meta['TZ']*3600))

    return TMYData, meta
        

