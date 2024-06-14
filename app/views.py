import yaml
import os
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from jinja2 import Template

LANGUAGE = "english"
from collections import defaultdict

def load_tasks(tasks_dir):
    tasks = []
    # Load all tasks in the given directory and create list of tuples (title, filename, topic_id)
    for task_file in os.listdir(tasks_dir):
        if task_file.endswith('.yaml'):
            with open(os.path.join(tasks_dir, task_file), 'r') as file:
                task = yaml.safe_load(file)
                tasks.append((task['title'][LANGUAGE], task_file, task['topic_id']))
    return tasks

def structure_tasks(tasks, topics_lookup):
    
    structured_tasks = {}

    for title, filename, topic_id in tasks:
        topic = topics_lookup['topics'][topic_id]
        key_idea_id = topic['key_idea']
        level_id = topic['level']

        level_name = topics_lookup['levels'][level_id][LANGUAGE]
        key_idea_name = topics_lookup['key_ideas'][key_idea_id][LANGUAGE]
        topic_name = topic['title'][LANGUAGE]

        if level_name not in structured_tasks:
            structured_tasks[level_name]={}

        if key_idea_name not in structured_tasks[level_name]:
            structured_tasks[level_name][key_idea_name] = {}
        
        if topic_name not in structured_tasks[level_name][key_idea_name]:
            structured_tasks[level_name][key_idea_name][topic_name] = []
        
        structured_tasks[level_name][key_idea_name][topic_name].append((title, filename))

    return structured_tasks

def index(request):
    # Load all tasks in the given directory
    tasks_dir = os.path.join(os.path.dirname(__file__), 'data/math')
    tasks = load_tasks(tasks_dir)

    # Load topics lookup
    with open(os.path.join(os.path.dirname(__file__), 'data/topics_lookup.yaml'), 'r') as file:
        topics_lookup = yaml.safe_load(file)

    # Structure tasks
    structured_tasks = structure_tasks(tasks, topics_lookup)

    print(structured_tasks)

    # Render index.html and display the tasks in the sidebar
    return render(request, 'app/index.html', {'structured_tasks': structured_tasks})

def fill_text(yaml_file, language):
    # Convert YAML data to a string
    template_str = yaml.dump(yaml_file)

    # Create a Jinja2 template
    template = Template(template_str)

    # Prepare the context with the selected language
    text_data = yaml_file["text"]
    context = {key: value[language] for key, value in text_data.items()}

    # Render the template with the context
    rendered_str = template.render(text=context)

    # Convert the rendered string back to a dictionary
    return yaml.safe_load(rendered_str)

@csrf_exempt
def load_task(request):
    tasks_dir = os.path.join(os.path.dirname(__file__), 'data/math')
    template_dir = os.path.join(os.path.dirname(__file__), 'data/templates')

    if request.method == 'POST':
        task_name = request.POST.get('task_name', '')
    
    # load yaml file by task name
    task_file = os.path.join(tasks_dir, task_name)

    # parse task and load according template 
    task = open(task_file, "r").read()
    task = yaml.safe_load(task)
    task = fill_text(task, language=LANGUAGE)
    template_name = task["template"]+".yaml"
    template = open(os.path.join(template_dir, template_name), "r").read()
    template = yaml.safe_load(template)

    # read pyscript fileds from task and template
    template_header = template["pyscript"]["imports"] 
    tempalte_generator = template["pyscript"]["generator"]
    task_header = task["pyscript"]["imports"] 
    task_globals = task["pyscript"]["globals"]
    task_checker = task["pyscript"]["checker"]
    task_generator = task["pyscript"]["generator"]
    
    # build pyscript tag that handles the task layout and logic
    response_html = f"""
    <py-script>
        {template_header}
        {tempalte_generator}
        {task_header}
        {task_globals}
        {task_checker}
        {task_generator}

        def check(event):
            result = check_answer(event)
            flag = result[0]
            if flag:
                pydom['#result'][0].html = "Correct!" 
                generate('task-container')
            else:
                pydom['#result'][0].html = "Almost! Try again!"

        def refresh(event):
            generate('task-container')
        
        generate('task-container')
    </py-script>
    """
    
    return HttpResponse(response_html)
