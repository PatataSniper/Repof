from jsonschema import validate
from jsonschema import Draft7Validator as DraftValidator
import app.utils
import json
import csv
from app.table import Table
import re

class Properties:
    def __init__(self, schema, props, csvdata):
        self.schema = self.getJsonObject(schema)
        self.props = self.getJsonObject(props)
        self.errorFlag = False
        self.errorMessage = []
        self.findErrors(self.schema, self.props, None)
        if (self.checkForErrors()):
            return
        self.data = self.getCSVData(csvdata)
        self.propsAttr = self.props["attributes"]
        self.attrs_schema = self.getAttrSchema()
        self.compareAttrsData()
        if (self.checkForErrors()):
            return

    def getJsonObject(self, path):
        with open(path) as schema_file:
            return json.load(schema_file)

    def getCSVData(self, csvdata):
        with open(csvdata, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            return list(reader)

    def getAttrSchema(self):
        attrs = []
        intPattern = "^(\+|-)?[0-9]+$"
        floatPattern = "^(\+|-)?[0-9]*\.?[0-9]+([Ee](\+|-)?[0-9]*)?$"
        booleanPattern = "^\s*(1|0|T(rue|RUE)|true|F(alse|ALSE)|false)\s*$"

        for attr in self.propsAttr:
            attrs.append({
                "type" : "object",
                "properties" : {
                    attr["name"] : {}
                }
            })
            type = attr["type"]
            if (type == "enum"):
                attrs[-1]["properties"][attr["name"]]["enum"] = attr["classes"]
            else:
                attrs[-1]["properties"][attr["name"]]["type"] = "string"
            if (type != "string"):
                if (type == "pattern"):
                    attrs[-1]["properties"][attr["name"]]["pattern"] = attr["pattern"]
                elif (type == "integer"):
                    attrs[-1]["properties"][attr["name"]]["pattern"] = intPattern
                elif (type == "number"):
                    attrs[-1]["properties"][attr["name"]]["pattern"] = floatPattern
                elif (type == "boolean"):
                    attrs[-1]["properties"][attr["name"]]["pattern"] = booleanPattern
        return attrs

    def compareAttrsData(self):
        error_num_attrs = False
        for instance in self.data:
            if (not error_num_attrs and len(instance) != len(self.attrs_schema)):
                self.errorFlag = True
                self.errorMessage.append("Attributes in properties file don't match the csv data")
                self.attrs_schema = self.defaultSchema()
            for i in range(len(instance)):
                type = self.props["attributes"][i]["type"]
                schema = self.attrs_schema[i]
                json_data = { self.props["attributes"][i]["name"] : instance[i] }
                errorMessage = "'"+instance[i]+"' is not of type "+type+" in attribute '"+self.props["attributes"][i]["name"]+"'"
                if (self.findErrors(schema, json_data, errorMessage) == 0):
                    if (type == "number"):
                        instance[i] = float(instance[i])
                    if (type == "integer"):
                        instance[i] = int(instance[i])
                    if (type == "boolean"):
                        instance[i] = re.search("^\s*(1|T(rue|RUE)|true)\s*$", instance[i]) != None

        attrs = []
        intPattern = "^(\+|-)?[0-9]+$"
        floatPattern = "^(\+|-)?[0-9]*\.?[0-9]+([Ee](\+|-)?[0-9]*)?$"
        booleanPattern = "^\s*(1|0|T(rue|RUE)|true|F(alse|ALSE)|false)\s*$"

        for attr in self.propsAttr:
            attrs.append({
                "type" : "object",
                "properties" : {
                    attr["name"] : {}
                }
            })
            type = attr["type"]
            if (type == "enum"):
                attrs[-1]["properties"][attr["name"]]["enum"] = attr["classes"]
            elif (type == "string"):
                attrs[-1]["properties"][attr["name"]]["type"] = "string"
                if ("maxLength" in attr and attr["maxLength"] != None and attr["maxLength"] != 0):
                    attrs[-1]["properties"][attr["name"]]["maxLength"] = attr["maxLength"]
            if (type == "pattern"):
                attrs[-1]["properties"][attr["name"]]["type"] = "string"
                attrs[-1]["properties"][attr["name"]]["pattern"] = attr["pattern"]
            elif (type == "integer" or type == "number"):
                attrs[-1]["properties"][attr["name"]]["type"] = "integer" if type == "integer" else "number"
                if ("minimum" in attr and attr["minimum"] != None):
                    attrs[-1]["properties"][attr["name"]]["minimum"] = attr["minimum"]
                if ("maximum" in attr and attr["maximum"] != None):
                    attrs[-1]["properties"][attr["name"]]["maximum"] = attr["maximum"]
            elif (type == "boolean"):
                attrs[-1]["properties"][attr["name"]]["type"] = "boolean"

            self.attrs_schema = attrs

    def defaultSchema(self):
        pass

    def getTable(self):
        return Table(self, None, self.data)

    def findErrors(self, schema, json_data, errorMessage):
        v = DraftValidator(schema)
        errors = sorted(v.iter_errors(json_data), key=lambda e: e.path)
        for error in errors:
            self.errorMessage.append(errorMessage if errorMessage != None else error.message)
        return len(errors) != 0

    def printErrors(self):
        for error in self.errorMessage:
            print(error)

    def checkForErrors(self):
        if (len(self.errorMessage) != 0):
            self.errorFlag = True
        return self.errorFlag

#with open("sample.schema") as schema_file:
#    schema = json.load(schema_file)
#    with open("properties.json") as prop_file:
#        properties = json.load(prop_file)
#        validate(instance=properties, schema=schema)
