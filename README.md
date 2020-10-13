# assett_flask

## Other usefull Ubuntu tools
`sudo apt install build-essential`   

## Use Python3 to make venv and install Flask:
`git clone this`  
`cd this`   
`mkdir venv`   
`python3 -m venv venv`  
`. venv/bin/activate`  
`pip3 install wheel`  
`pip3 install Flask flask_pymongo requests-toolbelt`  
```
  Failed building wheel for MarkupSafe
  Running setup.py clean for MarkupSafe
Failed to build MarkupSafe
Installing collected packages: itsdangerous, Werkzeug, click, MarkupSafe, Jinja2, Flask
  Running setup.py install for MarkupSafe ... done
Successfully installed Flask-1.1.1 Jinja2-2.11.1 MarkupSafe-1.1.1 Werkzeug-1.0.0 click-7.0 itsdangerous-1.1.0
```
#### To exit venv
`deactivate`

## Basic working example with Flask is run to be seen externally by
```
$ export FLASK_APP=flaskr
$ export FLASK_ENV=development
$ flask init-db
$ flask run
```

## Useful examples
#### Authentication: https://github.com/pallets/flask/tree/master/examples/tutorial/flaskr
