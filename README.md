## A set of tools for manipulating Edifact CUSCAR message

### Setup

python3 -m venv edifact-cuscar-env
. edifact-cuscar-env-env/bin/activate

git clone https://github.com/nerdocs/pydifact
python setup.py install

### Pretty print

To pretty print the CUSCAR file:

python print.py sample-edifact/sample.edi 

To ignore missing code set values:

python print.py --ignore_errors sample-edifact/sample.edi

To only display the unknown segment definitions (so you can expand the schema):

python print.py --unknown sample-edifact/sample.edi  

### Generate from template

#### display to stdout

python generate.py  sample-edifact/template.edi

#### write to file

python generate.py  sample-edifact/template.edi output.edi

### Specification

used CUSCAR message specification found here:
https://www.truugo.com/edifact/d03a/cuscar/

### Extending

The schema for the segments and elements is in cuscar.json
It loads codesets from codelists.json

You can add new codesets using convert_codelist.py
