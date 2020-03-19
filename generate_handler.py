import edifact
import string
import random
from pathlib import Path



class GenerateHandler(edifact.Handler):
    _current_segment = []

    def visit_codeset_element(self, data_element_schema, element, codeset, verbose, ignore_codeset_errors):
        #leave untouched for now
        return False, element

    def visit_literal_element(self, data_element_schema, element):
        #print(data_element_schema)
        if 'pii' in data_element_schema and data_element_schema['pii'] == True:
            requested_generator = data_element_schema['generator']
            if requested_generator in self.generators:
                new_value = self.generators[requested_generator](data_element_schema, element)
                return True, new_value
            else:
                raise Exception("Unknown generator {}".format(requested_generator))
        return False, element

    def visit_segment(self, segment, schema):
        if len(self._current_segment) > 0:
            self._current_segment.pop()
        self._current_segment.append(segment)

    def visit_unknown_segment(self, segment):
        #Stop if we don't understand the message - can't be sure there isn't PII in there
        msg = 'Unknown Segment tag: {}, content: {}'.format(segment.tag, segment.elements)
        raise Exception(msg)

    # ----------------------------------------------------------------------------------------------

    generators = {}
    generated_value_store = {}
    ports = []
    gb_ports = []
    ARRIVAL_LOCATION = 60 # Codeset 3227 Arrival location value

    def random_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for x in range(size))

    def generator_random(self, data_element_schema, element):
        return self.random_generator(data_element_schema["length"])

    def generator_random_location_gb(self):
        return random.choice(self.gb_ports)

    def generator_random_location_world(self):
        return random.choice(self.ports)

    # Choose a random port form the pre-loaded port list
    # attempt to use the location_function_code from the same segment
    # if it looks like arrival - select a random GB port
    # if it is something else - select a random worldwide port
    def generator_random_location(self, data_element_schema, element):
        if self.if_in_arrival_location():
            return self.generator_random_location_gb()
        else:
            return self.generator_random_location_world()

    def if_in_arrival_location(self):
        if len(self._current_segment) > 0:
            segment = self._current_segment[-1]
            if segment.tag == "LOC":
                location_function_code = segment.elements[0]
                return int(location_function_code) == self.ARRIVAL_LOCATION
        return False

    # Generate a random identification reference
    # Attempt to use the associated party qualifier to prefix the code
    # with either: "SU" for supplier, "CN" for consignee, "CZ" for consignor so 
    # we can read who is who in the obfuscated data
    def generator_random_identification(self, data_element_schema, element):
        return self.nad_party_qualifier() + self.random_generator(15)

    # Attempt to determine the qualifier
    def nad_party_qualifier(self):
        if len(self._current_segment) > 0:
            segment = self._current_segment[-1]
            if segment.tag == "NAD":
                return segment.elements[0]
        return "UNK"


    # Generate a random address line
    def generator_random_addressline(self, data_element_schema, element):
        return self.random_generator(10) + "ADDR, TOWN, POSTCODE"

    def generator_random_transport(self, data_element_schema, element):
        return self.random_generator(20) + "TEST SHIP"

    # Generate a randome value and store it under the element descriptor
    # useful for message references which are global and used in multiple places
    # in the message 
    def generator_random_and_store(self, data_element_schema, element):
        if data_element_schema["desc"] not in self.generated_value_store:
            new_value = self.random_generator(data_element_schema["length"])
            self.generated_value_store[data_element_schema["desc"]] = new_value
        return self.generated_value_store[data_element_schema["desc"]]

    def initialise_generators(self):
        self.generators = {
            'random' : self.generator_random,
            'random_and_store' : self.generator_random_and_store,
            'random_location' : self.generator_random_location,
            'random_identification' : self.generator_random_identification,
            'random_address_line' : self.generator_random_addressline,
            'random_transport' : self.generator_random_transport
        }   

    def initialise_codesets(self):
        codeset_dir = Path("codelists")
        self.ports, self.gb_ports = self.initialise_port_codesets(codeset_dir)

    def initialise_port_codesets(self, codeset_dir):
        ports_filename = codeset_dir.joinpath("ports.dat")
        port_codes = []
        gb_port_codes = []
        with open(ports_filename, "rt") as textFile:
            for line in textFile.readlines():
                code = line.strip()
                port_codes.append(code)
                if line.startswith('GB'):
                    gb_port_codes.append(code)
        #print("Read {} port codes".format(len(port_codes)))
        return port_codes, gb_port_codes

    def initialise(self):
        self.initialise_generators()
        self.initialise_codesets()