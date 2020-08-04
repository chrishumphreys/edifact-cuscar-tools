# A set of tools for manipulating Edifact CUSCAR message

## Setup

``` bash
python3 -m venv edifact-cuscar-env
. edifact-cuscar-env/bin/activate
```

``` bash
git clone https://github.com/nerdocs/pydifact
cd pydifact
python setup.py install
cd ..
```

## Pretty print

To pretty print the CUSCAR file:

``` bash
python print.py sample-edifact/simple.edi 
```

To ignore missing code set values:

``` bash
python print.py --ignore_errors sample-edifact/simple.edi
```

To only display the unknown segment definitions (so you can expand the schema):

``` bash
python print.py --unknown sample-edifact/simple.edi  
```

## Generate from template

### display to stdout

``` bash
python generate.py  sample-edifact/template.edi
```

### write to file

``` bash
python generate.py  sample-edifact/template.edi output.edi
```

### Specifying values

Rather than generating random values for all fields, you can specify some to use. This is useful for linking consignments together.

``` bash
python generate.py sample-edifact/template.edi output.edi \
--consignee "A Consignee" \
--consignor "A Consignor" \
--supplier "A Supplier" \
--carrier "A Carrier" \
--arrival "GBPME"
```

### Creating synthetic data of various sizes

``` bash
python create.py
```

You can specify various options for parties/ports in the message:

``` bash
python create.py \
    --consignee "A Consignee" \
    --consignor "A Consignor" \
    --supplier "A Supplier" \
    --carrier "A Carrier" \
    --arrival "GBPME" \
    --departure "JPNAO" \
    --goods "A goods description" \
    --vessel "A ship name"
```

You can adjust the size of the message by specifying number of equipments and consignments to include:

``` bash
python create.py \
    --consignments 10 \
    --equipments 10
```

You can also generate a template message instead of a real message for use by data-doser by:

``` bash
python create.py \
    --doser argument.
```

### Specification

used CUSCAR message specification found here:

- <https://www.truugo.com/edifact/d03a/cuscar/>
- <https://www.truugo.com/edifact/d95b/cuscar/>

### Extending

The schema for the segments and elements is in cuscar.json
It loads codesets from codelists.json

You can add new codesets using convert_codelist.py
