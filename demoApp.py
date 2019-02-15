import os
from bottle import route, run, template, Bottle
app = Bottle(__name__)


index_html = '''Webserver using Bottle framework!!! </br> By <strong>{{ author }}</strong>.'''


@app.route('/')
def index():
    return template(index_html, author='Chetan Gomase')


@app.route('/name/<name>')
def name(name):
    return template(index_html, author=name)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port, debug=True)
