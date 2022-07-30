import json


with open('data.json') as file:
    x = json.load(file)

y = {}
for i in x:
    y[i['id']] = i


with open('structuredDataById.json', 'w') as fp:
    json.dump(y, fp, indent=4)