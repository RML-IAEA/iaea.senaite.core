# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2023 by it's authors.
# Some rights reserved, see README and LICENSE.

""" Life Technologies QuBit
"""
from datetime import datetime
from senaite.core.exportimport.instruments.resultsimport import \
    AnalysisResultsImporter, InstrumentCSVResultsFileParser


class QuBitCSVParser(InstrumentCSVResultsFileParser):

    def __init__(self, csv, analysiskey):
        InstrumentCSVResultsFileParser.__init__(self, csv)
        self.analysiskey = analysiskey
        self.header = None

    def _parseline(self, line):
        # Sample Id,Specimen Type,Date,Time,Reading,Unit,Concentration,Unit,Remark
        if line.startswith('Sample Id'):
            self.headers = [token.strip() for token in line.split(',')]
            self.headers[7] += '1'  # Two identical header, rename one of them.
            return 0

        # WW-01176,Blood,2010/11/02,10:33 AM,0.15   ug/ml,10.85,ng/ul,Good sample
        # WW-01175,Plasma,2010/11/02,10:33 AM,0.731 ug/ml,10.85,ng/ul,Good sample
        splitted = [token.strip() for token in line.split(',')]
        _values = dict(zip((self.headers),(splitted)))

        values = {self.analysiskey:
                    {'DefaultResult': 'Concentration',
                     'Remarks': _values['Remark'],
                     'Concentration': _values['Concentration'],
                     'Reading': _values['Reading']}
                 }
        try:
            # 2010/11/02,10:33 AM
            dtstr = '%s %s' % (_values['Date'], _values['Time'])
            dtobj = datetime.strptime(dtstr, '%Y/%m/%d %H:%M %p')
            values[self.analysiskey]['DateTime'] = dtobj.strftime("%Y%m%d %H:%M:%S")
        except Exception:
            pass

        # add result
        self._addRawResult(_values['Sample Id'], values, True)
        return 0


class QuBitImporter(AnalysisResultsImporter):

    def __init__(self, parser, context, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid=None):
        AnalysisResultsImporter.__init__(self, parser, context, override,
                                         allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
