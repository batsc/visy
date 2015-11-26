# -*- coding: iso-8859-1 -*-
import json

file = '../output/SAFNWC_MSG3_RDT__201507011515_ukamv_______.buf_section4'
outfile = '../web/features.json'

params_strings = {
    'Direction': ['Direction of motion of the cloud system', '{:>03.0f}'],
    'Speed': ['Speed of motion of the cloud system', '{:.0f} m/s'],
    'Top pressure': ['Pressureof top of the cloud system', '{:.0f} Pa'],
    'Cooling rate': ['Cooling rate of the cloud system', '{:.5f} K/s']}

codes_strings = {
    'System nature': 'Convective system or other cloud system',
    'Phase': 'Phase of the life cycle of the cloud system'}

# CODE TABLE MAPPINGS
# System nature
nature_mapping = {0: 'Convective',
                  1: 'Split from previous convecting',
                  2: 'Other',
                  3: 'Filtered (convective non active)',
                  7: 'Missing'}

# Mapping of phase to contour colour
phase_mapping = {0: {'colour': '#00ffff', 'name': 'Triggering'},
                 1: {'colour': '#ff0000', 'name': 'Growing'},
                 2: {'colour': '#9400d3', 'name': 'Mature'},
                 3: {'colour': '#0000ff', 'name': 'Decaying'}}

# Cloud system type
type_mapping = {0: 'Non-processed',
                1: 'Cloud free land',
                2: 'Cloud free sea',
                3: 'Land contaminated by snow/ice',
                4: 'Sea contaminated by snow/ice',
                5: 'Very low and cumuliform clouds',
                6: 'Very low and stratiform clouds',
                7: 'Low and cumuliform clouds',
                8: 'Low and stratiform clouds',
                9: 'Medium and cumuliform clouds',
                10: 'Medium and stratiform clouds',
                11: 'High opaque and cumuliform clouds',
                12: 'High opaque and stratiform clouds',
                13: 'Very high opaque and cumuliform clouds',
                14: 'Very high opaque and stratiform clouds',
                15: 'High semitransparent thin clouds',
                16: 'High semitransparent meanly thick clouds',
                17: 'High semitransparent thick clouds',
                18: 'High semitransparent above low or medium clouds',
                19: 'Fractional clouds (sub-pixel water clouds)',
                20: 'Undefined (by cloud mask)',
                31: 'Missing'}


class System(object):
    """
    Class to contain RDT information for a detected system

    """
    def __init__(self, id):
        self.uid = id
        self.coords = []
        self.params = {}
        self.codes = {}

    def add_coord(self, coords):
        self.coords.append(coords)


class CloudSystems(object):
    """
    Contains a list of System instances

    """
    def __init__(self):
        self.systems = []

    def extract_region(self, lonmin, lonmax, latmin, latmax):
        """
        Return a CloudSystem containing only systems within a defined
        region

        """
        pass

    def to_json(self):
        """
        Output to JSON format

        """
        self.json_dict = {}

        for system in self.systems:
            uid = "feature_" + "{:0>4d}".format(system.uid)
            self.json_dict[uid] = {}
            self.json_dict[uid]['coords'] = system.coords
            self.json_dict[uid]['params'] = {}

            for k, v in system.params.iteritems():
                self.json_dict[uid]['params'][k] = system.params[k]

            # Add parameters dictated by codes
            self.json_dict[uid]['params']['System nature'] = \
                nature_mapping[system.codes['System nature']]
            self.json_dict[uid]['params']['Phase'] = \
                phase_mapping[system.codes['Phase']]['name']
            self.json_dict[uid]['contour_colour'] = \
                phase_mapping[system.codes['Phase']]['colour']

    def json_to_file(self, filename):
        """
        Output JSON to file

        """
        with open(filename, "w") as text_file:
            text_file.write(json.dumps(self.json_dict))


def read_RDT_section4(filename):
    """
    Read text output of RDT, section 4, and return a CloudSystems instance

    """
    text_file = open(filename, 'r')
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

            # Read parameters
            for k, v in params_strings.iteritems():
                val = next(i for i in system_lines if v[0] in i).split(' ')[-1]
                try:
                    cs.systems[-1].params[k] = v[1].format(float(val))
                except:
                    cs.systems[-1].params[k] = val

            # Read code table values
            for k, v in codes_strings.iteritems():
                val = next(i for i in system_lines
                           if v in i).split(' ')[-1].split('.')[0]
                cs.systems[-1].codes[k] = int(val)

    return cs

if __name__ == "__main__":
    cs = read_RDT_section4(file)
    cs.to_json()
    cs.json_to_file(outfile)
