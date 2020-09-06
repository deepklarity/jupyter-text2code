import json

from IPython import get_ipython
from IPython.core.magics.namespace import NamespaceMagics

_nms = NamespaceMagics()
_Jupyter = get_ipython()
_nms.shell = _Jupyter.kernel.shell


def dataframes_info():
    values = _nms.who_ls()
    info = {v: (eval(v).columns.tolist()) for v in values if type(eval(v)).__name__ == 'DataFrame'}
    return json.dumps(info)
