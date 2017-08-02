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
from datetime import datetime
from typing import List, Optional

from rdflib import URIRef, Graph, BNode, RDF, XSD
from rdflib.term import Node, Literal

from i2fhirb2.fhir.fhirmetadata import FHIRMetadata
from i2fhirb2.fhir.fhirpatientdimension import FHIRPatientDimension
from i2fhirb2.fhir.fhirpatientmapping import FHIRPatientMapping
from i2fhirb2.fhir.fhirproviderdimension import FHIRProviderDimension
from i2fhirb2.fhir.fhirprovidermapping import FHIRProviderMapping
from i2fhirb2.fhir.fhirspecific import concept_code, FHIR
from i2fhirb2.fhir.fhirvisitdimension import FHIRVisitDimension
from i2fhirb2.i2b2model.data.i2b2observationfact import ObservationFact, ObservationFactKey, valuetype_blob, \
    valuetype_text, valuetype_date, valuetype_number
from i2fhirb2.sqlsupport.dynobject import DynElements


def literal_val(val: Literal) -> str:
    return '"{}"'.format(str(val).replace('\n', '\\n').replace(r'\t', '\\t'))


def boolean_val(val: Literal) -> str:
    return val.value


def date_val(val: Literal) -> datetime:
    return val.value


def datetime_val(val: Literal) -> datetime:
    return datetime.strptime(val.value, '%Y-%m-%dT%H:%M:%SZ')


def decimal_val(val: Literal) -> float:
    return float(val.value)


def gyear_val(val: Literal) -> datetime:
    return datetime.strptime(val.value, '%Y')


def gYearMonth_val(val: Literal) -> datetime:
    return datetime.strptime(val.value, '%Y-%m')


def time_val(val: Literal) -> datetime:
    return datetime.strptime(val.value, '%H:%M:%S')

# Conversion table from XSD data type to corresponding i2b2 field
literal_conversions = {
    XSD.base64Binary: (literal_val, valuetype_blob),
    XSD.boolean: (boolean_val, valuetype_text),
    XSD.date: (date_val, valuetype_date),
    XSD.dateTime: (datetime_val, valuetype_date),
    XSD.decimal: (decimal_val, valuetype_number),
    XSD.gYear: (gyear_val, valuetype_date),
    XSD.gYearMonth: (gYearMonth_val, valuetype_date),
    XSD.integer: (decimal_val, valuetype_number),
    XSD.nonNegativeInteger: (decimal_val, valuetype_number),
    XSD.positiveInteger: (decimal_val, valuetype_number),
    XSD.time: (time_val, valuetype_date)}


class FHIRObservationFact(ObservationFact):
    _t = DynElements(ObservationFact)

    def __init__(self, g: Graph, ofk: ObservationFactKey, predicate: URIRef, object: Node, instance_num: int=1):
        """
        Construct an observation fact entry
        :param g: Graph containing information about the object
        :param ofk: Observation fact key - patient, encounter, etc
        :param predicate: predicate of concept_code
        :param object: object of concept_code
        :param instance_num: instance identifier
        """
        super().__init__(ofk, concept_code(predicate))
        self._instance_num = instance_num
        self.fhir_primitive(g, object)

    @staticmethod
    def is_primitive(g: Graph, obj: Optional[Node]) -> bool:
        """
        Determine whether obj is a primitive or composite object
        :param g: Graph context for testing
        :param obj: object to test
        :return:
        """
        if obj is None or not isinstance(obj, BNode):
            return False
        obj_val = g.value(obj, FHIR.value)
        return obj_val is not None and isinstance(obj_val, Literal)

    def fhir_primitive(self, g: Graph, obj: Optional[Node]) -> None:
        assert(self.is_primitive(g, obj))
        val = g.value(obj, FHIR.value)
        # TODO: remove the conversions that aren't needed (toPython does the same thing)
        if val.datatype in literal_conversions:
            f, t = literal_conversions[val.datatype]
            if t == valuetype_text:
                self._tval_char = val.toPython()
            elif t == valuetype_number:
                self._tval_char = 'E'
                self._nval_num = val.toPython()
            elif t == valuetype_blob:
                self._observation_blob = val.toPython()
            elif t == valuetype_date:
                dt = val.toPython()
                self._tval_char = dt.strftime('%Y-%m-%d %H:%M')
                self._nval_num = (dt.year * 10000) + (dt.month * 100) + dt.day + \
                                 (((dt.hour / 100.0) + (dt.minute / 10000.0)) if isinstance(dt, datetime) else 0)
            else:
                self._tval_char = val.toPython()
            self._valtype_cd = t.code
        else:
            self._tval_char = val.toPython()
            self._valtype_cd = valuetype_text.code


