# Copyright (c) 2017, Mayo Clinic
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#     Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#     Neither the name of the Mayo Clinic nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
import os
import unittest
from collections import OrderedDict
from datetime import datetime

from i2fhirb2.fhir.fhirmodifierdimension import FHIRModifierDimension
from i2fhirb2.fhir.fhirspecific import W5, FHIR
from i2fhirb2.i2b2model.metadata.i2b2modifierdimension import ModifierDimension
from tests.utils.base_test_case import BaseTestCase
from tests.utils.shared_graph import shared_graph


class ModifierDimensionTestCase(BaseTestCase):
    dirname, _ = os.path.split(os.path.abspath(__file__))
    g = shared_graph

    def test_basics(self):
        from i2fhirb2.i2b2model.metadata.i2b2modifierdimension import ModifierDimension
        ModifierDimension._clear()
        ModifierDimension.graph = self.g
        ModifierDimension.download_date = datetime(2017, 5, 25)
        ModifierDimension.sourcesystem_cd = "FHIR"
        ModifierDimension.import_date = datetime(2017, 5, 25)
        md = ModifierDimension(W5["cause"], "\\FHIR\\w5\\who\\")
        self.assertAlmostNow(md.update_date)
        ModifierDimension.update_date = datetime(2001, 12, 1)
        expected = OrderedDict([
             ('modifier_path', '\\FHIR\\w5\\who\\cause\\'),
             ('modifier_cd', 'W5:cause'),
             ('name_char', 'W5 cause'),
             ('modifier_blob', ''),
             ('update_date', datetime(2001, 12, 1, 0, 0)),
             ('download_date', datetime(2017, 5, 25, 0, 0)),
             ('import_date', datetime(2017, 5, 25, 0, 0)),
             ('sourcesystem_cd', 'FHIR'),
             ('upload_id', None)])
        self.assertEqual(expected, md._freeze())

        md = ModifierDimension(FHIR.Account.balance, "\\FHIR\\")
        expected = OrderedDict([('modifier_path', '\\FHIR\\Account\\balance\\'),
                                ('modifier_cd', 'FHIR:Account.balance'),
                                ('name_char', 'FHIR Account balance'),
                                ('modifier_blob', ''),
                                ('update_date', datetime(2001, 12, 1, 0, 0)),
                                ('download_date', datetime(2017, 5, 25, 0, 0)),
                                ('import_date', datetime(2017, 5, 25, 0, 0)),
                                ('sourcesystem_cd', 'FHIR'),
                                ('upload_id', None)])
        self.assertEqual(expected, md._freeze())

    def test_deep_nesting_1(self):

        ModifierDimension._clear()
        ModifierDimension.sourcesystem_cd = "FHIR STU3"
        ModifierDimension.update_date = datetime(2017, 5, 25, 13, 0)

        ot = FHIRModifierDimension(self.g)
        self.assertEqual([
            ('\\FHIR\\CodeableConcept\\coding\\',
             'FHIR:CodeableConcept.coding',
             'FHIR CodeableConcept coding'),
            ('\\FHIR\\CodeableConcept\\text\\',
             'FHIR:CodeableConcept.text',
             'FHIR CodeableConcept text')],
            list((e.modifier_path, e.modifier_cd, e.name_char) for e in
                 sorted(ot.dimension_list(domain=FHIR.CodeableConcept))))

    def test_deep_nesting_2(self):
        ModifierDimension._clear()
        ModifierDimension.sourcesystem_cd = "FHIR STU3"
        ModifierDimension.update_date = datetime(2017, 5, 25, 13, 0)

        ot = FHIRModifierDimension(self.g)
        self.assertEqual([
                        '\\FHIR\\Observation\\component\\code\\',
                        '\\FHIR\\Observation\\component\\dataAbsentReason\\',
                        '\\FHIR\\Observation\\component\\interpretation\\',
                        '\\FHIR\\Observation\\component\\referenceRange\\',
                        '\\FHIR\\Observation\\component\\valueAttachment\\',
                        '\\FHIR\\Observation\\component\\valueBoolean\\',
                        '\\FHIR\\Observation\\component\\valueCodeableConcept\\',
                        '\\FHIR\\Observation\\component\\valueDateTime\\',
                        '\\FHIR\\Observation\\component\\valueInteger\\',
                        '\\FHIR\\Observation\\component\\valuePeriod\\',
                        '\\FHIR\\Observation\\component\\valueQuantity\\',
                        '\\FHIR\\Observation\\component\\valueRange\\',
                        '\\FHIR\\Observation\\component\\valueRatio\\',
                        '\\FHIR\\Observation\\component\\valueSampledData\\',
                        '\\FHIR\\Observation\\component\\valueString\\',
                        '\\FHIR\\Observation\\component\\valueTime\\'],
                     list(e.modifier_path for e in
                          sorted(ot.dimension_list(domain=FHIR.ObservationComponentComponent))))

if __name__ == '__main__':
    unittest.main()
