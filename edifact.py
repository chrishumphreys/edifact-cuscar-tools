from pydifact.message import Message
import json
import abc

# Implement Handler to process the edifact message and call handle_message(...)
class Handler(abc.ABC):
    @abc.abstractmethod
    def visit_codeset_element(self, data_element_schema, element, codeset, ignore_codeset_errors):
        pass

    @abc.abstractmethod
    def visit_literal_element(self, data_element_schema, element):
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

def load_codesets(verbose):
    codelists = {}
    with open('codelists.json') as json_file:
        codelists = json.load(json_file)
        for codeset in codelists:
            codeset_config = codelists[codeset]
            if verbose:
                print("Loading codeset from {}".format(codeset_config["data"]))
            with open(codeset_config["data"]) as json_file:
                codes = json.load(json_file)
            codeset_config["codes"] = codes
            codeset_config["name"] = codeset
    return codelists
        
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

def codeset_lookup(code, codeset, verbose, ignore_codeset_errors):
    try:
        return codeset["codes"][code]
    except KeyError:
        msg = "Cannot find code '{}' in codeset {} '{}'".format(code, codeset["name"], codeset["desc"])
        if verbose:
            print(msg)
        if ignore_codeset_errors:
            return { "name" : code }
        else:
            raise KeyError(msg)

def find_codeset(element_schema, codelists, verbose):
    try:
        codeset = element_schema["codeset"]
        return codelists[codeset]
    except KeyError:
        msg = "Cannot find codeset '{}' - check included in codelists.json".format(codeset)
        if verbose:
            print(msg)
        raise KeyError(msg)


def handle_element(data_element_schema, element, codelists, verbose, ignore_codeset_errors, handler):
    try:
        if is_codeset(data_element_schema) and element != '':
            codeset = find_codeset(data_element_schema, codelists, verbose)
            updated, new_value = handler.visit_codeset_element(data_element_schema, element, codeset, verbose, ignore_codeset_errors)
        else:
            updated, new_value = handler.visit_literal_element(data_element_schema, element)
        return updated, new_value
    except Exception as e:
        print("Error {} whilst printing: {}".format(e, element))
        raise

def handle_segment(segment, message_schema, codelists, verbose, ignore_codeset_errors, handler):
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
                            codelists, verbose, ignore_codeset_errors, handler)
                        if updated:
                            element[component_index] = new_value
                else:
                    # Single component data element specified - assume first is sub element
                    updated, new_value = handle_element(data_element_schema["contents"][0], element, codelists, 
                        verbose, ignore_codeset_errors, handler)
                    if updated:
                        segment.elements[index] = new_value
            else:
                #schema suggests this is a single element
                updated, new_value = handle_element(data_element_schema, element, codelists, verbose, 
                    ignore_codeset_errors, handler)
                if updated:
                    segment.elements[index] = new_value
    except:
        print("Error whilst printing segment: {}".format(segment))  
        raise  

def handle_message(message, schema, codelists, verbose, ignore_codeset_errors, show_only_unknown, handler):
    for segment in message.segments:
        if segment.tag in schema:
            if show_only_unknown:
                pass
            else:
                handle_segment(segment, schema, codelists, verbose, ignore_codeset_errors, handler)
        else:
            handler.visit_unknown_segment(segment)