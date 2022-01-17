# markdown2json-converter-py

A simple python script to convert markdown table files to json schema and description list (.tpl). Almost a direct translation of the JavaScript script as found in https://github.com/csihda/markdown2json-converter.

## Usage

Put your markdown table file in the same directory as the script and run:

```
python mdconverter.py
```

If successfull json and .tpl files are created in the same directory for each markdown table file.

## Accepted mardown table format

The table must always satisfy this format
| Key | Title | Description | Type | Required | Default value |
| ------------------- | ------------------------- | --------------------------------------------------------------------------------- | ------- | -------- | ------------- |
|Keyword for the field. Must not be too long and contain white spaces| Title for the field | Description of the field | any type in {string, number, integer, boolean, array} | any value in {true, false} | Default value for this field, can be left empty|

## Example

Markdown table:
| Key | Title | Description | Type | Required | Default value |
| ----------- | ------------------------- | ------------------------------------------- | ------- | -------- | ------------- |
| stringType | String Type Field | A field that accepts a string type input. | string | true | |
| numberType | Number Type Field [Unit] | A field that accepts a number type input. | number | true | |
| integerType | Integer Type Field [Unit] | A field that accepts an integer type input. | integer | false | |
| booleanType | Boolean Type Field | A field that accepts a boolean type input. | boolean | true | |
| arrayType | Array Type Field | A field that accepts an array type input. | array | true | |

Converted json schema based on the table:

```
{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "id": "some schema id",
    "title": "some schema title",
    "description": "some schema description",
    "type": "object",
    "properties": {
        "stringType": {
            "title": "String Type Field",
            "description": "A field that accepts a string type input.",
            "type": "string"
        },
        "numberType": {
            "title": "Number Type Field [Unit]",
            "description": "A field that accepts a number type input.",
            "type": "number"
        },
        "integerType": {
            "title": "Integer Type Field [Unit]",
            "description": "A field that accepts an integer type input.",
            "type": "integer"
        },
        "booleanType": {
            "title": "Boolean Type Field",
            "description": "A field that accepts a boolean type input.",
            "type": "boolean"
        },
        "arrayType": {
            "title": "Array Type Field",
            "description": "A field that accepts an array type input.",
            "type": "array"
        }
    },
    "required": [
        "stringType",
        "numberType",
        "booleanType",
        "arrayType"
    ]
}
```

Converted description list (.tpl) based on the table:

```
<dl>
<dt>String Type Field</dt>
<dd>A field that accepts a string type input.</dd>
<dt>Number Type Field [Unit]</dt>
<dd>A field that accepts a number type input.</dd>
<dt>Integer Type Field [Unit]</dt>
<dd>A field that accepts an integer type input.</dd>
<dt>Boolean Type Field</dt>
<dd>A field that accepts a boolean type input.</dd>
<dt>Array Type Field</dt>
<dd>A field that accepts an array type input.</dd>
</dl>
```
