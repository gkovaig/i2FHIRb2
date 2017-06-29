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

import unittest

from rdflib import Graph


class PrimitiveIssueTestCase(unittest.TestCase):
    """ The fhir.ttl ontology has been updated and, among the fixes, the FHIR primitive types are now subclasses
    of FHIR.Primitive -- the current conversion tools are putting them in with a visual attribute of "DA"
    """
    def test_primitive(self):
        from i2fhirb2.fhir.fhirontologytable import FHIROntologyTable
        from i2fhirb2.fhir.fhirspecific import FHIR
        g = Graph()
        g.load('../data/w5.ttl', format="turtle")
        g.load('../data/fhir.ttl', format="turtle")
        mdt = FHIROntologyTable(g)
        self.assertTrue(mdt.is_primitive(FHIR.string))
        self.assertFalse(mdt.is_primitive(FHIR.CodeableConcept))
        self.assertTrue(mdt.is_primitive(FHIR.uri))
        self.assertTrue(mdt.is_primitive(FHIR.index))


if __name__ == '__main__':
    unittest.main()