import logging
import os
import re
import time
import urllib
from threading import Thread
import pika
import json
from Queue import Queue

from flask import current_app as app, render_template, request, redirect, abort, jsonify, json as json_mod, url_for, session, Blueprint

from itsdangerous import TimedSerializer, BadTimeSignature, Signer, BadSignature
from passlib.hash import bcrypt_sha256

from CTFd.utils import sha512, is_safe_url, authed, can_send_mail, sendmail, can_register, get_config, verify_email
from CTFd.models import db, Teams, Pages
from CTFd.plugins import register_plugin_assets_directory
import CTFd.auth
import CTFd.views
from CTFd import utils	

def load(app):
#    register_plugin_assets_directory(app, base_path='/plugins/ctfd-shell-plugin/assets/') 
    app.db.create_all()

    shellexists = Pages.query.filter_by(route='shell').first()
    if not shellexists:
        title = 'Shell'
        route = 'shell'
        html = """<style>
#shell-container {
  width: calc(100vw - 20px);
  padding: 0 0 0 0;
}

#shell-help {
  text-align: center;
  height:75px;
  margin: 0 0 0 0;
  border-radius: 5px;
}

#shell {
  height: calc(100vh - 200px);
  width: 100%;
}
</style>

<div id="shell-container" class="container shell-container">
  <div id="shell-help" class="alert alert-info alert-dismissable">
    <a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>
    <p>Use the username and password you registered with to log in.</p>
    <p>You may also log in over ssh on port 2222</p>
  </div>
  <div class>
    <iframe id="shell" src="https://192.168.1.1/shell/" id="gadget0" name="gadget0" frameborder="1"></iframe>
  </div>
</div>
        """

        page = Pages(title, route, html, draft=False, auth_required=True)
        db.session.add(page)
        db.session.commit()

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='shell_queue', durable=True)

    def new_register():
        logger = logging.getLogger('regs')
        if not utils.can_register():
            return redirect(url_for('auth.login'))
        if request.method == 'POST':
            errors = []
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']

            name_len = len(name) == 0
            names = Teams.query.add_columns('name', 'id').filter_by(name=name).first()
            emails = Teams.query.add_columns('email', 'id').filter_by(email=email).first()
            pass_short = len(password) == 0
            pass_long = len(password) > 128
            valid_email = utils.check_email_format(request.form['email'])
            team_name_email_check = utils.check_email_format(name)

            if not valid_email:
                errors.append("Please enter a valid email address")
            if names:
                errors.append('That team name is already taken')
            if team_name_email_check is True:
                errors.append('Your team name cannot be an email address')
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


                    message = json.dumps(["add", name, password])

                    channel.basic_publish(exchange='',
                          routing_key='shell_queue',
                          body=message,
                          properties=pika.BasicProperties(
                             delivery_mode = 2, # make message persistent
                          ))

                    session['username'] = team.name
                    session['id'] = team.id
                    session['admin'] = team.admin
                    session['nonce'] = utils.sha512(os.urandom(10))

                    if utils.can_send_mail() and utils.get_config('verify_emails'):  # Confirming users is enabled and we can send email.
                        logger = logging.getLogger('regs')
                        logger.warn("[{date}] {ip} - {username} registered (UNCONFIRMED) with {email}".format(
                            date=time.strftime("%m/%d/%Y %X"),
                            ip=utils.get_ip(),
                            username=request.form['name'].encode('utf-8'),
                            email=request.form['email'].encode('utf-8')
                        ))
                        utils.verify_email(team.email)
                        db.session.close()
                        return redirect(url_for('auth.confirm_user'))
                    else:  # Don't care about confirming users
                        if utils.can_send_mail():  # We want to notify the user that they have registered.
                            utils.sendmail(request.form['email'], "You've successfully registered for {}".format(utils.get_config('ctf_name')))

            logger.warn("[{date}] {ip} - {username} registered with {email}".format(
                date=time.strftime("%m/%d/%Y %X"),
                ip=utils.get_ip(),
                username=request.form['name'].encode('utf-8'),
                email=request.form['email'].encode('utf-8')
            ))
            db.session.close()
            return redirect(url_for('challenges.challenges_view'))
        else:
            return render_template('register.html')   
     
    def new_profile(data=None):
        logger = logging.getLogger('logins')

        if data is not None:
            try:
                s = TimedSerializer(app.config['SECRET_KEY'])
                name = s.loads(utils.base64decode(data, urldecode=True), max_age=1800)
            except BadTimeSignature:
                return render_template('reset_password.html', errors=['Your link has expired'])
            except (BadSignature, TypeError, base64.binascii.Error):
                return render_template('reset_password.html', errors=['Your reset token is invalid'])

            if request.method == "GET":
                return render_template('reset_password.html', mode='set')
            if request.method == "POST":
                team = Teams.query.filter_by(name=name).first_or_404()
                team.password = bcrypt_sha256.encrypt(request.form['password'].strip())
                db.session.commit()
                logger.warn("[{date}] {ip} -  successful password reset for {username}".format(
                    date=time.strftime("%m/%d/%Y %X"),
                    ip=utils.get_ip(),
                    username=team.name.encode('utf-8')
                ))

                password = request.form['password'].strip()

                if password:
                        message = json.dumps(["change", name, password])

                        channel.basic_publish(exchange='',
                                            routing_key='shell_queue',
                                            body=message,
                                            properties=pika.BasicProperties(
                                                delivery_mode = 2, # make message persistent
                                            ))
                db.session.close()
                return redirect(url_for('auth.login'))

        if request.method == 'POST':
            email = request.form['email'].strip()
            team = Teams.query.filter_by(email=email).first()

            errors = []

            if utils.can_send_mail() is False:
                return render_template(
                    'reset_password.html',
                    errors=['Email could not be sent due to server misconfiguration']
                )

            if not team:
                return render_template(
                    'reset_password.html',
                    errors=['If that account exists you will receive an email, please check your inbox']
                )

            utils.forgot_password(email, team.name)

            return render_template(
                'reset_password.html',
                errors=['If that account exists you will receive an email, please check your inbox']
            )
        return render_template('reset_password.html')


    def new_reset_pass():
        if utils.authed():
            if request.method == "POST":
                errors = []

                name = request.form.get('name').strip()
                email = request.form.get('email').strip()
                website = request.form.get('website').strip()
                affiliation = request.form.get('affiliation').strip()
                country = request.form.get('country').strip()

                user = Teams.query.filter_by(id=session['id']).first()

                if not utils.get_config('prevent_name_change'):
                    names = Teams.query.filter_by(name=name).first()
                    name_len = len(request.form['name']) == 0

                emails = Teams.query.filter_by(email=email).first()
                valid_email = utils.check_email_format(email)

                if utils.check_email_format(name) is True:
                    errors.append('Team name cannot be an email address')

                if ('password' in request.form.keys() and not len(request.form['password']) == 0) and \
                        (not bcrypt_sha256.verify(request.form.get('confirm').strip(), user.password)):
                    errors.append("Your old password doesn't match what we have.")
                if not valid_email:
                    errors.append("That email doesn't look right")
                if not utils.get_config('prevent_name_change') and names and name != session['username']:
                    errors.append('That team name is already taken')
                if emails and emails.id != session['id']:
                    errors.append('That email has already been used')
                if not utils.get_config('prevent_name_change') and name_len:
                    errors.append('Pick a longer team name')
                if website.strip() and not utils.validate_url(website):
                    errors.append("That doesn't look like a valid URL")

                if len(errors) > 0:
                    return render_template('profile.html', name=name, email=email, website=website,
                                           affiliation=affiliation, country=country, errors=errors)

                else:
                    team = Teams.query.filter_by(id=session['id']).first()
                    if team.name != name:
                        if not utils.get_config('prevent_name_change'):
                            team.name = name
                            session['username'] = team.name
                    if team.email != email.lower():
                        team.email = email.lower()
                        if utils.get_config('verify_emails'):
                            team.verified = False

                    if 'password' in request.form.keys() and not len(request.form['password']) == 0:
                        team.password = bcrypt_sha256.encrypt(request.form.get('password'))
                        message = json.dumps(["change", name, password])

                        channel.basic_publish(exchange='',
                          routing_key='shell_queue',
                          body=message,
                          properties=pika.BasicProperties(
                             delivery_mode = 2, # make message persistent
                          ))

                    team.website = website
                    team.affiliation = affiliation
                    team.country = country
                    db.session.commit()
                    db.session.close()


                    return redirect(url_for('views.profile'))
            else:
                user = Teams.query.filter_by(id=session['id']).first()
                name = user.name
                email = user.email
                website = user.website
                affiliation = user.affiliation
                country = user.country
                prevent_name_change = utils.get_config('prevent_name_change')
                confirm_email = utils.get_config('verify_emails') and not user.verified
                return render_template('profile.html', name=name, email=email, website=website, affiliation=affiliation,
                                       country=country, prevent_name_change=prevent_name_change, confirm_email=confirm_email)
        else:
            return redirect(url_for('auth.login'))


    app.view_functions['auth.register'] = new_register
    app.view_functions['views.profile'] = new_profile
    app.view_functions['auth.reset_password'] = new_reset_pass

