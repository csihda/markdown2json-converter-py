import json
import os
from pathlib import Path
from re import findall
from copy import deepcopy
import re

# markdown table column
ID = 0
KEY = 1
TITLE = 2
UNIT = 3
DESCRIPTION = 4
TYPE = 5
OCC = 6
ALLOWED_VAL = 7


def delete_empty_array(_dict):
    """Delete empty array values recursively from all of the dictionaries"""
    for key, value in list(_dict.items()):
        if isinstance(value, dict):
            delete_empty_array(value)
        elif value == []:
            del _dict[key]
        elif isinstance(value, list):
            for v_i in value:
                if isinstance(v_i, dict):
                    delete_empty_array(v_i)

    return _dict


def index_containing_substring(the_list, substring):
    for i, s in enumerate(the_list):
        if substring in s:
            return i
    return -1


def get_rid_of_empty(arr):
    res = []
    for i in arr:
        if i.strip() != '':
            res.append(i)
    return res


def validate_table(markdown_table):
    messages = []
    result = True
    try:
        markdown_array_rep = json.dumps(markdown_table).replace('"', "")
        markdown_array_rep = markdown_array_rep.split(
            '\\n')  # split based on the new lines

        markdown_array_rep = get_rid_of_empty(markdown_array_rep)
        # check the first row
        # convert string to array
        for i in range(0, len(markdown_array_rep)):
            row = markdown_array_rep[i]
            row = row.split("|")
            # remove first and last elements
            row = row[1:-1]
            # trim the excess spaces after and before a text
            if i == 0:
                row = [text.strip().lower() for text in row]
                if row != ["id", "key", "title", "unit", "description", "type", "occ", "allowed values"]:
                    result = False
                    messages.append("Typo(s) found in the first row")
            elif i == 1:
                #print("Validation: skipping second row")
                None
            else:
                row = [text.strip() for text in row]
                # check first coloumn / ID
                if len(row[ID].split(".")) > 2:
                    result = False
                    messages.append(
                        'Typo is found in "Id" of row no. {0} : |{1}|'.format(i-1, row[ID]))
                # check second coloumn / KEY
                if row[KEY] == "":
                    result = False
                    messages.append(
                        '"Key" must not be empty. Row no. {0}'.format(i-1))
                # check sixth coloumn / TYPE
                if row[TYPE].lower() not in ["string", "number", "integer", "boolean", ""]:
                    result = False
                    messages.append(
                        '"Type" must be one of these types: "string", "number", "integer", or "boolean". Row no. {0}: {1}'.format(i-1, row[TYPE]))
                # check seventh coloumn / OCC
                minmax = row[OCC].split("-")
                all_positive_integer_regex = '^\d+$'
                if row[OCC] == "":
                    result = False
                    messages.append(
                        '"Occ" should not be empty. Row no. {}'.format(i-1))
                elif len(minmax) > 1:
                    if re.match(all_positive_integer_regex, minmax[0]):
                        minmax[0] = minmax[0]
                    else:
                        result = False
                        messages.append(
                            'Typo is found in "Occ" of row no. {0}: |{1}|'.format(i-1, row[OCC]))
                    if not re.match(all_positive_integer_regex, minmax[1]):
                        if minmax[1] != "n":
                            result = False
                            messages.append(
                                'Typo is found in "Occ" of row no. {0}: |{1}|'.format(i-1, row[OCC]))
                    elif minmax[1] == "0":
                        result = False
                        messages.append(
                            'Max. part of "Occ" cannot be zero. Row no. {0}: |{1}|'.format(i-1, row[OCC]))
                    # check if max is bigger than min
                    if re.match(all_positive_integer_regex, minmax[0]) and re.match(all_positive_integer_regex, minmax[1]):
                        min = int(minmax[0])
                        max = int(minmax[1])
                        if min >= max:
                            result = False
                            messages.append(
                                'Min. value of "Occ" cannot be equal or bigger than the Max. value. Row no. {0}: |{1}|'.format(i-1, row[OCC]))
                # check eight coloumn / ALLOWED_VAL
                # specific check for number and integer types
                # TO DO:
                # 1. Implement validation for min and mix keywords for types: integer, number, string (char)
                if row[TYPE].lower() == "number":
                    # check first whether ALLOWED_VAL is supposed to be enumerate or min and max
                    maxmin_mode = False
                    if "max:" in row[ALLOWED_VAL].replace(" ", "").lower():
                        print("Max keyword detected")
                        maxmin_mode = True
                        maxmin_keyword = row[ALLOWED_VAL].replace(
                            " ", "").lower().split(";")
                        # check if the max keyword value is valid
                        indx = index_containing_substring(
                            maxmin_keyword, "max:")
                        maxmin_keyword = maxmin_keyword[indx]
                        maxmin_keyword = maxmin_keyword.split(":")
                        try:
                            maxmin_keyword = float(maxmin_keyword[1])
                        except:
                            result = False
                            messages.append('Typo found in "Allowed values". Row no. {0}: |{1}|'.format(
                                i-1, row[ALLOWED_VAL]))
                    if "min:" in row[ALLOWED_VAL].replace(" ", "").lower():
                        print("Min keyword detected")
                        maxmin_mode = True
                        maxmin_keyword = row[ALLOWED_VAL].replace(
                            " ", "").lower().split(";")
                        # check if the min keyword value is valid
                        indx = index_containing_substring(
                            maxmin_keyword, "min:")
                        maxmin_keyword = maxmin_keyword[indx]
                        maxmin_keyword = maxmin_keyword.split(":")
                        try:
                            maxmin_keyword = float(maxmin_keyword[1])
                        except:
                            result = False
                            messages.append('Typo found in "Allowed values". Row no. {0}: |{1}|'.format(
                                i-1, row[ALLOWED_VAL]))
                    if not maxmin_mode:
                        # enumerate
                        values = row[ALLOWED_VAL].split(";")
                        if not values == ['']:
                            try:
                                values = [float(value) for value in values]
                            except:
                                result = False
                                messages.append('Typo found in "Allowed values". Row no. {0}: |{1}|'.format(
                                    i-1, row[ALLOWED_VAL]))
                if row[TYPE].lower() == "integer":
                    # check first whether ALLOWED_VAL is supposed to be enumerate or min and max
                    maxmin_mode = False
                    if "max:" in row[ALLOWED_VAL].replace(" ", "").lower():
                        print("Max keyword detected")
                        maxmin_mode = True
                        maxmin_keyword = row[ALLOWED_VAL].replace(
                            " ", "").lower().split(";")
                        # check if the max keyword value is valid
                        indx = index_containing_substring(
                            maxmin_keyword, "max:")
                        maxmin_keyword = maxmin_keyword[indx]
                        maxmin_keyword = maxmin_keyword.split(":")
                        try:
                            maxmin_keyword = int(maxmin_keyword[1])
                        except:
                            result = False
                            messages.append('Typo found in "Allowed values". Row no. {0}: |{1}|'.format(
                                i-1, row[ALLOWED_VAL]))
                    if "min:" in row[ALLOWED_VAL].replace(" ", "").lower():
                        print("Min keyword detected")
                        maxmin_mode = True
                        maxmin_keyword = row[ALLOWED_VAL].replace(
                            " ", "").lower().split(";")
                        # check if the min keyword value is valid
                        indx = index_containing_substring(
                            maxmin_keyword, "min:")
                        maxmin_keyword = maxmin_keyword[indx]
                        maxmin_keyword = maxmin_keyword.split(":")
                        try:
                            maxmin_keyword = int(maxmin_keyword[1])
                        except:
                            result = False
                            messages.append('Typo found in "Allowed values". Row no. {0}: |{1}|'.format(
                                i-1, row[ALLOWED_VAL]))
                    # enumerate
                    if not maxmin_mode:
                        values = row[ALLOWED_VAL].split(";")
                        if not values == ['']:
                            k = i - 1
                            integer_result = True
                            try:
                                # first turn it to float
                                values = [float(value) for value in values]
                                for j in range(0, len(values)):
                                    value = values[j]
                                    if not (value % 1 == 0):
                                        result = False
                                        integer_result = False
                                    else:
                                        values[j] = int(value)
                                if integer_result == False:
                                    messages.append('Typo found in "Allowed values". Row no. {0}: |{1}|'.format(
                                        k, row[ALLOWED_VAL]))
                            except Exception as e:
                                result = False
                                messages.append('Typo found in "Allowed values". Row no. {0}: |{1}|'.format(
                                    k, row[ALLOWED_VAL]))
                if row[TYPE].lower() == "string":
                    # check first whether ALLOWED_VAL is supposed to be enumerate or min and max
                    maxmin_mode = False
                    if "max:" in row[ALLOWED_VAL].replace(" ", "").lower():
                        print("Max keyword detected")
                        maxmin_mode = True
                        maxmin_keyword = row[ALLOWED_VAL].replace(
                            " ", "").lower().split(";")
                        # check if the max keyword value is valid
                        indx = index_containing_substring(
                            maxmin_keyword, "max:")
                        maxmin_keyword = maxmin_keyword[indx]
                        maxmin_keyword = maxmin_keyword.split(":")
                        try:
                            maxmin_keyword = int(maxmin_keyword[1])
                        except:
                            result = False
                            messages.append('Typo found in "Allowed values". Row no. {0}: |{1}|'.format(
                                i-1, row[ALLOWED_VAL]))
                    if "min:" in row[ALLOWED_VAL].replace(" ", "").lower():
                        print("Min keyword detected")
                        maxmin_mode = True
                        maxmin_keyword = row[ALLOWED_VAL].replace(
                            " ", "").lower().split(";")
                        # check if the min keyword value is valid
                        indx = index_containing_substring(
                            maxmin_keyword, "min:")
                        maxmin_keyword = maxmin_keyword[indx]
                        maxmin_keyword = maxmin_keyword.split(":")
                        try:
                            maxmin_keyword = int(maxmin_keyword[1])
                        except:
                            result = False
                            messages.append('Typo found in "Allowed values". Row no. {0}: |{1}|'.format(
                                i-1, row[ALLOWED_VAL]))
                if row[TYPE].lower() == "" and row[ALLOWED_VAL] != "":
                    result = False
                    messages.append('Object or array type cannot have "Allowed values". Row no. {0}: |{1}|'.format(
                        i-1, row[ALLOWED_VAL]))
        return result, messages

    except Exception as e:
        print(e)
        messages.append(
            "The table is really wrong, the converter did not understand the table at all. Skipping this file.")
        return result, messages


