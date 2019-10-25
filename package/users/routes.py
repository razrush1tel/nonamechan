import os
from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from package import db, bcrypt
from package.models import User, Post
from package.users.forms import (LogInForm, RegistrationForm, SearchForm,
                        UpdateAccountForm, RequestResetForm, ResetPasswordForm)
from package.users.utils import save_picture, send_reset_email


users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    searchform = SearchForm()
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        print('validated')
        if form.email.data == os.environ.get('EMAIL_USER'):
            role = 2
        else:
            role = 0
        status = 'active'
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, role=role, status=status)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('users.login'))
    else:
        print('not validated')
        print(form.errors)
    return render_template('register.html', title='Register', form=form, searchform=searchform)


@users.route('/login', methods=['GET', 'POST'])
def login():
    searchform = SearchForm()
    form = LogInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(url_for(next_page)) if next_page else redirect(url_for('main.home'))
    return render_template('login.html', title='Log In', form=form, searchform=searchform)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account/<username>", methods=['GET', 'POST'])
@login_required
def account(username):
    searchform = SearchForm()
    form = UpdateAccountForm()
    user = User.query.filter_by(username=username).first()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file, _, _ = save_picture(form.picture.data, (250, 250), 'profile_pics')
            user.profile_pic = picture_file
            db.session.commit()
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('users.account', username=username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + user.profile_pic)
    print(image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form, searchform=searchform, name=username, user=user)


@login_required
@users.route('/ban/<username>', methods=['POST'])
def ban(username):
    user = User.query.filter_by(username=username).first()
    user.status = 'banned'
    db.session.commit()
    return redirect(url_for('users.account', username=username))


@login_required
@users.route('/unban/<username>', methods=['POST'])
def unban(username):
    user = User.query.filter_by(username=username).first()
    user.status = 'active'
    db.session.commit()
    return redirect(url_for('users.account', username=username))


@login_required
@users.route('/promote/<username>', methods=['POST'])
def promote(username):
    user = User.query.filter_by(username=username).first()
    user.role += 1
    db.session.commit()
    return redirect(url_for('users.account', username=username))


@login_required
@users.route('/disapprove/<username>', methods=['POST'])
def disapprove(username):
    user = User.query.filter_by(username=username).first()
    user.role -= 1
    db.session.commit()
    return redirect(url_for('users.account', username=username))


@users.route('/author/<string:username>', methods=['GET', 'POST'])
def author(username):
    searchform = SearchForm()
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.order_by(Post.date_posted.desc())\
        .order_by(Post.date_posted.desc())\
        .paginate(per_page=24, page=page)
    return render_template('author_posts.html', posts=posts, user=user, searchform=searchform)

@users.route('/favorites/<string:username>', methods=['GET', 'POST'])
def favorites(username):
    searchform = SearchForm()
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    favorite_set = set([i.id for i in user.favorites])
    print(favorite_set)
    posts = Post.query.filter(Post.id.in_(favorite_set)).order_by(Post.date_posted.desc()).paginate(per_page=24, page=page)
    return render_template('favorites.html', posts=posts, user=user, searchform=searchform)


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    searchform = SearchForm()
    if current_user.is_authenticated:
        return redirect_url(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form, searchform=searchform)


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    searchform = SearchForm()
    if current_user.is_authenticated:
        return redirect_url(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token token', 'warning')
        return redirect(url_for('users.utils.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form, searchform=searchform)
