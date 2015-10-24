# -*- coding: iso-8859-1 -*-
import json

file = '../output/SAFNWC_MSG3_RDT__201507011515_ukamv_______.buf_section4'

class System(object):
    ''' Class to contain RDT information for a detected system
    '''
    def __init__(self, id, num_vertices):
        self.uid = id
        self.num_vertices = num_vertices
        self.coords = []
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
    def scale_coords(self, width, height):
        ''' Scale the coords to be contained within width/height box
        '''
        # Max/min lats and lons (not sure of this)
        self.latmax = max([item[0] for val in self.systems for item in val.coords])
        self.latmin = min([item[0] for val in self.systems for item in val.coords])
        self.lonmax = max([item[1] for val in self.systems for item in val.coords])
        self.lonmin = min([item[1] for val in self.systems for item in val.coords])
        self.mx = width / (self.lonmax - self.lonmin)
        self.cx = width - self.mx * self.lonmax
        self.my = height / (self.latmax - self.latmin)
        self.cy = height - self.my * self.latmax
        
        for i, system in enumerate(self.systems):
            self.systems[i].coords_scaled = []
            for coords in system.coords:
                self.systems[i].coords_scaled.append(
                    [self.my * coords[0] + self.cy, self.mx * coords[1] + self.cx])
    def to_json_file(self, filename):
        ''' Output to JSON format
        '''
        json_dict = {}
        for system in self.systems:
            uid = "feature_" + "{:0>4d}".format(system.uid)
            json_dict[uid] = {} 
            json_dict[uid]['coords'] = system.coords_scaled
        
        with open(filename, "w") as text_file:
            text_file.write(json.dumps(json_dict))
        
# Define a list for cloud systems
def read_RDT_section4(filename):
    ''' Read text output of RDT, section 4
    '''
    cs = CloudSystems()

    uid = 0
    with open(file) as f:
        for line in f:
            # New system if num vertices specified
            if line.find('Number of points of contour of the cloud system') > 0:
                uid += 1
                num_vertices = int(line.split(' ')[-1])
                cs.systems.append(System(uid, num_vertices))
                continue
            # If these are coordinates, they alternate latitude, then longitude
            if line.find('Latitude (coarse accuracy) of one point of contour') > 0:
                lat_lon = [float(line.split(' ')[-1])]
                continue
            elif line.find('Longitude (coarse accuracy) of one point of contour') > 0:
                lat_lon.append(float(line.split(' ')[-1]))
                cs.systems[-1].add_coord(lat_lon)
                continue
    return cs