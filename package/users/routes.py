import os
from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from package import db, bcrypt
from package.models import User, Post, Atable_subs, Atable_notif, Notification, Comment
from package.users.forms import (LogInForm, RegistrationForm, SearchForm, SubscribeForm,
                        UpdateAccountForm, RequestResetForm, ResetPasswordForm)
from package.posts.forms import CommentForm
from package.users.utils import save_picture, send_reset_email
from package.main.routes import extract_tags


users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    searchform = SearchForm()
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    registerform = RegistrationForm()
    if registerform.validate_on_submit():
        print('validated')
        if registerform.email.data == os.environ.get('EMAIL_USER'):
            role = 2
        else:
            role = 0
        status = 'active'
        hashed_password = bcrypt.generate_password_hash(registerform.password.data).decode('utf-8')
        user = User(username=registerform.username.data, email=registerform.email.data, password=hashed_password, role=role, status=status)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('users.login'))
    else:
        print('not validated')
        print(registerform.errors)
    return render_template('register.html', title='Register', registerform=registerform, searchform=searchform)


@users.route('/login', methods=['GET', 'POST'])
def login():
    searchform = SearchForm()
    loginform = LogInForm()
    if loginform.validate_on_submit():
        user = User.query.filter_by(email=loginform.email.data).first()
        if user and bcrypt.check_password_hash(user.password, loginform.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(url_for(next_page)) if next_page else redirect(url_for('main.home'))
    return render_template('login.html', title='Log In', loginform=loginform, searchform=searchform)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account/<username>", methods=['GET', 'POST'])
@login_required
def account(username):
    subs_flag = 0
    searchform = SearchForm()
    updateform = UpdateAccountForm()
    commentform = CommentForm()
    user = User.query.filter_by(username=username).first()

    if user is None:
        return render_template('no_user.html', title='Account', searchform=searchform)
    else:
        sub_count = len(Atable_subs.query.filter_by(cmaker_id=user.id).all())
        if Atable_subs.query.filter_by(cmaker_id=user.id, sub_id=current_user.id).first() is not None:
            subs_flag = 1
        elif user.id == current_user.id:
            subs_flag = 2
        if updateform.validate_on_submit():
            if updateform.picture.data:
                picture_file, _, _ = save_picture(updateform.picture.data, (250, 250), 'profile_pics')
                user.profile_pic = picture_file
                db.session.commit()
            comments = Comment.query.filter_by(user_id=username)
            for i in comments:
                i.user_id = updateform.username.data
            current_user.username = updateform.username.data
            current_user.email = updateform.email.data
            db.session.commit()
            flash('Your account has been updated', 'success')
            return redirect(url_for('users.account', username=updateform.username.data))
        elif request.method == 'GET':
            updateform.username.data = current_user.username
            updateform.email.data = current_user.email
        if commentform.validate_on_submit():
            comment = Comment(author=current_user.username, content=commentform.content.data, user_id=username)
            user.comment_list.append(comment)
            db.session.commit()
            return redirect(url_for('users.account', username=username))
        image_file = url_for('static', filename='profile_pics/' + user.profile_pic)
        return render_template('account.html', title='Account', image_file=image_file,
                            updateform=updateform, searchform=searchform, name=username, user=user,
                            subscribed=subs_flag, sub_count=sub_count, commentform=commentform)


@users.route("/notifications/<username>", methods=['GET', 'POST'])
@login_required
def notifications(username):
    searchform = SearchForm()
    received = Atable_notif.query.filter_by(recip_id=current_user.id)
    notif_set = set([elem.notif_id for elem in received])
    notif_list = Notification.query.filter(Notification.id.in_(notif_set)).order_by(Notification.date.desc())
    for del_notif in received:
        db.session.delete(del_notif)
    db.session.commit()
    return render_template('notifications.html', title='Notification', notif_list=notif_list, searchform=searchform)


@users.route("/followers/<username>", methods=['GET', 'POST'])
@login_required
def followers(username):
    searchform = SearchForm()
    user = User.query.filter_by(username=username).first()
    followers_id = [i.sub_id for i in Atable_subs.query.filter_by(cmaker_id=user.id)]
    followers = []
    for i in followers_id:
        followers.append(User.query.get(i))
    return render_template('followers.html', title='Followers', followers=followers, searchform=searchform)


@login_required
@users.route('/follow/<username>', methods=['POST'])
def follow(username):
    user = User.query.filter_by(username=username).first()
    new_record = Atable_subs(cmaker_id=user.id, sub_id=current_user.id)
    db.session.add(new_record)
    db.session.commit()
    return redirect(url_for('users.account', username=username))


@login_required
@users.route('/unfollow/<username>', methods=['POST'])
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    rel = Atable_subs.query.filter_by(cmaker_id=user.id, sub_id=current_user.id).first()
    db.session.delete(rel)
    db.session.commit()
    return redirect(url_for('users.account', username=username))


@login_required
@users.route('/ban/<username>', methods=['POST'])
def ban(username):
    user = User.query.filter_by(username=username).first()
    user.status = 'banned'
    notification = Notification(username=user.username, type='ban', content=" has been banned")
    db.session.add(notification)
    allusers = User.query.all()
    for elem in allusers:
        rel_notif = Atable_notif(notif_id=notification.id, recip_id=elem.id)
        db.session.add(rel_notif)
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
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.date_posted.desc())\
        .order_by(Post.date_posted.desc())\
        .paginate(per_page=24, page=page)
    return render_template('author_posts.html', posts=posts, user=user, searchform=searchform, tag_list=extract_tags(posts.items))

@users.route('/favorites/<string:username>', methods=['GET', 'POST'])
def favorites(username):
    searchform = SearchForm()
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    favorite_set = set([i.fav_id for i in user.fav_list])
    posts = Post.query.filter(Post.id.in_(favorite_set)).order_by(Post.date_posted.desc()).paginate(per_page=24, page=page)
    return render_template('favorites.html', posts=posts, user=user, searchform=searchform, tag_list=extract_tags(posts.items))


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    searchform = SearchForm()
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    requestform = RequestResetForm()
    if requestform.validate_on_submit():
        user = User.query.filter_by(email=requestform.email.data).first()
        send_reset_email(user)
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', requestform=requestform, searchform=searchform)


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    searchform = SearchForm()
    if current_user.is_authenticated:
        return redirect_url(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token token', 'warning')
        return redirect(url_for('users.utils.reset_request'))
    resetform = ResetPasswordForm()
    if resetform.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(resetform.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', resetform=resetform, searchform=searchform)
