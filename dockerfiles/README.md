# About jupyter-text2code

### A proof-of-concept jupyter extension which converts english queries into relevant python code. 

#### Github Repository: https://github.com/deepklarity/jupyter-text2code

### Blog post with more details:
#### [Data analysis made easy: Text2Code for Jupyter notebook](https://towardsdatascience.com/data-analysis-made-easy-text2code-for-jupyter-notebook-5380e89bb493?source=friends_link&sk=2c46fff2c31f7fe59b667350e4596b18)

### Demo Video:
#### [Text2Code for Jupyter notebook](https://www.youtube.com/watch?v=3gZ7_9W-TJs)

# How to Use the Images

### Install docker from:  https://docs.docker.com/engine/install/

### CPU image:

1. Pull the docker image
```
docker pull deepklarity/jupyter-text2code:latest
```
2. Run the Docker image
```
docker run -it -p 8888:8888 deepklarity/jupyter-text2code:latest
```

### GPU image:
1. Pull the docker image
```
docker pull docker pull deepklarity/jupyter-text2code:latest-gpu
```
2. Run the Docker image
```
docker run -it --gpus all -p 8888:8888 deepklarity/jupyter-text2code:latest-gpu
```

### Open Jupyter Notebook: 

#### Once the container is running, you will see a URL with a token in the terminal/console. Open that URL in your browser. 

Example url: ``` http://127.0.0.1:8888/?token=48c6ea28c1cbce210c008f1ef8dab8fa91ad77420922e259 ```

### Usage Instructions:

- You can open the sample ``` notebooks/ctds.ipynb```  notebook for testing
- Click on the `Terminal` Icon which appears on the menu (to activate the extension)
- Type "help" to see a list of currently supported commands in the repo
- Watch [Demo video](https://www.youtube.com/watch?v=3gZ7_9W-TJs) for some examples
