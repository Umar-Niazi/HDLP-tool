# templates/__init__.py
from flask import Flask

app = Flask(__name__)

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    if value is None:
        return ""
    return value.strftime(format)

@app.template_filter('truncate')
def truncate_filter(s, length=255, end='...'):
    if len(s) <= length:
        return s
    return s[:length] + end
