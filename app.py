import pickle, uuid

from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

projects = []

with open('./projects.pickle', 'rb') as handle:
  my_data = pickle.load(handle)
  projects = my_data


def save_data(projects_to_save):
  with open('./projects.pickle', 'wb') as f:
    pickle.dump(projects_to_save, f)


# fields = ["name", "completed", "project_id"]


def filter_list_of_dicts(list_of_dicts, fields):
  filtered_dicts = []
  for dict in list_of_dicts:
    new_dict = dict.copy()
    for key in dict:
      if key not in fields:
        del new_dict[key]
      pass
    filtered_dicts.append(new_dict)
  return filtered_dicts


# filter_list_of_dicts(projects, fields)
# print(f'filtered list is: {filtered_dicts}')


# ez egy endpoint, ha a böngészőben a főoldalt ("/") jeleníti meg. Ez egy HTTP REQUEST GET METHOD:
@app.route("/")
def home():
  return render_template("index.html.j2", name="István")


# ez az endpoint már nem a főoldalt, hanem ha az urlbe azt írom, hogy "/projects" akkor az alábbi return-t jeleníti meg:
@app.route("/projects")
def get_projects():
  try:
    request_data = request.get_json()
    print(f'request_data is {type(request_data)} : {request_data}')
    fields = request_data['fields']
    return jsonify(filter_list_of_dicts(projects, fields))
  except:

    # return jsonify({'projects': projects})
    # ha azt akarom, hogy ezt elérje másik domain-ről egy web alkalmazás, akkor így kell megírni (konkrét elérési út helyett a * bárkit enged hozzáférni):
    return jsonify({'projects': projects}), 200, {
        'Access-Control-Allow-Origin': 'http://127.0.0.1:5500'
    }


# projekt hozzáadása POST methoddal:
@app.route("/project", methods=['POST'])
def create_project():
  new_project_id = uuid.uuid4().hex[:24]
  request_data = request.get_json()

  # generating new tasks (there can be more then one) from request body & random id:
  new_tasks = []
  for task in request_data['tasks']:
    new_task_id = uuid.uuid4().hex[:24]
    new_checklist = []
    # generating new chklist items (there can be more then one) from request body & random id:
    for item in task['checklist']:
      new_checklist_id = uuid.uuid4().hex[:24]
      chklist_item = {
          'name': item['name'],
          'completed': item['completed'],
          'checklist_id': new_checklist_id
      }
      new_checklist.append(chklist_item)

    new_task = {
        'name': task['name'],
        'completed': task['completed'],
        'checklist': new_checklist,
        'task_id': new_task_id
    }
    new_tasks.append(new_task)

  new_project = {
      'name': request_data['name'],
      'tasks': new_tasks,
      'completed': request_data['completed'],
      'creation_date': request_data['creation_date'],
      'project_id': new_project_id
  }
  projects.append(new_project)
  save_data(projects)
  return jsonify({'message':
                  f'project created with id: {new_project_id}'}), 201


# ez pedig már egy változó beírását is lehetővé teszi az url-be, és annak megfelelő a response:
@app.route("/project/<string:proj_id>")
def get_project(proj_id):
  for project in projects:
    if project['project_id'] == proj_id:
      return jsonify(project)
  return jsonify({'message': 'project not found'}), 404


# original end point was searching by name, so first I need to modify to searc by id.
@app.route("/project/<string:proj_id>/tasks")
def get_project_tasks(proj_id):
  for project in projects:
    if project['project_id'] == proj_id:
      try:
        request_data = request.get_json()
        fields = request_data['fields']
        found_project = project['tasks']
        return jsonify(filter_list_of_dicts(found_project, fields))
      except:
        return jsonify({'tasks': project['tasks']})
  return jsonify({'message': 'project not found'}), 404


# task hozzáadása endpoint (POST METHOD):
@app.route("/project/<string:proj_id>/task", methods=['POST'])
def add_task_to_project(proj_id):
  request_data = request.get_json()
  for project in projects:
    if 'project_id' in project and project['project_id'] == proj_id:
      if 'completed' not in request_data or type(
          request_data['completed']) is not bool:
        return jsonify({'message': 'completed must be a boolean'}), 400
      new_task_id = uuid.uuid4().hex[:24]
      new_checklist_id = uuid.uuid4().hex[:24]
      new_checklist = request_data['checklist']
      # I suppose that all requests will have only 1 checklist item as the example, so I can use the first element of the checklist list hardcoded. Otherwise we would need a loop to add all checklist items.
      new_checklist[0]['checklist_id'] = new_checklist_id
      new_task = {
          'name': request_data['name'],
          'completed': request_data['completed'],
          'task_id': new_task_id,
          'checklist': new_checklist
      }
      project['tasks'].append(new_task)
      save_data(projects)
      return jsonify({'message': f'task created with id: {new_task_id}'}), 201
  return jsonify({'message': 'project not found'}), 404


# project completed endpoint:
@app.route("/project/<string:proj_id>/complete", methods=['POST'])
def project_completed(proj_id):
  for project in projects:
    if project['project_id'] == proj_id:
      if project['completed'] == True:
        return jsonify({'message': ''}), 200
      project['completed'] = True
      return jsonify(project)
  return jsonify({'message': 'project not found'}), 404
