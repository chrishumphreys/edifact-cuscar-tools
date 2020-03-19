#Generate a new cuscar edifact message from a template file by substituting pii

import json
import edifact
import argparse
import print_handler
import generate_handler

parser = argparse.ArgumentParser(description='Generate a new CUSAR EDIFACT message from template')
parser.add_argument('input', metavar='input', type=str, help='edifact template')
parser.add_argument('output', metavar='output', nargs='?', type=str, help='edifact output file or stdout')
parser.add_argument('--verbose', action="store_true", help='be verbose')
parser.add_argument('--consignor', metavar='consignor', nargs='?', type=str, help='use specified consignor (sender) identity rather than random')
parser.add_argument('--consignee', metavar='consignee', nargs='?', type=str, help='use specified consignee (buyer) identity rather than random')
parser.add_argument('--supplier', metavar='supplier', nargs='?', type=str, help='use specified supplier identity rather than random')
parser.add_argument('--carrier', metavar='carrier', nargs='?', type=str, help='use specified carrier (Document/message issuer/sender) identity rather than random')
parser.add_argument('--arrival', metavar='arrival', nargs='?', type=str, help='use specified arrival port code rather than random GB port')


args = parser.parse_args()
verbose=False
if args.verbose:
    verbose = True
edifact_template = args.input
edifact_output = args.output

codeset_manager = edifact.CodesetManager(verbose, True)
message = edifact.load_edifact(edifact_template)
cuscar_schema = edifact.load_schema("cuscar.json", verbose)
handler = generate_handler.GenerateHandler()
specified_values = {}
if args.consignee:
    specified_values["consignee"] = args.consignee
if args.consignor:
    specified_values["consignor"] = args.consignor
if args.supplier:
    specified_values["supplier"] = args.supplier
if args.carrier:
    specified_values["carrier"] = args.carrier
if args.arrival:
    specified_values["arrival"] = args.arrival

handler.initialise(specified_values)

edifact.handle_message(message, cuscar_schema, codeset_manager, verbose, False, handler)
if edifact_output:
    edifact.save_edifact(edifact_output, message)
else:
    handler = print_handler.PrettyPrintHandler()
    edifact.handle_message(message, cuscar_schema, codeset_manager, verbose, False, handler)
