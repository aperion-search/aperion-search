from pathlib import Path
from jinja2 import Environment, TemplateSyntaxError

path = Path(r'aperion/templates/simple/results.html')
s = path.read_text(encoding='utf-8')
try:
    Environment().parse(s)
    print('PARSE_OK')
except TemplateSyntaxError as e:
    print('LINE', e.lineno)
    print('MESSAGE', e.message)
    if e.source:
        print('SOURCE')
        print(e.source)
