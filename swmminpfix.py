import re
from pathlib import Path, PureWindowsPath
from shutil import move

def change_start_end_date(fswmminp):
    pass

def add_to_fname(fname, directory=None, append='_edited', suffix=None, rename=None):
    fpath = Path(fname).resolve()
    newname = rename if rename else fpath.stem
    if directory is None:
        directory = fpath.parent
    else:
        directory = (fpath.parent / directory).resolve()
    if suffix == None:
        return directory / (newname + append + fpath.suffix)
    else:
        return directory / (newname + append + '.' + suffix)
    
def replace_time_series_files(fswmminp, basedir):
    '''
    Read a SWMM input file and replace file paths for external time-series to 
    use the provided base directory. The revised file is written to a new file
    appended with "_edited". 

    :param fswmminp: The SWMM input file
    :param basedir: The base directory where the time-series files are located

    '''
    
    # Get new path to write
    fswmminp_edited = add_to_fname(fswmminp, append='_edited')
    
    # Status flag of file contents
    ts_status = 0 # 0 = not yet reached, 1 = reached, 2 = past
    
    # Pattern to match a section
    section_pat = re.compile(r'\[\w*\]')
    
    with open(fswmminp) as f, open(fswmminp_edited, 'w') as f2:

        for line in f:
            
            # Determine if you are in time series section
            # 0 = not yet reached, 1 = reached, 2 = past section
            if '[TIMESERIES]' in line:
                ts_status = 1
            elif ts_status == 1 and re.match(section_pat, line):
                ts_status = 2
            
            # In the time series section, modify path in line
            if ts_status == 1 and 'FILE' in line:
                ts_name, _, oldname = line.strip().split()
                wpath = PureWindowsPath(oldname[1:-1])
                # newname = windowspath.parent.name / windowspath.name
                newname = Path(wpath.parent.name) / wpath.name
                newpath = (Path(basedir) / newname).resolve()
                TS0path = (Path(basedir) / "TS0.dat").resolve()
                if newpath.exists():
                    # f2.write(f'{ts_name} FILE "{newpath}"\n')
                    f2.write(f'{ts_name} FILE "{TS0path}"\n')
                
            # Not in the time series section, just write the same line
            else:
                f2.write(line)

def remove_inflows(fswmminp):
    '''
    Read a SWMM input file and comments out all lines in the inflows section
    The revised file *replaces* the provided SWMM file.
    
    :param fswmminp: The SWMM input file
    '''

    fdest = add_to_fname(fswmminp, append='_tmp')

    # Status flag of file contents
    inflow_status = 0 # 0 = not yet reached, 1 = reached, 2 = past
    
    # Pattern to match a section
    section_pat = re.compile(r'\[\w*\]')
    
    with open(fswmminp) as f, open(fdest, 'w') as f2:

        for line in f:
            
            # Determine if you are in time series section
            # 0 = not yet reached, 1 = reached, 2 = past section
            if '[INFLOWS]' in line:
                inflow_status = 1
            elif inflow_status == 1 and re.match(section_pat, line):
                inflow_status = 2

            # In the inflows section, remove lines
            if inflow_status == 1 and line.strip() not in ('', '[INFLOWS]'):
                f2.write(f";{line}") # Comment out using ;
                
            # Not in the inflows section, just write the same line
            else:
                f2.write(line)
    
    # Replace the fswmm file provided
    move(fdest, fswmminp)

if __name__ == '__main__':
    
    # Replace all filepaths in time series section for all SWMM inputs
    FSWMMINP = [
        'C:\\Users\\Anthony\\Desktop\\EPA SWMM\\Newport_010423b\\Newport_042220AZ2.inp'
    ]
    
    for f in FSWMMINP:
        replace_time_series_files(f, 'C:\\Users\\Anthony\\Desktop\\EPA SWMM\\InputFiles')
    
    print('TODO: change end date in preamble')
    print('Done')
    
    