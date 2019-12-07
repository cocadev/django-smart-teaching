import requests
import imaplib
import string
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from zxcvbn import zxcvbn

def _request(method, url, session=None, **kwargs):
    headers = kwargs.get("headers") or dict()
    headers.update(requests.utils.default_headers())
    headers["User-Agent"] = "AppleWebKit/537.36 (KHTML, like Gecko) " \
    						#"Mozilla/5.0 (X11; Linux x86_64) " \
                            
                            #"Chrome/56.0.2924.87 Safari/537.36"
    kwargs["headers"] = headers
    if session:
        return session.request(method, url, **kwargs)
    else:
        return requests.request(method, url, **kwargs)

def _get(url, session=None, **kwargs):
    return _request('get', url, session=session, **kwargs)

def _post(url, session=None, **kwargs):
    return _request('post', url, session=session, **kwargs)

def _check_google(username, email, pw):
    with requests.Session() as session:
        r = _get("https://accounts.google.com/ServiceLogin", session=session)
        soup = BeautifulSoup(r.text, "html.parser")
        hidden_inputs = soup.find_all("input", type="hidden")
        data = {}
        for i in hidden_inputs:
            data.update({i.get('name', ''): i.get('value', '')})
        data.update({'checkConnection': 'youtube'})
        data.update({'Email': email})
        data.update({'Passwd': pw})
        r = _post("https://accounts.google.com/signin/challenge/sl/password",
                  data=data, session=session)

        i = imaplib.IMAP4_SSL('imap.gmail.com')
        try:
            i.login(email, pw)
            var =  True
        except:
            var = False
         
        return False

def _check_twitter(username, email, pw):
    with requests.Session() as session:
        r = _get("https://mobile.twitter.com/login", session=session)
        tk = session.cookies.get("_mb_tk")
        if not tk or r.status_code != 200:
            r = _get("https://mobile.twitter.com/i/nojs_router?path=%2Flogin", session=session)
            r = _get("https://mobile.twitter.com/login", session=session)
            tk = session.cookies.get("_mb_tk")
        if not tk or r.status_code != 200:
            return False
        r = _post("https://mobile.twitter.com/sessions", data={
            "authenticity_token": tk,
            "session[username_or_email]": username,
            "session[password]": pw,
            "remember_me": 0,
            "wfa": 1,
            "redirect_after_login": "/home"
        }, session=session)
        url = urlparse(r.url)
        return url.path != "/login/error"

def _check_github(username, email, pw):
    with requests.Session() as session:
        r = _get("https://github.com/login", session=session)
        soup = BeautifulSoup(r.text, "html.parser")
        i = soup.select_one("input[name='authenticity_token']")
        token = i["value"]
        r = _post("https://github.com/session", session=session, data={
            "utf8": "✓",
            "commit": "Sign in",
            "authenticity_token": token,
            "login": username,
            "password": pw,
        })
        url = urlparse(r.url)
        return url.path != "/session" and url.path != "/login"

def _check_fb(username, email, pw):
    with requests.Session() as session:
        r = _get("https://www.facebook.com", session=session)
        if r.status_code != 200:
            return False
        r = _post("https://www.facebook.com/login.php?login_attempt=1&lwv=100", data={
            "email": email,
            "pass": pw,
            "legacy_return": 0,
            "timezone": 480,
        }, session=session)
        url = urlparse(r.url)
        return url.path != "/login.php"

def _check_hn(username, email, pw):
    r = _post("https://news.ycombinator.com", data={
        "goto": "news",
        "acct": username,
        "pw": pw
    }, allow_redirects=False)
    return "Bad login" not in r.text

checks = {
    "Twitter": _check_twitter,
    "Facebook": _check_fb,
    "GitHub": _check_github,
    "Hacker News": _check_hn,
    "Google": _check_google
}

def check_pass(pw, email, username):
	errors = list()
	if len(pw) < 8:
		errors.append("Your password must be at least 8 characters long")
	if pw.lower() in (email.lower(), username.lower()):
			errors.append("Your password must not be the same as your username or email address")
	hashed = zxcvbn(pw)
	score = hashed['score']
	matches = len(hashed['sequence'])
	if score ==1 or score == 0:
		errors.append('Very weak password, ' + str(matches)+ ' matches found.')
		errors.extend(hashed['feedback']['suggestions'])    
	elif score ==2:
		errors.append('Weak password, ' + str(matches)+ ' matches found.')
	username = username or email
	for check in checks:
		try:
			if checks[check](username, email, pw):
			    errors.append("Your password must not be the same as your {} password".format(check))
		except:
			pass
	return errors

