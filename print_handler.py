import edifact as edifact

class PrettyPrintHandler(edifact.Handler):
    _current_segment = []

    def visit_codeset_element(self, data_element_schema, element, codeset, verbose, ignore_codeset_errors):
        print("{} : '{}' ({})".format(data_element_schema["desc"], edifact.codeset_lookup(element, codeset, 
            verbose, ignore_codeset_errors)["name"], element))
        return False, None

    def visit_literal_element(self, data_element_schema, element):
        print("{} : {}".format(data_element_schema["desc"], element))
        return False, None

    def visit_segment(self, segment, schema):
        if len(self._current_segment) > 0:
            self._current_segment.pop()
        print("> {} ({}:{}) <".format(schema['desc'], schema['optionality'], schema['cardinality']))
        self._current_segment.append(segment)

    def visit_unknown_segment(self, segment):
        print('Segment tag: {}, content: {}'.format(segment.tag, segment.elements))
