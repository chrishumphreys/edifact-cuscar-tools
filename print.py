# Pretty print a cuscar edifact message

import json
import edifact
import argparse
import print_handler

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

codeset_manager = edifact.CodesetManager(verbose, ignore_codeset_errors)
message = edifact.load_edifact(edifact_filename)
cuscar_schema = edifact.load_schema("cuscar.json", verbose)
handler = print_handler.PrettyPrintHandler()
edifact.handle_message(message, cuscar_schema, codeset_manager, verbose, show_only_unknown, handler)