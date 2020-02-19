import edifact
import string
import random


generated_value_store = {}

def random_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def generator_random(data_element_schema, element):
    return random_generator(data_element_schema["length"])

def generator_random_and_store(data_element_schema, element):
    if data_element_schema["desc"] not in generated_value_store:
        new_value = random_generator(data_element_schema["length"])
        generated_value_store[data_element_schema["desc"]] = new_value
    return generated_value_store[data_element_schema["desc"]]

generators = {
    'random' : generator_random,
    'random_and_store' : generator_random_and_store,
    'random_location' : generator_random
}


class GenerateHandler(edifact.Handler):
    def visit_codeset_element(self, data_element_schema, element, codeset, verbose, ignore_codeset_errors):
        #leave untouched for now
        return False, element

    def visit_literal_element(self, data_element_schema, element):
        #print(data_element_schema)
        if 'pii' in data_element_schema and data_element_schema['pii'] == True:
            requested_generator = data_element_schema['generator']
            if requested_generator in generators:
                new_value = generators[requested_generator](data_element_schema, element)
                return True, new_value
            else:
                raise Exception("Unknown generator {}".format(requested_generator))
        return False, element

    def visit_segment(self, segment, schema):
        pass

    def visit_unknown_segment(self, segment):
        #Stop if we don't understand the message - can't be sure there isn't PII in there
        msg = 'Unknown Segment tag: {}, content: {}'.format(segment.tag, segment.elements)
        raise Exception(msg)