def main():
    global ID, KEY, TITLE, UNIT, DESCRIPTION, TYPE, OCC, ALLOWED_VAL
    # check if there are markdowns file within the folder
    filelist = list(Path('.').glob('**/*.md'))

    # exclude README.md files
    readme_index = []
    for i in range(0, len(filelist)):
        if str(filelist[i].name).lower() == 'readme.md':
            readme_index.append(i)
    if len(readme_index) > 1:
        for index in sorted(readme_index, reverse=True):
            del filelist[index]

    # early exist when no markdowns are found
    if len(filelist) == 0:
        print("No markdown files were found.")
        return
    else:
        print("{} markdown table(s) found".format(len(filelist)))

    # read each available markdown and process it
    for file in filelist:
        with open(str(file), 'r') as f:
            print(">>> converting {}...".format(str(file)))
            # file name without extension
            filename = str(file).replace(".md", "")

            # read the content of the file
            content = f.read()

            markdown_array_rep = json.dumps(content).replace('"', "")
            markdown_array_rep = markdown_array_rep.split(
                '\\n')  # split based on the new lines

            # validate, the file content, whether it has the right structure
            result, messages = validate_table(content)
            if not result:
                for message in messages:
                    print(message)
                print(">>> skipping this file: {}.md".format(filename))
                return

            # create initial schema/dict
            schema = {}
            schema["$schema"] = "http://json-schema.org/draft-04/schema#"
            schema["id"] = "some schema id"
            schema["title"] = "some schema title"
            schema["description"] = "some schema description"
            schema["type"] = "object"
            schema["properties"] = {}
            schema["required"] = []

            # go through markdown_array_rep, and create schema property for each element
            # but first and second get rid of the first row
            markdown_array_rep = markdown_array_rep[2:]
            # get rid of empty element
            markdown_array_rep = get_rid_of_empty(markdown_array_rep)
            list_iter = iter(markdown_array_rep)
            i = 1
            current_subschema_idx = 0
            current_row_type = ""
            for row in list_iter:
                # convert string to array
                row = row.split("|")
                # remove first and last elements
                row = row[1:-1]
                # trim the excess spaces after and before a text
                row = [text.strip() for text in row]

                # first, check if the current row is actually within a subschema
                if current_row_type == "array_subschema":
                    # add a new property element into the schema
                    upper_row = markdown_array_rep[current_subschema_idx]
                    # convert string to array
                    upper_row = upper_row.split("|")
                    # remove first and last elements
                    upper_row = upper_row[1:-1]
                    # trim the excess spaces after and before a text
                    upper_row = [text.strip() for text in upper_row]
                    if not upper_row[KEY] == "":
                        schema["properties"][upper_row[KEY]
                                             ]["items"]["properties"][row[KEY]] = {}
                        if row[OCC][0] == "1":
                            schema_required = schema["properties"][upper_row[KEY]
                                                                   ]["items"]["required"]
                            schema_required.append(row[KEY])
                            schema["properties"][upper_row[KEY]
                                                 ]["items"]["required"] = schema_required

                    else:
                        print('"Key" is not found at row {}'.format(i))
                        exit()
                    # add title to the new element, if applicable
                    if not row[TITLE] == "":
                        schema["properties"][upper_row[KEY]
                                             ]["items"]["properties"][row[KEY]]["title"] = row[TITLE]
                    # add unit to the new element, if applicable
                    if not row[UNIT] == "":
                        schema["properties"][upper_row[KEY]]["items"]["properties"][row[KEY]
                                                                                    ]["title"] = row[TITLE]+f" [{row[UNIT]}]"
                    # add description to the new element
                    if not row[DESCRIPTION] == "":
                        schema["properties"][upper_row[KEY]]["items"]["properties"][row[KEY]
                                                                                    ]["description"] = row[DESCRIPTION]
                    if not row[TYPE] == "":
                        schema["properties"][upper_row[KEY]
                                             ]["items"]["properties"][row[KEY]]["type"] = row[TYPE].lower()
                    # TO DO:
                    # 1. Implement max and min keywords for types: number, integer, string (character)
                    if not row[ALLOWED_VAL] == "":
                        maxmin_mode = False
                        if "max:" in row[ALLOWED_VAL].replace(" ", "").lower():
                            maxmin_mode = True
                            maxmin_keyword = row[ALLOWED_VAL].replace(
                                " ", "").lower()
                            maxmin_keyword = maxmin_keyword.split(";")
                            indx = index_containing_substring(
                                maxmin_keyword, "max:")
                            maxmin_keyword = maxmin_keyword[indx]
                            maxmin_keyword = maxmin_keyword.split(":")
                            maxmin_keyword = maxmin_keyword[1]
                            if row[TYPE] == "string":
                                schema["properties"][upper_row[KEY]]["items"]["properties"][row[KEY]]["maxLength"] = int(
                                    maxmin_keyword)
                            if row[TYPE] == "number":
                                schema["properties"][upper_row[KEY]]["items"]["properties"][row[KEY]]["maximum"] = float(
                                    maxmin_keyword)
                            if row[TYPE] == "integer":
                                schema["properties"][upper_row[KEY]]["items"]["properties"][row[KEY]]["maximum"] = int(
                                    maxmin_keyword)
                        if "min:" in row[ALLOWED_VAL].replace(" ", "").lower():
                            maxmin_mode = True
                            maxmin_keyword = row[ALLOWED_VAL].replace(
                                " ", "").lower()
                            maxmin_keyword = maxmin_keyword.split(";")
                            indx = index_containing_substring(
                                maxmin_keyword, "min:")
                            maxmin_keyword = maxmin_keyword[indx]
                            maxmin_keyword = maxmin_keyword.split(":")
                            maxmin_keyword = maxmin_keyword[1]
                            if row[TYPE] == "string":
                                schema["properties"][upper_row[KEY]]["items"]["properties"][row[KEY]]["minLength"] = int(
                                    maxmin_keyword)
                            if row[TYPE] == "number":
                                schema["properties"][upper_row[KEY]]["items"]["properties"][row[KEY]]["minimum"] = float(
                                    maxmin_keyword)
                            if row[TYPE] == "integer":
                                schema["properties"][upper_row[KEY]]["items"]["properties"][row[KEY]]["minimum"] = int(
                                    maxmin_keyword)
                        if not maxmin_mode:
                            enum_values = row[ALLOWED_VAL].split(";")
                            enum_values = [val.strip() for val in enum_values]
                            schema["properties"][upper_row[KEY]
                                                 ]["items"]["properties"][row[KEY]]["enum"] = enum_values
                    if len(row[OCC].split("-")) > 1:
                        schema["properties"][upper_row[KEY]
                                             ]["items"]["properties"][row[KEY]]["type"] = "array"
                        schema["properties"][upper_row[KEY]
                                             ]["items"]["properties"][row[KEY]]["items"] = {}
                        schema["properties"][upper_row[KEY]]["items"]["properties"][row[KEY]
                                                                                    ]["items"]["type"] = row[TYPE].lower()

                    # check if next iter is still "array_subschema"
                    try:
                        next_row = markdown_array_rep[i]
                        # convert string to array
                        next_row = next_row.split("|")
                        # remove first and last elements
                        next_row = next_row[1:-1]
                        # trim the excess spaces after and before a text
                        next_row = [text.strip() for text in next_row]
                        # print("next_row:", next_row, "line 109")
                        if len(next_row[ID].split(".")) < 2:
                            current_row_type = ""
                        i += 1
                    except:
                        print("Finished")
                elif current_row_type == "subschema":
                    # add a new property element into the schema
                    upper_row = markdown_array_rep[current_subschema_idx]
                    # convert string to array
                    upper_row = upper_row.split("|")
                    # remove first and last elements
                    upper_row = upper_row[1:-1]
                    # trim the excess spaces after and before a text
                    upper_row = [text.strip() for text in upper_row]
                    # print("upper row:",upper_row)
                    if not upper_row[KEY] == "":
                        schema["properties"][upper_row[KEY]
                                             ]["properties"][row[KEY]] = {}
                        if row[OCC][0] == "1":
                            schema_required = schema["properties"][upper_row[KEY]]["required"]
                            schema_required.append(row[KEY])
                            schema["properties"][upper_row[KEY]
                                                 ]["required"] = schema_required
                    else:
                        print('"Key" is not found at row {}'.format(i))
                        exit()
                    # add title to the new element, if applicable
                    if not row[TITLE] == "":
                        schema["properties"][upper_row[KEY]
                                             ]["properties"][row[KEY]]["title"] = row[TITLE]
                    # add unit to the new element, if applicable
                    if not row[UNIT] == "":
                        schema["properties"][upper_row[KEY]]["properties"][row[KEY]
                                                                           ]["title"] = row[TITLE]+f" [{row[UNIT]}]"
                    # add description to the new element
                    if not row[DESCRIPTION] == "":
                        schema["properties"][upper_row[KEY]]["properties"][row[KEY]
                                                                           ]["description"] = row[DESCRIPTION]
                    if not row[TYPE] == "":
                        schema["properties"][upper_row[KEY]
                                             ]["properties"][row[KEY]]["type"] = row[TYPE].lower()
                    # TO DO:
                    # 1. Implement max and min keywords for types: number, integer, string (character)
                    if not row[ALLOWED_VAL] == "":
                        maxmin_mode = False
                        if "max:" in row[ALLOWED_VAL].replace(" ", "").lower():
                            maxmin_mode = True
                            maxmin_keyword = row[ALLOWED_VAL].replace(
                                " ", "").lower()
                            maxmin_keyword = maxmin_keyword.split(";")
                            indx = index_containing_substring(
                                maxmin_keyword, "max:")
                            maxmin_keyword = maxmin_keyword[indx]
                            maxmin_keyword = maxmin_keyword.split(":")
                            maxmin_keyword = maxmin_keyword[1]
                            if row[TYPE] == "string":
                                schema["properties"][upper_row[KEY]]["properties"][row[KEY]]["maxLength"] = int(
                                    maxmin_keyword)
                            if row[TYPE] == "number":
                                schema["properties"][upper_row[KEY]]["properties"][row[KEY]]["maximum"] = float(
                                    maxmin_keyword)
                            if row[TYPE] == "integer":
                                schema["properties"][upper_row[KEY]]["properties"][row[KEY]]["maximum"] = int(
                                    maxmin_keyword)
                        if "min:" in row[ALLOWED_VAL].replace(" ", "").lower():
                            maxmin_mode = True
                            maxmin_keyword = row[ALLOWED_VAL].replace(
                                " ", "").lower()
                            maxmin_keyword = maxmin_keyword.split(";")
                            indx = index_containing_substring(
                                maxmin_keyword, "min:")
                            maxmin_keyword = maxmin_keyword[indx]
                            maxmin_keyword = maxmin_keyword.split(":")
                            maxmin_keyword = maxmin_keyword[1]
                            if row[TYPE] == "string":
                                schema["properties"][upper_row[KEY]]["properties"][row[KEY]]["minLength"] = int(
                                    maxmin_keyword)
                            if row[TYPE] == "number":
                                schema["properties"][upper_row[KEY]]["properties"][row[KEY]]["minimum"] = float(
                                    maxmin_keyword)
                            if row[TYPE] == "integer":
                                schema["properties"][upper_row[KEY]]["properties"][row[KEY]]["minimum"] = int(
                                    maxmin_keyword)

                        if not maxmin_mode:
                            enum_values = row[ALLOWED_VAL].split(";")
                            enum_values = [val.strip() for val in enum_values]
                            schema["properties"][upper_row[KEY]
                                                 ]["properties"][row[KEY]]["enum"] = enum_values

                    if len(row[OCC].split("-")) > 1:
                        schema["properties"][upper_row[KEY]
                                             ]["properties"][row[KEY]]["type"] = "array"
                        schema["properties"][upper_row[KEY]
                                             ]["properties"][row[KEY]]["items"] = {}
                        schema["properties"][upper_row[KEY]]["properties"][row[KEY]
                                                                           ]["items"]["type"] = row[TYPE].lower()
                    # check if next iter is still "array_subschema"
                    try:
                        next_row = markdown_array_rep[i]
                        # convert string to array
                        next_row = next_row.split("|")
                        # remove first and last elements
                        next_row = next_row[1:-1]
                        # trim the excess spaces after and before a text
                        next_row = [text.strip() for text in next_row]
                        # print("next_row:", next_row, "line 155")
                        if len(next_row[ID].split(".")) < 2:
                            current_row_type = ""
                        i += 1
                    except:
                        print("Finished")
                else:
                    # add a new property element into the schema
                    if not row[KEY] == "":
                        schema["properties"][row[KEY]] = {}
                        # handle required
                        if row[OCC][0] == "1":
                            schema_required = schema["required"]
                            schema_required.append(row[KEY])
                            schema["required"] = schema_required
                    else:
                        print('"Key" is not found at row {}'.format(i))
                        exit()

                    # first add common keywords
                    # add title to the new element, if applicable
                    if not row[TITLE] == "":
                        schema["properties"][row[KEY]]["title"] = row[TITLE]
                    # add unit to the new element, if applicable
                    if not row[UNIT] == "":
                        schema["properties"][row[KEY]
                                             ]["title"] = row[TITLE]+f" [{row[UNIT]}]"
                    # add description to the new element
                    if not row[DESCRIPTION] == "":
                        schema["properties"][row[KEY]
                                             ]["description"] = row[DESCRIPTION]
                    # add type to the new element
                    if not row[TYPE] == "":
                        schema["properties"][row[KEY]
                                             ]["type"] = row[TYPE].lower()
                    else:
                        # check if this row is actually an object or array with a subschema
                        # by checking the next id
                        next_row = markdown_array_rep[i]
                        # convert string to array
                        next_row = next_row.split("|")
                        # remove first and last elements
                        next_row = next_row[1:-1]
                        # trim the excess spaces after and before a text
                        next_row = [text.strip() for text in next_row]
                        if (len(next_row[ID].split(".")) == 2) and (len(row[OCC].split("-")) == 2):
                            # then it is an array with a subschema
                            # add object type to the row
                            schema["properties"][row[KEY]]["type"] = "array"
                            # add properties keywords
                            schema["properties"][row[KEY]]["items"] = {}
                            schema["properties"][row[KEY]
                                                 ]["items"]["type"] = "object"
                            schema["properties"][row[KEY]
                                                 ]["items"]["required"] = []
                            schema["properties"][row[KEY]
                                                 ]["items"]["properties"] = {}
                            current_subschema_idx = i-1
                            current_row_type = "array_subschema"
                            # assign min and max items
                            minmax = row[OCC].split("-")
                            if not minmax[0] == "0":
                                schema["properties"][row[KEY]
                                                     ]["minItems"] = int(minmax[0])
                            if not minmax[1] == "n":
                                schema["properties"][row[KEY]
                                                     ]["maxItems"] = int(minmax[1])
                        elif (len(next_row[ID].split(".")) == 2) and (len(row[OCC]) < 2):
                            # print("then this is a pure object")

                            # add object type to the row
                            schema["properties"][row[KEY]]["type"] = "object"
                            # add properties keywords
                            schema["properties"][row[KEY]]["required"] = []
                            schema["properties"][row[KEY]]["properties"] = {}
                            current_subschema_idx = i-1
                            current_row_type = "subschema"
                    # TO DO:
                    # 1. Implement max and min keywords for types: number, integer, string (character)
                    if not row[ALLOWED_VAL] == "":
                        maxmin_mode = False
                        if "max:" in row[ALLOWED_VAL].replace(" ", "").lower():
                            maxmin_mode = True
                            maxmin_keyword = row[ALLOWED_VAL].replace(
                                " ", "").lower()
                            maxmin_keyword = maxmin_keyword.split(";")
                            indx = index_containing_substring(
                                maxmin_keyword, "max:")
                            maxmin_keyword = maxmin_keyword[indx]
                            maxmin_keyword = maxmin_keyword.split(":")
                            maxmin_keyword = maxmin_keyword[1]
                            if row[TYPE] == "string":
                                schema["properties"][row[KEY]
                                                     ]["maxLength"] = int(maxmin_keyword)
                            if row[TYPE] == "number":
                                schema["properties"][row[KEY]
                                                     ]["maximum"] = float(maxmin_keyword)
                            if row[TYPE] == "integer":
                                schema["properties"][row[KEY]
                                                     ]["maximum"] = int(maxmin_keyword)
                        if "min:" in row[ALLOWED_VAL].replace(" ", "").lower():
                            maxmin_mode = True
                            maxmin_keyword = row[ALLOWED_VAL].replace(
                                " ", "").lower()
                            maxmin_keyword = maxmin_keyword.split(";")
                            indx = index_containing_substring(
                                maxmin_keyword, "min:")
                            maxmin_keyword = maxmin_keyword[indx]
                            maxmin_keyword = maxmin_keyword.split(":")
                            maxmin_keyword = maxmin_keyword[1]
                            if row[TYPE] == "string":
                                schema["properties"][row[KEY]
                                                     ]["minLength"] = int(maxmin_keyword)
                            if row[TYPE] == "number":
                                schema["properties"][row[KEY]
                                                     ]["minimum"] = float(maxmin_keyword)
                            if row[TYPE] == "integer":
                                schema["properties"][row[KEY]
                                                     ]["minimum"] = int(maxmin_keyword)
                        if not maxmin_mode:
                            if row[TYPE] == "string":
                                enum_values = row[ALLOWED_VAL].split(";")
                                enum_values = [val.strip()
                                               for val in enum_values]
                                schema["properties"][row[KEY]
                                                     ]["enum"] = enum_values
                            if row[TYPE] == "number":
                                enum_values = row[ALLOWED_VAL].split(";")
                                enum_values = [float(val.strip())
                                               for val in enum_values]
                                schema["properties"][row[KEY]
                                                     ]["enum"] = enum_values
                            if row[TYPE] == "integer":
                                enum_values = row[ALLOWED_VAL].split(";")
                                enum_values = [int(val.strip())
                                               for val in enum_values]
                                schema["properties"][row[KEY]
                                                     ]["enum"] = enum_values

                    if (not row[TYPE] == "") and (len(row[OCC].split("-")) == 2):
                        # then this row is an array
                        # then change the type to array
                        schema["properties"][row[KEY]]["type"] = "array"
                        # add type of items
                        schema["properties"][row[KEY]]["items"] = {
                            "type": row[TYPE].lower()}
                        # assign min and max items
                        minmax = row[OCC].split("-")
                        if not minmax[0] == "0":
                            schema["properties"][row[KEY]
                                                 ]["minItems"] = int(minmax[0])
                        if not minmax[1] == "n":
                            schema["properties"][row[KEY]
                                                 ]["maxItems"] = int(minmax[1])

                    i += 1
            print(">>> finished converting {}.md".format(filename))

            # now make sure that there is no "required" keyword with the value of empty array
            schema = delete_empty_array(schema)

            # now create the json file
            json_file = open('{}-json-schema.json'.format(filename), 'w')
            json_file.write(json.dumps(schema, sort_keys=False, indent=4))
            json_file.close()

            # now create the description list file
            # separate the schema into main schema, sub schemas, and array schemas
            main_schema = deepcopy(schema)
            sub_schemas = []
            array_schemas = []
            for key, value in schema["properties"].items():
                if value["type"] == "object":
                    sub_schemas.append(value)
                    del main_schema["properties"][key]
                if value["type"] == "array" and value["items"]["type"] == "object":
                    array_schemas.append(value)
                    del main_schema["properties"][key]

            description_list = "<h1><strong>{}</strong></h1>\n".format(
                main_schema["title"])
            description_list += "<dl>\n"
            # loop through first the main schema
            for key, value in main_schema["properties"].items():
                description_list += "<dt>{}</dt>\n".format(value["title"])
                description_list += "<dd>{}</dd>\n".format(
                    value["description"])
            # loop through subschemas
            for subschema in sub_schemas:
                description_list += '<dt style="background-color: #ffffff; border: 0px; height: 10px;"></dt>\n'
                description_list += '<dt style="background-color: #ffffff; border: 0px;"><a style="color: #000000;"><strong>{}</strong></a></dt>\n'.format(
                    subschema["title"])
                for key, value in subschema["properties"].items():
                    description_list += "<dt>{}</dt>\n".format(value["title"])
                    description_list += "<dd>{}</dd>\n".format(
                        value["description"])
            description_list += "</dl>"
            #print(json.dumps(schema, sort_keys=False, indent=4))
            # loop through array subschemas
            for arr_subschema in array_schemas:
                description_list += '\n<div style="background-color: #ffffff; border: 0px;"><a style="color:#000000;"><strong>{}</strong></a></div>\n'.format(
                    arr_subschema["title"])
                description_list += '<div>\n'
                description_list += '<table style="border-collapse: collapse;" border="1">\n'
                description_list += '<tbody>\n'
                description_list += '<tr>\n'
                description_list += '<td style="text-align: left;"><strong>No.</strong></td>\n'
                for key, value in arr_subschema["items"]["properties"].items():
                    description_list += '<td style="text-align: center;"><strong>{}</strong></td>\n'.format(
                        value["title"])
                description_list += '</tr>\n'

                description_list += '<tr>\n'
                description_list += '<td style="text-align: left;">1</td>\n'
                for key, value in arr_subschema["items"]["properties"].items():
                    description_list += '<td style="text-align: center;">{}</td>\n'.format(
                        value["description"])

                description_list += '</tr>\n'
                description_list += '</tbody>\n'
                description_list += '</table>\n'
                description_list += '</div>'

            # print(description_list)

            # create the .tpl file for this
            tpl_file = open(
                "{}-elab-descriptionlist.tpl".format(filename), 'w')
            tpl_file.write(description_list)
            tpl_file.close()


if __name__ == "__main__":
    main()
