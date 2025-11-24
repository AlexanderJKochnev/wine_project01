в шапке файла добавить для совместимости с python >3.11
.venv/lib/python3.12/site-packages/pymorphy2/units/base.py

# Совместимость с Python 3.11+
if not hasattr(inspect, 'getargspec'):
    def getargspec(func):
        spec = inspect.getfullargspec(func)
        return spec.args, spec.varargs, spec.varkw, spec.defaults
    inspect.getargspec = getargspec

