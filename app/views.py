import yaml
import os
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from jinja2 import Template

LANGAUGE = "english"

def index(request):
    return render(request, 'app/index.html')

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
    template = open(os.path.join(os.path.dirname(__file__), 'data/01_simple_question_answer.yaml'), "r").read()
    template = yaml.safe_load(template)
    template_header = template["pyscript"]["imports"] 
    tempalte_generator = template["pyscript"]["generator"]

    task = open(os.path.join(os.path.dirname(__file__), 'data/task.yaml'), "r").read()
    task = yaml.safe_load(task)
    task = fill_text(task, language=LANGAUGE)
    task_header = task["pyscript"]["imports"] 
    task_generator = task["pyscript"]["generator"]

    response_html = f"""
    <py-script>
        {template_header}
        {tempalte_generator}
        {task_header}
        {task_generator}
        generate("task-container")
    </py-script>
    """
    print(response_html)
    return HttpResponse(response_html)