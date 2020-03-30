{
  "description" : "description of the dataset",
  "instances_number" : 3,
  "attributes_number" : 5,
  "attributes" : [
    {
      "name" : "instancia",
      "type" : "integer",
      "minimum" : 0
    },
    {
      "name" : "pronostico",
      "type" : "enum",
      "classes" : [ "sunny", "overcast", "rainy" ]
    },
    {
      "name" : "temperatura",
      "type" : "number"
    },
    {
      "name" : "humedad",
      "type" : "number"
    },
    {
      "name" : "viento",
      "type" : "boolean"
    },
    {
      "name" : "jugar",
      "type" : "enum",
      "classes" : [ "yes", "no" ]
    }
  ],
  "target" : "jugar",
  "index" : "instancia",
  "missed" : "?",
  "path" : "./data.csv"
}
