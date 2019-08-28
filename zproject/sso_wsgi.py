from zproject.wsgi import application

old_request_class = application.request_class

def request_class(environ):
    request = old_request_class(environ)
    request.urlconf = "zproject.sso_urls"
    return request

application.request_class = request_class
