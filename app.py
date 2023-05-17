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


# ez egy endpoint, ha a böngészőben a főoldalt ("/") jeleníti meg. Ez egy HTTP REQUEST GET METHOD:
@app.route("/")
def home():
  return render_template("index.html.j2", name="István")


# ez az endpoint már nem a főoldalt, hanem ha az urlbe azt írom, hogy "/projects" akkor az alábbi return-t jeleníti meg:
@app.route("/projects")
def get_projects():
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


@app.route("/project/<string:name>/tasks")
def get_project_tasks(name):
  for project in projects:
    if project['name'] == name:
      return jsonify({'tasks': project['tasks']})
  return jsonify({'message': 'project not found'}), 404


# task hozzáadása endpoint (POST METHOD):
@app.route("/project/<string:name>/task", methods=['POST'])
def add_task_to_project(name):
  request_data = request.get_json()
  for project in projects:
    if 'name' in project and project['name'] == name:
      if 'completed' not in request_data or type(
          request_data['completed']) is not bool:
        return jsonify({'message': 'completed must be a boolean'}), 400
      new_task = {
          'name': request_data['name'],
          'completed': request_data['completed']
      }
      project['tasks'].append(new_task)
      return jsonify(new_task), 201
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
