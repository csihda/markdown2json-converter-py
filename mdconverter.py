import json
import os
from pathlib import Path
from re import findall
from copy import deepcopy


def main():
    # check if there are markdowns file within the folder
    filelist = list(Path('.').glob('**/*.md'))

    # early exist when no markdowns are found
    if len(filelist) == 0:
        print("No markdown files were found.")
        return

    # read each available markdown and process it
    for file in filelist:
        with open(str(file), 'r') as f:
            # file name without extension
            filename = str(file).replace(".md", "")
            # read the content of the file
            content = f.read()

            markdown_array_rep = json.dumps(content).replace('"', "")
            markdown_array_rep = markdown_array_rep.split(
                '\\n')  # split based on the new lines

            # create initial schema/dict
            updatedSchema = {}
            updatedSchema["$schema"] = "http://json-schema.org/draft-04/schema#"
            updatedSchema["id"] = "some schema id"
            updatedSchema["title"] = "some schema title"
            updatedSchema["description"] = "some schema description"
            updatedSchema["type"] = "object"
            updatedSchema["properties"] = {}

            # regex pattern for getting rid of all repeating
            # characters that are not in alphabet
            regex_pattern = "([a-zA-Z])\\1*"

            # create an array for each line
            markdown_array_trans = []
            for i in markdown_array_rep:
                markdown_sub_array = i.split("|")
                # delete first and last element of markdown_sub_array
                markdown_sub_array = markdown_sub_array[1:len(
                    markdown_sub_array)-1]

                if len(markdown_sub_array) != 0:
                    if(len(findall(regex_pattern, markdown_sub_array[0])) == 0):
                        # do nothing
                        pass
                    else:
                        # trim for excess spaces
                        arr = [x.strip() for x in markdown_sub_array]
                        markdown_array_trans.append(arr)

            # transpose markdown array rep
            # maybe using numpy is easier, but hey, let's make it as close as the JavaScript one
            reshaped_array = []
            try:
                for i in range(0, len(markdown_array_trans[0])):
                    temp_array = []
                    for j in range(0, len(markdown_array_trans)):
                        temp_array.append(markdown_array_trans[j][i])
                    reshaped_array.append(temp_array)
            except Exception as e:
                print(e)

            # pass the loop if reshaped array length is less than 6
            if len(reshaped_array) < 6:
                print("Markdown is not valid. Skipping {}.".format(file))
            else:
                # reshaped array to dict/json
                objectified = {}
                for i in reshaped_array:
                    key = i[0].lower()
                    value = deepcopy(i)
                    value = value[1:]
                    objectified[key] = value
                # print(json.dumps(objectified, sort_keys=True, indent=4))

                # now input this content to the schema
                for i in range(0, len(objectified['key'])):
                    value = {}
                    if objectified["title"][i] != "":
                        value["title"] = objectified["title"][i]
                    if objectified["description"][i] != "":
                        value["description"] = objectified["description"][i]
                    if objectified["type"][i] != "":
                        value["type"] = objectified["type"][i]
                    if objectified["default value"][i] != "":
                        value["default"] = objectified["default value"][i]

                    updatedSchema["properties"][objectified["key"][i]] = value

                # now check the required
                if objectified["required"] != None:
                    required = []
                    for i in range(0, len(objectified["required"])):
                        if objectified["required"][i].lower() == "true":
                            required.append(objectified["key"][i])
                    updatedSchema["required"] = required

                # print("created schema:", json.dumps(updatedSchema, sort_keys=False, indent=4))

                # now create the json file
                json_file = open('{}-json-schema.json'.format(filename), 'w')
                json_file.write(json.dumps(
                    updatedSchema, sort_keys=False, indent=4))

                # now create the description list file
                description_list = "<dl>\n"
                for i in range(0, len(objectified["key"])):
                    description_list += "<dt>{}</dt>\n".format(
                        objectified["title"][i])
                    description_list += "<dd>{}</dd>\n".format(
                        objectified["description"][i])
                description_list += "</dl>"

                # create the .tpl file for this
                tpl_file = open(
                    "{}-elab-descriptionlist.tpl".format(filename), 'w')
                tpl_file.write(description_list)


if __name__ == "__main__":
    main()
