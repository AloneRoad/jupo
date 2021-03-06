#! coding: utf-8
# pylint: disable-msg=W0311, W0611, E1103, E1101
#@PydevCodeAnalysisIgnore

from flask import redirect, request, session, Response
from functools import wraps
from lib import cache
import api


def login_required(f):
  """
  redirects to the home page if the user has no session
  """
  @wraps(f)
  def wrapper(*args, **kwargs):
    session_id = session.get('session_id')
    user_id = api.get_user_id(session_id)
    if user_id:
      utcoffset = request.cookies.get('utcoffset')
      if utcoffset:
        api.update_utcoffset(user_id, utcoffset)
        
      return f(*args, **kwargs)
    resp = redirect('/')
    back_to = request.args.get('back_to')
    if back_to:
      resp.set_cookie('redirect_to', back_to)
    else:
      resp.set_cookie('redirect_to', request.url)
    return resp
  return wrapper
  
  
def cache_response(f):
  """ Fullpage caching """
  @wraps(f)
  def decorated_function(*args, **kwargs):
    session_id = session.get('session_id')
    user_id = api.get_user_id(session_id)
    if user_id and request.method in ['GET', 'OPTIONS']:
      if request.query_string:
        key = '%s: %s %s?%s' % (user_id,
                                request.method,
                                request.path,
                                request.query_string)
      else:
        key = '%s: %s %s' % (user_id,
                                request.method,
                                request.path)
      
      rv = cache.get(key)
      if not rv:
        rv = f(*args, **kwargs)
        cache.set(key, rv)
      return rv
    elif user_id and request.method == 'POST':
      key = '%s:*' % user_id
      cache.clear(key)
    return f(*args, **kwargs)
  return decorated_function
  



def admin_required(f):
  @login_required
  @wraps(f)
  def wrapper(*args, **kwds):
    pass
    return f(*args, **kwds)

  return wrapper

def guest_or_login_required(f):
  @wraps(f)
  def wrapper(*args, **kwds):
    pass
    return f(*args, **kwds)
  return wrapper
  
  