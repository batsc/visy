# -*- coding: iso-8859-1 -*-

file = '../output/SAFNWC_MSG3_RDT__201507011515_ukamv_______.buf_section4'

class System(object):
    ''' Class to contain RDT information for a detected system
    '''
    def __init__(self, id, num_vertices):
        self.uid = uid
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
        
# Define a list for cloud systems
cs = CloudSystems()

uid = 0
with open(file) as f:
    for line in f:
        # New system if num vertices specified
        if line.find('Number of points of contour of the cloud system') > 0:
            uid += 1
            num_vertices = int(line.split(' ')[-1])
            cs.systems.append(system(uid, num_vertices))
            continue
        # If these are coordinates, they alternate latitude, then longitude
        if line.find('Latitude (coarse accuracy) of one point of contour') > 0:
            lat_lon = [float(line.split(' ')[-1])]
            continue
        elif line.find('Longitude (coarse accuracy) of one point of contour') > 0:
            lat_lon.append(float(line.split(' ')[-1]))
            cloud_systems[-1].add_coord(lat_lon)
            continue
