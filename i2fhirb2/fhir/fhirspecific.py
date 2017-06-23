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
from rdflib import Namespace, Graph, URIRef
from rdflib.namespace import split_uri

# Namespaces
W5 = Namespace("http://hl7.org/fhir/w5#")
FHIR = Namespace("http://hl7.org/fhir/")

# Namespace map from URI to nsname
nsmap = {str(W5): "W5",
         str(FHIR): "FHIR"}


# List of W5 categores that should not be included in the output
w5_infrastructure_categories = {W5.conformance, W5.infrastructure, W5.information}

# List of predicates that aren't a direct part of the i2b2 structure
skip_fhir_predicates = {FHIR['index'], FHIR.nodeRole, FHIR['id']}

# List of FHIR 'primitive' types, not to be further expanded
fhir_primitives = {FHIR.Reference}


class AnonNS:
    _nsnum = 0

    def __init__(self):
        self._nsnum += 1
        self.ns = 'ns{}'.format(self._nsnum)


def concept_path(subject: URIRef) -> str:
    """
    Convert subject into an i2b2 concept path fragment.
    Example: Patient.status --> Patient\\status\\
    :param subject: FHIR URI
    :return: i2b2 path fragment
    """
    return split_uri(subject)[1].replace('.', '\\') + '\\'


def concept_code(subject: URIRef) -> str:
    """
    Return the i2b2 concept code for subject
    :param subject: URI to convert
    :return: 'ns:code' form of URI
    """
    ns, code = split_uri(subject)
    if ns not in nsmap:
        nsmap[ns] = AnonNS().ns
    return '{}:{}'.format(nsmap[ns], code)


def concept_name(g: Graph, subject: URIRef) -> str:
    """
    Return the i2b2 concept name for subject
    :param g: Graph - used to access label
    :param subject: concept subject
    :return: Name derived from lable if it exists otherwise the URI itself
    """
    # Note - labels appear to have '.' in them as well
    return str(g.label(subject, split_uri(subject)[1])).replace('.', ' ')


def modifier_path(modifier: URIRef) -> str:
    """
    Convert modifier uri into an i2b2 modifier path fragment, removing the first part of the name
    Example: CodedEntry.code.text --> code\\text\\
    :param modifier: FHIR URI
    :return: i2b2 path fragment
    """
    path = split_uri(modifier)[1]
    return (path.split('.', 1)[1].replace('.', '\\') if '.' in path else path) + '\\'


def modifier_code(modifier: URIRef) -> str:
    """
    Return the i2b2 modifier code for subject.  Output is same as concept_code
    :param modifier:
    :return:
    """
    return concept_code(modifier)


def modifier_name(g: Graph, modifier: URIRef) -> str:
    """
    Return the i2b2 concept name for modifier removing the first part of the name
    :param g: Graph - used to access label
    :param modifier: concept subject
    :return: Name derived from lable if it exists otherwise the URI itself
    """
    default_name = split_uri(modifier)[1]
    full_name = str(g.label(modifier, default_name))
    if '.' in full_name:
        full_name = default_name.split('.', 1)[1]        # Remove first name segment
    return full_name.replace('.', ' ')
