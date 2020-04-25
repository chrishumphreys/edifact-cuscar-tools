## A set of tools for manipulating Edifact CUSCAR message

### Setup

```
python3 -m venv edifact-cuscar-env
. edifact-cuscar-env/bin/activate
```

```
git clone https://github.com/nerdocs/pydifact
cd pydifact
python setup.py install
cd ..
```

### Pretty print

To pretty print the CUSCAR file:

```
python print.py sample-edifact/simple.edi 
```

To ignore missing code set values:

```
python print.py --ignore_errors sample-edifact/simple.edi
```

To only display the unknown segment definitions (so you can expand the schema):

```
python print.py --unknown sample-edifact/simple.edi  
```
### Generate from template

#### display to stdout

```
python generate.py  sample-edifact/template.edi
```

#### write to file

```
python generate.py  sample-edifact/template.edi output.edi
```

#### Specifying values

Rather than generating random values for all fields, you can specify some to use. This is useful for linking consignments together.

```
python generate.py sample-edifact/template.edi output.edi \
--consignee "A Consignee" \
--consignor "A Consignor" \
--supplier "A Supplier" \
--carrier "A Carrier" \
--arrival "GBPME"
```

### Creating synthetic data of various sizes

```
python create.py
```

You can specify various options for parties/ports in the message:

--consignor : use specified consignor (sender) identity rather than random
--consignee : use specified consignee (buyer) identity rather than random
--supplier : use specified supplier identity rather than random
--carrier : use specified carrier (Document/message issuer/sender) identity rather than random
--arrival : use specified arrival port code rather than random GB port
--departure : use specified departure port code rather than random port

You can adjust the size of the message by specifying number of equipments and consignments to include

--consignments : Number of consignments to add
--equipments : Number of equipments to add

You can also generate a template message instead of a real message for use by data-doser by specigying the --doser argument.

### Specification

used CUSCAR message specification found here:
https://www.truugo.com/edifact/d03a/cuscar/
https://www.truugo.com/edifact/d95b/cuscar/

### Extending

The schema for the segments and elements is in cuscar.json
It loads codesets from codelists.json

You can add new codesets using convert_codelist.py
