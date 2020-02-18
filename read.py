import json
from pydifact.message import Message
import argparse


parser = argparse.ArgumentParser(description='Pretty print CUSAR EDIFACT message')
parser.add_argument('file', metavar='file', type=str,
                   help='edifact file to print')
parser.add_argument('--ignore_errors', action="store_true",
                   help='ignore missing codeset errors')
parser.add_argument('--unknown', action="store_true",
                   help='only display unknown segments')
parser.add_argument('--verbose', action="store_true",
                   help='be verbose')

args = parser.parse_args()
ignore_codeset_errors = False
if args.ignore_errors:
    ignore_codeset_errors = True
show_only_unknown=False
if args.unknown:
    show_only_unknown = True
verbose=False
if args.verbose:
    verbose = True
edifact_filename = args.file

message = Message.from_file(edifact_filename)

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
        

cuscar_schema = {}
with open('cuscar.json') as json_file:
    cuscar_schema = json.load(json_file)
    #print(cuscar_schema)

def print_unb(segment):
    print('UNB')

def is_composite(component):
    return "contents" in component 

def is_codeset(component):
    return "codeset" in component 

def codeset_lookup(code, codeset):
    try:
        return codeset["codes"][code]
    except KeyError as e:
        msg = "Cannot find code '{}' in codeset {} '{}'".format(code, codeset["name"], codeset["desc"])
        print(msg)
        if ignore_codeset_errors:
            return { "name" : code }
        else:
            raise KeyError(msg)

def find_codeset(element_schema):
    try:
        codeset = element_schema["codeset"]
        return codelists[codeset]
    except KeyError as e:
        msg = "Cannot find codeset '{}' - check included in codelists.json".format(codeset)
        print(msg)
        raise KeyError(msg)

def pretty_print_element(data_element_schema, element):
    try:
        if is_codeset(data_element_schema) and element != '':
            codeset = find_codeset(data_element_schema)
            print("{} : '{}' ({})".format(data_element_schema["desc"], codeset_lookup(element, codeset)["name"], element))
        else:
            print("{} : {}".format(data_element_schema["desc"], element))
    except Exception as e:
        print("Error {} whilst printing: {}".format(e, element))
        raise

def pretty_print_segment(segment):
    try:
        schema = cuscar_schema[segment.tag]
        print("> {} ({}:{}) <".format(schema['desc'], schema['optionality'], schema['cardinality']))
        #print(schema["contents"])
        #print(segment)
        for index, element in enumerate(segment.elements, start=0):
            data_element_schema = schema["contents"][index]
            if is_composite(data_element_schema):
                # schema suggests this is a composite element
                print("{}:".format(data_element_schema["desc"]))
                if isinstance(element, list):
                    # multiple component data elements specified
                    for component_index, component_element in enumerate(element, start=0):
                        component_schema = data_element_schema["contents"][component_index]
                        pretty_print_element(component_schema, component_element)
                else:
                    # Single component data element specified - assume first is sub element
                    pretty_print_element(data_element_schema["contents"][0], element)
            else:
                #schema suggests thi is a single element
                pretty_print_element(data_element_schema, element)
    except:
        print("Error whilst printing segment: {}".format(segment))  
        raise  

for segment in message.segments:
    #if segment.tag == 'UNB':
    #    print_unb(segment)
    if segment.tag in cuscar_schema:
        if show_only_unknown:
            pass
        else:
            pretty_print_segment(segment)
    else:
        print('Segment tag: {}, content: {}'.format(
            segment.tag, segment.elements))