class FHIRObservationFactFactory:
    """
    FHIRObservationFactFactory takes an RDF graph and generates a set of observation_fact, patient_dimension,
    visit_dimension, provider_dimension, patient_mapping and provider_mapping entries
    """

    special_processing_list = {RDF.type: None, FHIR.nodeRole: None, FHIR.index: None}

    def __init__(self, g: Graph, ofk: ObservationFactKey, subject: Optional[URIRef]):
        self.g = g
        self.ofk = ofk
        self.observation_facts = []         # type: List[FHIRObservationFact]
        self.patient_dimensions = []        # type: List[FHIRPatientDimension]
        self.provider_dimensions = []       # type: List[FHIRProviderDimension]
        self.visit_dimensions = []          # type: List[FHIRVisitDimension]
        self.patient_mappings = []          # type: List[FHIRPatientMapping]
        self.provider_mappings = []         # type: List[FHIRProviderMapping]

        # TODO: look at DomainResource embedded entries (claim-example-oral-bridge).  Perhaps we should change the
        # RDF generator to add type arcs to all resources?
        self._instance_generator = FHIRObservationFactFactory.InstanceNumFactory()
        for s in {subject} if subject else self.g.subjects(FHIR.nodeRole, FHIR.treeRoot):
            self.observation_facts += self.generate_facts(s)

    def generate_facts(self, subject: URIRef) -> List[FHIRObservationFact]:
        """
        Generate an observation fact entry for each predicate object associated with subject.  If the predicate
        is not primitive (i.e. it has a non-value BNode as a target), generate a series of modifiers for each element
        in the BNode.  Note -- this generation sorts the inputs because the order is indirectly preserved in the output
        instance numbers.
        :param subject: Subject of the observation (Patient)
        :return:
        """
        rval = []               # type: List[FHIRObservationFact]

        for conc, obj in sorted(self.g.predicate_objects(subject)):
            if conc not in self.special_processing_list:
                if FHIRObservationFact.is_primitive(self.g, obj):
                    rval.append(FHIRObservationFact(self.g, self.ofk, conc, obj))
                else:
                    rval += self.generate_modifiers(subject, conc, obj)
        return rval

    def generate_modifiers(self, subject: URIRef, concept: URIRef, obj: URIRef,
                           modifier_root: Optional[URIRef] = None, ) -> List[FHIRObservationFact]:
        rval = []               # type: List[FHIRObservationFact]
        inst_num = self._instance_generator.instance_num
        for modifier, modifier_object in sorted(self.g.predicate_objects(obj)):
            if FHIRObservationFact.is_primitive(self.g, modifier_object):
                self._instance_generator.mark_used()
                obsfact = FHIRObservationFact(self.g, self.ofk, concept, modifier_object, inst_num)
                obsfact._modifier_cd = concept_code(modifier)
                rval.append(obsfact)
            elif modifier not in self.special_processing_list:
                rval += self.generate_modifiers(subject, concept, modifier_object, modifier)
        return rval

    class InstanceNumFactory:
        def __init__(self):
            self._instance_num = 1
            self._used = True           # Instance 1 is reserved for non-modifiers

        def mark_used(self):
            self._used = True

        @property
        def instance_num(self) -> int:
            if self._used:
                self._instance_num += 1
                self._used = False
            return self._instance_num
