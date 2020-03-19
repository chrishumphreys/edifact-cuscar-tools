from pydifact.message import Message
import json
import abc

class CodesetManager():
    def __init__(self, verbose, ignore_codeset_errors):
        self._verbose = verbose
        self._ignore_codeset_errors = ignore_codeset_errors
        self.load_codesets()

    def load_codesets(self):
        self.codelists = {}
        with open('codelists.json') as json_file:
            self.codelists = json.load(json_file)
            for codeset in self.codelists:
                codeset_config = self.codelists[codeset]
                if self._verbose:
                    print("Loading codeset from {}".format(codeset_config["data"]))
                with open(codeset_config["data"]) as json_file:
                    codes = json.load(json_file)
                codeset_config["codes"] = codes
                codeset_config["name"] = codeset

    def _find_codeset(self, codeset_code):
        try:
            return self.codelists[codeset_code]
        except KeyError:
            msg = "Cannot find codeset '{}' - check included in codelists.json".format(codeset_code)
            if self._verbose:
                print(msg)
            raise KeyError(msg)

    def codeset_lookup(self, code, codeset_code):
        codeset = self._find_codeset(codeset_code)
        try:
            return codeset["codes"][code]
        except KeyError:
            msg = "Cannot find code '{}' in codeset {} '{}'".format(code, codeset["name"], codeset["desc"])
            if self._verbose:
                print(msg)
            if self._ignore_codeset_errors:
                return { "name" : code }
            else:
                raise KeyError(msg)

# Implement Handler to process the edifact message and call handle_message(...)
class Handler(abc.ABC):
    @abc.abstractmethod
    def visit_codeset_element(self, data_element_schema, element, codeset_manager, codeset_code, verbose):
        pass

    @abc.abstractmethod
    def visit_literal_element(self, data_element_schema, element, codeset_manager):
        pass

    @abc.abstractmethod
    def visit_segment(self, segment, schema):
        pass

    @abc.abstractmethod
    def visit_unknown_segment(self, segment):
        pass

def load_edifact(edifact_filename):
    return Message.from_file(edifact_filename)

def save_edifact(edifact_filename, message):
    with open(edifact_filename, 'w') as edifact_file:
        edifact_file.write(message.serialize())
    print("Edifact written to:{}".format(edifact_filename))
 
def load_schema(schema_file, verbose):
    with open(schema_file) as json_file:
        cuscar_schema = json.load(json_file)
        if (verbose):
            print(cuscar_schema)
        return cuscar_schema

def is_composite(component):
    return "contents" in component 

def is_codeset(component):
    return "codeset" in component 

def schema_codeset_code(component):
    return component["codeset"] 


def handle_element(data_element_schema, element, codeset_manager, verbose, handler):
    try:
        if is_codeset(data_element_schema) and element != '':
            codeset_code = schema_codeset_code(data_element_schema)
            updated, new_value = handler.visit_codeset_element(data_element_schema, element, codeset_manager, 
            codeset_code, verbose)
        else:
            updated, new_value = handler.visit_literal_element(data_element_schema, element, codeset_manager)
        return updated, new_value
    except Exception as e:
        print("Error {} whilst printing: {}".format(e, element))
        raise

def handle_segment(segment, message_schema, codeset_manager, verbose, handler):
    try:
        schema = message_schema[segment.tag]
        handler.visit_segment(segment, schema)
        if (verbose):
            print(schema["contents"])
            print(segment)
        for index, element in enumerate(segment.elements, start=0):
            data_element_schema = schema["contents"][index]
            if is_composite(data_element_schema):
                # schema suggests this is a composite element
                if verbose:
                    print("{}:".format(data_element_schema["desc"]))
                if isinstance(element, list):
                    # multiple component data elements specified
                    for component_index, component_element in enumerate(element, start=0):
                        component_schema = data_element_schema["contents"][component_index]
                        updated, new_value = handle_element(component_schema, component_element, 
                            codeset_manager, verbose, handler)
                        if updated:
                            element[component_index] = new_value
                else:
                    # Single component data element specified - assume first is sub element
                    updated, new_value = handle_element(data_element_schema["contents"][0], element, codeset_manager, 
                        verbose, handler)
                    if updated:
                        segment.elements[index] = new_value
            else:
                #schema suggests this is a single element
                updated, new_value = handle_element(data_element_schema, element, codeset_manager, verbose, handler)
                if updated:
                    segment.elements[index] = new_value
    except:
        print("Error whilst printing segment: {}".format(segment))  
        raise  

def handle_message(message, schema, codeset_manager, verbose, show_only_unknown, handler):
    for segment in message.segments:
        if segment.tag in schema:
            if show_only_unknown:
                pass
            else:
                handle_segment(segment, schema, codeset_manager, verbose, handler)
        else:
            handler.visit_unknown_segment(segment)