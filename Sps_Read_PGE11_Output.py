#!/usr/local/sci/bin/python2.7
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# Synopsis:
#
#   Sps_Read_PGE11_Output.py <RDT .buf_section4 text file> <JSON output file>
#
# Description:
#
#   Reads the text file of RDT/PGE11 output created by the BUFR to text program
#   and outputs JSON file which is to be used in a web browser display.
#
# Copyright:
#
#   (c) Crown copyright Met Office. All rights reserved.
#   For further details please refer to the file COPYRIGHT.txt
#   which you should have received as part of this distribution.
# -----------------------------------------------------------------------------

# Modules
import datetime
import json
import logging
import sys

# Globals
phrase_mappings = {
    'ID': 'Identification number of the cloud system-',
    'Detection Method': 'Method used to diagnose the nature of the cloud system-',
    'Num vertices': 'Number of points of contour of the cloud system-',
    'Nature': 'Nature (convective or not) of the cloud system',
    'Speed': 'Speed of motion of the cloud system',
    'Direction': 'Direction of motion of the cloud system',
    'Min BT': 'Minimum value of brightness temperature at the top',
    'Mean BT': 'Average value of brightness temperature at the top',
    'Expansion rate': 'Area expansion rate of the cloud system-',
    'Cooling rate': 'Cooling rate of the cloud system-',
    'Type': 'Type of the cloud system-',
    'Phase': 'Phase of the life cycle of the cloud system',
    'CTP': 'Pressure of top of the cloud system-',
    'Lightning count': 'Number of positive cloud-to-ground lightning flashes'}


class System(object):
    """
    Class to contain RDT information for a detected system

    """
    def __init__(self):
        self.coords = []
        self.params = {}

    def add_coord(self, coords):
        self.coords.append(coords)


