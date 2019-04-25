<p align=center><img align=center src'logo.png' width=200 /></p>
<h3 align=center>fup</h3>
<h6 align=center>Fplease UPload it!</h6>


# Installation

```shell
pip3 install fup
```

# School me in the ways of fup

`fup` is a command-line tool that takes the annoying out of deploying serverless web applications. In the `fup` world, there are three components to a web app: A database, an API, and a web component. (There will someday be more — for example, mobile apps — but that day is not yet here.)

- **Database.** Nicknamed `db`. This accepts data when you have data and has data when you want data.
- **Web.** A static website that can be served hot off the filesystem. This is perhaps the output of a `webpack` or `yarn build`?
- **API.** A Python Flask RESTful app. There is no other kind. So sue me.

Do you need a zero-config, serverless version of three or fewer of the above things? Then fup can help.

# Minimal working example: `API` and `Web`

This example only includes API and web components.

The API has only one endpoint, and the web component has only one page, but you can easily see how to expand these.

First, let's make the API. Create a new directory called `myapp` and inside it, make a new directory called `api`. Inside of `myapp/api`, put the following in `main.py`:

```python
from flask import Flask
from flask_cors import CORS

APP = Flask(__name__)
CORS(APP)


@APP.route("/")
def home():
    return "42"


if __name__ == "__main__":
    APP.run(host="0.0.0.0")
```

Let's add a requirements file at `myapp/api/requirements.txt`:

```
flask
flask-cors
```

Now let's create the web application. Create a directory `myapp/web`, and make a file `index.html`:

```html
<html>
    <head>
        <title>fup demo</title>
    </head>

    <body>
        <h1>Hello world!</h1>
        <p>
            This was uploaded using fup, and the answer to life, the universe, and everything, is <span id="answer">unknown.</span>
        </p>
    </body>
    <script>
        fetch("??").then(res => res.text()).then(text => {
            document.getElementByID("answer").innerHTML = text;
        });
    </script>
</html>
```

Now we have three files: `web/index.html`, `api/requirements.txt`, and `api/main.py`. Let's deploy it TO THE CLOUD

## Deploying to the cloud

First, come up with the name of this application. Here, we'll just call it `fup-helloworld`, but you can have several 'stacks' — for example, a `dev` stack and a `production` stack. Stacks are cheap, so you can have as many as you like!

To begin, install fup:

```shell
pip3 install fup
```

Now cd to the project's root directory. From there, let's init the new app:

```shell
fup init fup-helloworld --components web,api
```

We specify the list of components we want to upload: If you're uploading all three of web, api, and db, you don't need to specify this argument and you can just use `fup init fup-helloworld`.

After the command completes, you can use `fup status` to see what's deployed:

```
fup status fup-helloworld --components web,api
```

This will give you the URLs and other information about the deployed app.

You can now see your deployed app live on the web, with zero configuration. That wasn't so bad, was it?
