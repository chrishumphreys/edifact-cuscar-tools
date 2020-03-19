import edifact as edifact

class PrettyPrintHandler(edifact.Handler):
    _current_segment = []

    def visit_codeset_element(self, data_element_schema, element, codeset_manager, codeset_code, verbose):
        codeset_value = codeset_manager.codeset_lookup(element, codeset_code)["name"]
        print("{} : '{}' ({})".format(data_element_schema["desc"], codeset_value, element))
        return False, None

    def visit_literal_element(self, data_element_schema, element, codeset_manager):
        print("{} : {}".format(data_element_schema["desc"], element))
        return False, None

    def visit_segment(self, segment, schema):
        if len(self._current_segment) > 0:
            self._current_segment.pop()
        print("> {} ({}:{}) <".format(schema['desc'], schema['optionality'], schema['cardinality']))
        self._current_segment.append(segment)

    def visit_unknown_segment(self, segment):
        print('Segment tag: {}, content: {}'.format(segment.tag, segment.elements))