class CloudSystems(object):
    """
    Contains a list of System instances, created by parsing the RDT
    section4 text output file

    """
    def __init__(self, filename):
        """
        Read a section4 RDT text output file

        Args:

        * filename (string)
            RDT text file of name format:
            SAFNWC_MSG?_RDT__yyyymmddHHMM_europe______.buf_section4

        """
        self.logger = logging.getLogger()
        self.logger.info("Parsing: " + filename)

        with open(filename, 'r') as f:
            self.lines = f.read().splitlines()

        # Get some information
        self.end_of_file = False
        self.line_position = 0
        self.analysis_start = datetime.datetime(self._next_val('Year'),
                                                self._next_val('Month'),
                                                self._next_val('Day'),
                                                self._next_val('Hour'),
                                                self._next_val('Minute'))

        self.bounds = {}
        for pt in ['North West', 'South West', 'South East', 'North East']:
            self.bounds[pt] = [self._next_val('Latitude'),
                               self._next_val('Longitude', incr_line_pos=True)]

        self.total_num_systems = self._next_val('Number of cloud systems')

        self.logger.info("Analysis time start: " + str(self.analysis_start))
        self.logger.info("Region analysed")
        for k, v in self.bounds.iteritems():
            self.logger.info(" {} : {:.2f}N, {:.2f}E".format(k, v[0], v[1]))
        self.logger.info("Total num systems reported in file: " +
                         str(self.total_num_systems))

        # For storage of systems
        self.systems = []

    def _next_val(self, line, incr_line_pos=False):
        """
        Return the value from the file for the next occurrence of 'line'
        after self.line_position. Set the line number position if specified.

        """
        j = self.lines[self.line_position:]
        try:
            lnum, val = next(t for t in list(enumerate(j)) if line in t[1])
        except StopIteration:
            self.logger.warning("No more values for: " + line)
            return

        val = val.split(' ')[-1]

        if incr_line_pos:
            self.line_position += lnum + 1

        # Try converting val to a number, otherwise return string
        try:
            val = float(val)
            if val % 1 == 0:
                val = int(val)
            return val
        except ValueError:
            return val

    def _next_system(self):
        """
        Set the line position to the start of the next system, defined as
        the line after the line with the phrase:

            'Meteorological feature code for cloud'

        """
        line = 'Meteorological feature code for cloud'
        j = self.lines[self.line_position:]

        try:
            lnum, val = next(t for t in list(enumerate(j)) if line in t[1])
        except StopIteration:
            self.logger.info("No more systems in file")
            self.logger.info("Retained " + str(len(self.systems)) +
                             " systems")
            self.end_of_file = True
            return

        self.line_position += lnum + 1

    def parse_file(self, only_convective=True, keep_old=False):
        """
        Parse the contents of the file, retaining systems

        Kwargs:

        * only_convective (boolean - default = True)
            If True, retain only systems designated as 'Convective'
            (= 0 from symbol table)

        * keep_old (boolean - default = False)
            If False, don't save systems from before analysis start time

        """
        # Loop over all available systems
        while 1:

          self._next_system()
          if self.end_of_file:
              break

          s = System()

          # Get values for this system
          for k, v in phrase_mappings.iteritems():
              s.params[k] = self._next_val(v)

          # Get time associated with system
          s.datestamp = datetime.datetime(self._next_val('Year'),
                                          self._next_val('Month'),
                                          self._next_val('Day'),
                                          self._next_val('Hour'),
                                          self._next_val('Minute'))

          # Test to ignore depending on system nature
          if only_convective and s.params['Nature'] != 0:
              self.logger.debug("Ignoring non-convective system, ID: " +
                                str(s.params['ID']) + ", code: " +
                                str(s.params['Nature']))
              continue

          # Test to ignore depending on age
          if not keep_old and s.datestamp < self.analysis_start:
              self.logger.debug("Ignoring old system, ID: " +
                                str(s.params['ID']) + ", time: " +
                                str(s.datestamp))
              continue

          # Get polygon vertices
          num_vertices = self._next_val(phrase_mappings['Num vertices'])
          for v in range(num_vertices):
              s.add_coord((self._next_val('Latitude-'),
                           self._next_val('Longitude-', incr_line_pos=True)))

          # Modifications
          for param in s.params:

              # Convert temperatures from Kelvins to Celsius and round to 1 d.p
              if param in ['Min BT', 'Mean BT'] and s.params[param] > 100:
                  s.params[param] = round((s.params[param] - 273.15) * 10) / 10

              # Convert cooling rate from C/s to C/hr and round to 1 d.p
              if param in ['Cooling rate']:
                  s.params[param] = round(s.params[param] * 3600.0 * 10) / 10

              # Convert CTP from Pa to hPa
              if param in ['CTP']:
                  try:
                      s.params[param] /= 100
                  except TypeError:
                      pass

          # Append to systems list
          self.systems.append(s)

    def to_json(self):
        """
        Output the systems' information to JSON format

        """
        self.json_dict = {}

        for s in self.systems:
            uid = "feature_" + "{:0>4d}".format(s.params['ID'])
            self.json_dict[uid] = {}
            self.json_dict[uid]['coords'] = s.coords
            self.json_dict[uid]['params'] = {}

            for k, v in s.params.iteritems():
                self.json_dict[uid]['params'][k] = s.params[k]

    def json_to_file(self, filename):
        """
        Output JSON to file

        """
        with open(filename, "w") as text_file:
            text_file.write(json.dumps(self.json_dict, separators=(',', ':')))


if __name__ == "__main__":

    # Logging (remove other handlers)
    for h in logging.getLogger().handlers:
        logging.getLogger().removeHandler(h)
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG)
    logger = logging.getLogger()

    # Check command line arguments
    if len(sys.argv) > 1:
        s4_file = sys.argv[1]
        json_file = sys.argv[2]

    # Open and read RDT file
    cs = CloudSystems(s4_file)

    # Parse the file's contents
    cs.parse_file()

    # Convert to JSON format
    cs.to_json()

    # Write JSON to file
    cs.json_to_file(json_file)
