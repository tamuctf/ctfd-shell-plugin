import logging
import os
import re
import time
import urllib

from flask import current_app as app, render_template, request, redirect, abort, jsonify, json as json_mod, url_for, session, Blueprint

from itsdangerous import TimedSerializer, BadTimeSignature, Signer, BadSignature
from passlib.hash import bcrypt_sha256

from CTFd.utils import sha512, is_safe_url, authed, can_send_mail, sendmail, can_register, get_config, verify_email
from CTFd.models import db, Teams, Pages

def load(app):
	
	shell = Blueprint('shell', __name__, template_folder='shell-templates')
	app.register_blueprint(shell, url_prefix='/shell')
	page = Pages('shell',""" """ )
	auth = Blueprint('auth', __name__)

	shellexists = Pages.query.filter_by(route='shell').first()
        if not shellexists:
                db.session.add(page)
                db.session.commit()

	
	@app.route('/shell', methods=['GET'])
	def shell_view():
		if not authed():
			return redirect(url_form('auth.login', next=request.path))

		return render_template('shell.html',root=request.script_root) 
	
	@app.route('/register', methods=['POST', 'GET'])
	def register():
	    if not can_register():
		return redirect(url_for('auth.login'))
	    if request.method == 'POST':
		errors = []
		name = request.form['name']
		email = request.form['email']
		password = request.form['password']

		name_len = len(name) < 2  
		names = Teams.query.add_columns('name', 'id').filter_by(name=name).first()
		emails = Teams.query.add_columns('email', 'id').filter_by(email=email).first()
		pass_short = len(password) == 0
		pass_long = len(password) > 128
		valid_email = re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", request.form['email'])

		if not valid_email:
		    errors.append("That email doesn't look right")
		if names:
		    errors.append('That team name is already taken')
		if emails:
		    errors.append('That email has already been used')
		if pass_short:
		    errors.append('Pick a longer password')
		if pass_long:
		    errors.append('Pick a shorter password')
		if name_len:
		    errors.append('Pick a longer team name')

		if len(errors) > 0:
		    return render_template('register.html', errors=errors, name=request.form['name'], email=request.form['email'], password=request.form['password'])
		else:
		    with app.app_context():
			team = Teams(name, email.lower(), password)
			db.session.add(team)
			db.session.commit()
			db.session.flush()
			
			os.system("pwd")
			os.system("./CTFd/plugins/shell-plugin/add-shell-user.sh " + name + " " + password)

			session['username'] = team.name
			session['id'] = team.id
			session['admin'] = team.admin
			session['nonce'] = sha512(os.urandom(10))

			if can_send_mail() and get_config('verify_emails'): # Confirming users is enabled and we can send email.
			    db.session.close()
			    logger = logging.getLogger('regs')

			    logger.warn("[{0}] {1} registered (UNCONFIRMED) with {2}".format(time.strftime("%m/%d/%Y %X"),
											     request.form['name'].encode('utf-8'),
											     request.form['email'].encode('utf-8')))
			    return redirect(url_for('auth.confirm_user'))
			else: # Don't care about confirming users
			    if can_send_mail(): # We want to notify the user that they have registered.
				sendmail(request.form['email'], "You've successfully registered for {}".format(get_config('ctf_name')))

		db.session.close()

		logger = logging.getLogger('regs')
		logger.warn("[{0}] {1} registered with {2}".format(time.strftime("%m/%d/%Y %X"), request.form['name'].encode('utf-8'), request.form['email'].encode('utf-8')))
		return redirect(url_for('challenges.challenges_view'))
	    else:
		return render_template('register.html')

	def reset_password(data=None):
	    if data is not None and request.method == "GET":
		return render_template('reset_password.html', mode='set')
	    if data is not None and request.method == "POST":
		try:
		    s = TimedSerializer(app.config['SECRET_KEY'])
		    name = s.loads(urllib.unquote_plus(data.decode('base64')), max_age=1800)
		except BadTimeSignature:
		    return render_template('reset_password.html', errors=['Your link has expired'])
		except:
		    return render_template('reset_password.html', errors=['Your link appears broken, please try again.'])
		team = Teams.query.filter_by(name=name).first_or_404()
		password = request.form['password'].strip()
		name = team.name
		
		os.system("docker exec shell-server ./change-user-pass.sh" + name + " " + password)
		
		team.password = bcrypt_sha256.encrypt(password)
		db.session.commit()
		db.session.close()
		

		return redirect(url_for('auth.login'))

	    if request.method == 'POST':
		email = request.form['email'].strip()
		team = Teams.query.filter_by(email=email).first()
		if not team:
		    return render_template('reset_password.html', errors=['If that account exists you will receive an email, please check your inbox'])
		s = TimedSerializer(app.config['SECRET_KEY'])
		token = s.dumps(team.name)
		text = """
	Did you initiate a password reset?

	{0}/{1}

	""".format(url_for('auth.reset_password', _external=True), urllib.quote_plus(token.encode('base64')))

		sendmail(email, text)

		return render_template('reset_password.html', errors=['If that account exists you will receive an email, please check your inbox'])
	    return render_template('reset_password.html')


	app.view_functions['auth.reset_password'] = reset_password
	app.view_functions['auth.register'] = register
	
