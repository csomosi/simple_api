import pickle, json

with open('projects.json', 'r') as orig_file:
  projects_data = orig_file.read()

projects_json = json.loads(projects_data)

print(projects_data)

with open('./projects.pickle', 'wb') as f:
  pickle.dump(projects_json, f)
