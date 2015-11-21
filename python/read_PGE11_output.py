# -*- coding: iso-8859-1 -*-
import json

file = '../output/SAFNWC_MSG3_RDT__201507011515_ukamv_______.buf_section4'
outfile = '../web/features.json'

params_strings = {
    'direction' : 'Direction of motion of the cloud system',
    'speed' : 'Speed of motion of the cloud system',
    'Top pressure' : 'Pressureof top of the cloud system'}

class System(object):
    ''' Class to contain RDT information for a detected system
    '''
    def __init__(self, id):
        self.uid = id
        self.coords = []
        self.params = {}
    def add_coord(self, coords):
        self.coords.append(coords)

class CloudSystems(object):
    ''' Contains systems
    '''
    def __init__(self):
        self.systems = []
    def extract_region(self, lonmin, lonmax, latmin, latmax):
        ''' Return a CloudSystem containing only systems within a defined
            region
        '''
        pass
    def to_json(self):
        ''' Output to JSON format
        '''
        self.json_dict = {}
        for system in self.systems:
            uid = "feature_" + "{:0>4d}".format(system.uid)
            self.json_dict[uid] = {} 
            self.json_dict[uid]['coords'] = system.coords
            self.json_dict[uid]['params'] = {}
            for k, v in system.params.iteritems():
                self.json_dict[uid]['params'][k] = system.params[k]
    def json_to_file(self, filename):
        ''' Output JSON to file
        '''
        with open(filename, "w") as text_file:
            text_file.write(json.dumps(self.json_dict))
        
# Define a list for cloud systems
def read_RDT_section4(filename):
    ''' Read text output of RDT, section 4
    '''
    text_file=open(filename,'r')
    lines = text_file.read().splitlines()
    text_file.close()
    
    # Indices of start of all systems
    startstring = 'Number of points of contour of the cloud system'
    startinds = [i for i, s in enumerate(lines) if startstring in s]
    
    # Loop over all systems and store details
    cs = CloudSystems()
    for uid, ind in enumerate(startinds):
        if uid == len(startinds) - 1:
            system_lines = lines[ind:-1]
        else:
            system_lines = lines[ind:startinds[uid + 1]]
            
        # Only keep this system if the convective type is known
        convstring = 'Convective system or other cloud system'
        conv_line = [i for i in system_lines if convstring in i]
        if conv_line[0].split(' ')[-1].upper().find('UNKNOWN') < 0:
            cs.systems.append(System(uid))
        
            # Grab all coords (lons follow lats)
            latstring = 'Latitude (coarse accuracy) of one point of contour'
            latinds = [i for i, s in enumerate(system_lines) if latstring in s]
            for latind in latinds:
                lat_lon = [float(system_lines[latind].split(' ')[-1])]
                lat_lon.append(float(system_lines[latind + 1].split(' ')[-1]))
                cs.systems[-1].add_coord(lat_lon)

            # Add parameters
            for k, v in params_strings.iteritems():
                cs.systems[-1].params[k] = next(i for i in system_lines if v in i).split(' ')[-1].split('.')[0]
                
    return cs
    
if __name__ == "__main__":
    cs = read_RDT_section4(file)
    cs.to_json()
    cs.json_to_file(outfile)