# fup

## A Basic Example

### -1: Prerequisites

Before you begin, you will need to create an AWS credential file. If you have used boto or other similar libraries before, you may already have one.

To verify, make sure that your `~/.aws/credentials` file has at least one profile in it. Profiles look like this:

```
[profilename]
aws_access_key_id = ...
aws_secret_access_key = ...
```

If you do not have one of these, then you will need to [create one](https://docs.aws.amazon.com/cli/latest/userguide/cli-config-files.html).

### 0: Install fup

The best way to install fup while guaranteeing that you have the latest version is to clone from this GitHub repository:

```shell
git clone https://github.com/FitMango/fup2
cd fup2
pipenv install
```

(You will need to install `pipenv` for this to work: `pip3 install -U pipenv`)

### 1. Create your project

fup expects different components of your software to live in predetermined locations in a project directory. You will want to put your API in a directory named `api/`, and your static website should live in a directory named `web/`:

```
project/
    |
    |- api/
    |   |- main.py
    |
    |- web/
        |- index.html
        |- index.js
```

### 2: A basic API

In `api/main.py`, paste the following code:

```python
from flask import Flask

APP = Flask(__name__)

@APP.route("/")
def homepage():
    return "Hi! This API is working."

APP.run(host="0.0.0.0")
```

### 3: A basic webpage

In `web/index.html`, paste the following code:

```html
<html>
    <head>
        <title>My Website</title>
    </head>

    <body>
        <h1>Hello world!</h1>
    </body>
</html>
```

### 4. Deploying your API with fup

In your project directory, initialize fup:

```shell
fup init myproject --components web,api
```

We specify the list of components we want to upload: If you're uploading all three of web, api, and db, you don't need to specify this argument and you can just use `fup init fup-helloworld`.

After the command completes, you can use `fup status` to see what's deployed:

```
fup status myproject --components web,api
```

This will give you the URLs and other information about the deployed app.

### 5. TBC
