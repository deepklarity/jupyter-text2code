import setuptools       #to allow developer to easily build and distribute Python Packages
import os               #to enable interaction between the user and the operating system
from glob import glob   #to retieve pathnames / files matching a specified pattern


def get_serverextension_files():
    data_files = []
    for f in glob('mopp/mopp_serverextension/**', recursive=True):
        if os.path.isfile(f):
            relative_common_path = "/".join(f.split("/")[:-1])
            data_files.append((os.path.join("share/jupyter/nbextensions/", relative_common_path), 
                [f]))
    return data_files

data_files = [
    ('share/jupyter/nbextensions/mopp', [
        "mopp/__init__.py",
        "mopp/mopp.yaml",
        "mopp/main.js",
        "mopp/mopp.css",
        "mopp/mopp_lib.py"]),
    # ('share/jupyter/nbextensions/mopp/mopp_serverextension', [f for f in glob('mopp/mopp_serverextension/*', recursive=True) if os.path.isfile(f)]),
    ('etc/jupyter/jupyter_notebook_config.d', ['mopp/etc/mopp-serverextension.json']),
    ('etc/jupyter/nbconfig/tree.d', ['mopp/etc/mopp-nbextension.json'])
]

data_files.extend(get_serverextension_files())

setuptools.setup(
    name="mopp",
    version='0.0.1',
    url="",
    author="Deepak Rawat and Kartik Godawat",
    license="BSD 3-Clause",
    description="Jupyter server extension to assist with data science EDA",
    packages=setuptools.find_packages(),
    install_requires=['jupyter', 'jupyter_nbextensions_configurator', 'faiss', 'pandas', 'spacy', 'tensorflow', 'tensorflow_hub', 'absl-py', 'plotly', 'matplotlib'],
    python_requires='>=3.5',
    classifiers=[
        'Framework :: Jupyter',
    ],
    data_files=data_files,
    include_package_data=True,
    zip_safe=False
)
