import edifact

class GenerateHandler(edifact.Handler):
    def visit_codeset_element(self, data_element_schema, element, codeset, verbose, ignore_codeset_errors):
        #Leave codesets unchanged
        return False, element

    def visit_literal_element(self, data_element_schema, element):
        #print(data_element_schema)
        if 'pii' in data_element_schema and data_element_schema['pii'] == True:
            if "random" in data_element_schema['generator']:
                return True, "XXXXXXXXX"
        return False, element

    def visit_segment(self, segment, schema):
        pass

    def visit_unknown_segment(self, segment):
        #Stop if we don't understand the message - can't be sure there isn't PII in there
        msg = 'Unknown Segment tag: {}, content: {}'.format(segment.tag, segment.elements)
        raise Exception(msg)
