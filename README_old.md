# WSGISession

WSGISession provides an easy way to deal with sessions in any WSGI
compilant application. This middleware is useful always you want to
store user sessions of a user, understanding that this user will store
the session id in a cookie. It's up to you how to save and retrieve
the session object.

WSGISession has a pair of objects to use: `SessionMiddleware` and `Session`.
This objects should work on any WSGI compilant application; I have tested
on a plain WSGI application and on a Bottle application.

## How install WSGISession

Installing is easy, as the package is on PyPi. You can either

* Download wsgisession.py into your project root
* Use python tools to install from Pypi (pip, easy_install)

```bash
$ pip install wsgisession
$ easy_install wsgisession
```

## How to use SessionMiddleware

`SessionMiddleware` is a middleware, wrapping your application.
An instance of the `SessionMiddleware` object is a WSGI application
that behaves like a WSGI callable. Once the WSGI server calls a
`SessionMiddleware` instance, the callable method passes the call to the
wrapped WSGI callable, appending a `Session` object that corresponds to the
session id stored on a cookie. When calling the `start_response` method,
it also saves the session object and stores the session id in the
cookie. The work of loading and retrieving the session based on the id is
provided by a factory that must be written by you. Here is a simple example
where sessions are simply stored in a global dictionary (but this can also be
a local or remote database either):

```python
import uuid
from wsgiref.simple_server import make_server
from wsgisession import SessionMiddleware
from wsgisession import Session


sessions = {}


class ExampleFactory(object):

    def load(self, id):
        session = Session()
        if id in sessions:
            session.id = id
            session.data = sessions[id]
        else:
            pass

        return session

    def save(self, session):
        print(sessions)
        if not session.id:
            session.id = uuid.uuid4().hex

        sessions[session.id] = session.data
        return session.id


def wrapped_app(environ, start_response):
    session = environ.get('wsgisession')
    # google chrome sends 2 requests ...
    if environ['PATH_INFO'] != '/favicon.ico':
        session['counter'] = session.get('counter', 0) + 1

    start_response('200 OK', [('Content-Type', 'text/html')])
    return ['Visited {} times\n'.format(session['counter']).encode()]


factory = ExampleFactory()
app = SessionMiddleware(wrapped_app, factory)

if __name__ == '__main__':
    httpd = make_server('localhost', 8080, app)
    print("Listening on http://localhost:8080")

    httpd.serve_forever()
```

## How to use Session

`Session` is a convenience object, that stores data and the session id.
When created, `session.data` and `session.id` are initialized to `{}`
and `None` respectively. Your factory object is the responsible to
fill those fields.

This object has also a convenience methods for easy access to the data,
using the form `session[key]`, and also a method `session.get()` with a
default option.

## How to implement a SessionFactory

The `SessionFactory` class is the responsible to load and store the
session data wherever it goes (it's up to you). This class must
implement only two methods (you can add more if you need):

* load(id): loads the id and returns a Session object.
* save(session): saves the session and returns the id to load later

The session id goes "as is" to the cookie, so it's up to you to
protect them if they are sensible enough.

## Using SimpleSessionMiddleware

The SimpleSessionMiddleware offers a similar API for storing sessions.
But instead of using a factory class, it uses a more Pythonic approach
and merges Factory and Session to one class. The complexity is hidden
by using the `SessionManager` class.
If you read the code, you'll see that `SimpleSession` actually added the two
methods `load` and `save` from the class `Factory`. To use that session class
you need to use a `SessionManager` which implements only 3 methods. All of those
are magic methods. As an example see `DictBasedSessionManager` which keeps
all session information in a dictionary residing in memory as long as your
application is a live. It is easy to create session based classes that save
the information in MongoDB, Redis or any other database (SQL or NoSQL).
Here is an example application using the new `SimpleSessionMiddleware`:

```
from wsgiref.simple_server import make_server
from wsgisession import SimpleSessionMiddleware


def wrapped_app(environ, start_response):
    session = environ.get('wsgisession')
    # google chrome sends 2 requests ...
    if environ['PATH_INFO'] != '/favicon.ico':
        session['counter'] = session.get('counter', 0) + 1

    start_response('200 OK', [('Content-Type', 'text/html')])
    return ['Visited {} times\n'.format(session['counter']).encode()]


# this will use the default session manager
app = SimpleSessionMiddleware(wrapped_app)


if __name__ == '__main__':
    httpd = make_server('localhost', 8080, app)
    print("Listening on http://localhost:8080")
    httpd.serve_forever()
```

Assuming you have implemented a session manager to save session information
in Redis:

```
app = SimpleSessionMiddleware(wrapped_app, RedisSessionManager)
```
