from flask import current_app as app, render_template, request, redirect, abort, jsonify, json as json_mod, url_for, session, Blueprint

from CTFd.utils import authed, pages
from CTFd.models import db, Pages

def load(app):
	
	shell = Blueprint('shell', __name__, template_folder='shell-templates')
	app.register_blueprint(shell, url_prefix='/shell')
	page = Pages('shell',""" """ )
	
	shellexists = Pages.query.filter_by(route='shell').first()
        if not shellexists:
                db.session.add(page)
                db.session.commit()

	
	@app.route('/shell', methods=['GET'])
	def shell_view():
		if not authed():
			return redirect(url_form('auth.login', next=request.path))

		return render_template('shell.html',root=request.script_root) 
