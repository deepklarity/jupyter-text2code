import os
from glob import glob

import setuptools

MODE = os.environ.get("JUPYTER_TEXT2CODE_MODE")
INSTALL_LIBS = [
    "numpy",
    "jupyter",
    "jupyter_contrib_nbextensions",
    "pandas",
    "spacy==3.3.1",
    "sentence_transformers",
    "absl-py",
    "plotly",
    "matplotlib",
]

if MODE and MODE.lower() == "cpu":
    INSTALL_LIBS.append("faiss-cpu")
else:
    INSTALL_LIBS.append("faiss-gpu")


def get_serverextension_files():
    data_files = []
    for f in glob(
        "jupyter_text2code/jupyter_text2code_serverextension/**", recursive=True
    ):
        if os.path.isfile(f):
            frags = f.split("/")[:-1]
            frags[0] = "jupyter-text2code"
            relative_common_path = "/".join(frags)
            data_files.append(
                (os.path.join("share/jupyter/nbextensions/", relative_common_path), [f])
            )
    return data_files


data_files = [
    (
        "share/jupyter/nbextensions/jupyter-text2code",
        [
            "jupyter_text2code/__init__.py",
            "jupyter_text2code/jupyter_text2code.yaml",
            "jupyter_text2code/main.js",
            "jupyter_text2code/jupyter_text2code.css",
            "jupyter_text2code/jupyter_text2code_lib.py",
        ],
    ),
    (
        "etc/jupyter/jupyter_notebook_config.d",
        ["jupyter_text2code/etc/jupyter-text2code-extension.json"],
    ),
]

data_files.extend(get_serverextension_files())

setuptools.setup(
    name="jupyter-text2code",
    version="0.0.2",
    url="https://github.com/deepklarity/jupyter-text2code",
    author="Deepak Rawat and Kartik Godawat",
    license="MIT License",
    description="Jupyter server extension to assist with data science EDA",
    packages=setuptools.find_packages(),
    install_requires=INSTALL_LIBS,
    python_requires=">=3.7",
    classifiers=[
        "Framework :: Jupyter",
    ],
    data_files=data_files,
    include_package_data=True,
    zip_safe=False,
)
