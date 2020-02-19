#Generate a new cuscar edifact message from a template file by substituting pii

import json
import edifact
import argparse
import print_handler
import generate_handler

parser = argparse.ArgumentParser(description='Generate a new CUSAR EDIFACT message from template')
parser.add_argument('input', metavar='input', type=str, help='edifact template')
parser.add_argument('output', metavar='output', nargs='?', type=str, help='edifact output file or stdout')
parser.add_argument('--ignore_errors', action="store_true", help='ignore missing codeset errors')
parser.add_argument('--verbose', action="store_true", help='be verbose')

args = parser.parse_args()
ignore_codeset_errors = False
if args.ignore_errors:
    ignore_codeset_errors = True
verbose=False
if args.verbose:
    verbose = True
edifact_template = args.input
edifact_output = args.output

codelists = edifact.load_codesets(verbose)
message = edifact.load_edifact(edifact_template)
cuscar_schema = edifact.load_schema("cuscar.json", verbose)
handler = generate_handler.GenerateHandler()
edifact.handle_message(message, cuscar_schema, codelists, verbose, ignore_codeset_errors, False, handler)
if edifact_output:
    edifact.save_edifact(edifact_output, message)
else:
    handler = print_handler.PrettyPrintHandler()
    edifact.handle_message(message, cuscar_schema, codelists, verbose, ignore_codeset_errors, False, handler)
