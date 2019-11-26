import os
from flask import Blueprint, render_template, url_for, redirect, request, abort, current_app
from flask_login import current_user, login_required
from package import db
from package.models import Post, Tag, Atable_tag, Atable_fav, Atable_notif, Atable_subs, Comment, Notification
from package.posts.forms import SearchForm, UploadForm, CommentForm
from package.users.utils import save_picture

posts = Blueprint('posts', __name__)

@posts.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):
    flag = False
    commentform = CommentForm()
    searchform = SearchForm()
    post = Post.query.get_or_404(post_id)
    if commentform.validate_on_submit():
        comment = Comment(author=current_user.username, content=commentform.content.data, post_id=post_id)
        post.comment_list.append(comment)
        db.session.commit()
        return redirect(url_for('posts.post', post_id=post_id))
    if current_user.is_authenticated:
        if Atable_fav.query.filter_by(user_id=current_user.id, fav_id=post_id).first() is not None:
            flag = True
    return render_template('post.html', title='Post', post=post, searchform=searchform, commentform=commentform, faved=flag)


@login_required
@posts.route('/post/<int:post_id>/delete', methods=['GET', 'POST'])
def post_delete(post_id):
    searchform = SearchForm()
    return render_template('delete.html', post=Post.query.get_or_404(post_id), searchform=searchform)


@login_required
@posts.route('/post/<int:post_id>/delete_confirm', methods=['POST'])
def confirm_delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author == current_user or current_user.status == 'admin' or current_user.status == 'creator':
        picture_path = os.path.join(current_app.root_path, f'static/post_images/{post.picture}')
        for i in post.tag_list:
            print(i)
            db.session.delete(i)
        for i in post.likers_list:
            rel_fav = Atable_fav.query.filter_by(user_id=i.user_id, fav_id=post.id).first()
            db.session.delete(rel_fav)
        del_notif = Notification.query.filter_by(post_id=post.id).first()
        if del_notif is not None:
            for rel in Atable_notif.query.filter_by(notif_id=del_notif.id):
                db.session.delete(rel)
        db.session.delete(del_notif)
        db.session.delete(post)
        db.session.commit()
        os.remove(picture_path)
    else:
        abort(403)
    return redirect(url_for('main.home'))


@login_required
@posts.route('/favorite/<int:post_id>', methods=['GET', 'POST'])
def add_favorite(post_id):
    fav = Post.query.get(post_id)
    new_record = Atable_fav(user_id=current_user.id, fav_id=fav.id)
    db.session.add(new_record)
    db.session.commit()
    return redirect(url_for('posts.post', post_id=post_id))


@login_required
@posts.route('/unfavorite/<int:post_id>', methods=['GET', 'POST'])
def remove_favorite(post_id):
    rel = Atable_fav.query.filter_by(user_id=current_user.id, fav_id=post_id).first()
    db.session.delete(rel)
    db.session.commit()
    return redirect(url_for('posts.post', post_id=post_id))


@login_required
@posts.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def post_edit(post_id):
    searchform = SearchForm()
    info = "Max size is 256kB. Leave blank if you don't want to change picture"
    post = Post.query.get_or_404(post_id)
    uploadform = UploadForm()
    if post.author != current_user and current_user.role == 0:
        abort(403)
    if uploadform.validate_on_submit():
        if uploadform.picture.data:
            picture_file, width, height = save_picture(uploadform.picture.data, 'no', 'post_images')
            post.picture = picture_file
            post.width = width
            post.height = height
        edit_tags_set = set(post.edit_tags.split(', '))
        new_tags_set = set(uploadform.tags.data.split(', '))
        post.edit_tags = uploadform.tags.data
        db.session.commit()
        delete_tags = list(edit_tags_set - new_tags_set)
        for i in delete_tags:
            tag_to_del = Tag.query.filter_by(name=i).first()
            rel = Atable_tag.query.filter_by(tag_id=tag_to_del.id).first()
            if rel is not None:
                db.session.delete(rel)
                db.session.commit()
        append_tags = list(new_tags_set - edit_tags_set)
        for i in append_tags:
            elem = Tag.query.filter_by(name=i).first()
            if not elem:
                new_tag = Tag(name=i)
                elem = new_tag
                db.session.add(new_tag)
                db.session.commit()
            new_record = Atable_tag(post_id=post.id, tag_id=elem.id)
            # check if no record exists otherwise it will result int NOT_UNIQUE error
            if not Atable_tag.query.filter_by(post_id=post.id, tag_id=elem.id).first():
                db.session.add(new_record)
                db.session.commit()
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        uploadform.picture.data = post.picture
        uploadform.tags.data = post.edit_tags
    return render_template('upload.html', title='Edit', post=post, uploadform=uploadform, info=info, searchform=searchform)



@login_required
@posts.route('/upload', methods=['GET', 'POST'])
def upload():
    searchform = SearchForm()
    if current_user.status == 'banned':
        return render_template('banned.html')
    info = "Max size is 256kB."
    uploadform = UploadForm()
    if uploadform.validate_on_submit():
        picture_file, width, height = save_picture(uploadform.picture.data, 'no', 'post_images')
        tags = uploadform.tags.data.split(', ')
        post = Post(picture=picture_file, picture_w=width, picture_h=height, author=current_user)
        post.edit_tags = uploadform.tags.data
        post.user_id = current_user.id
        for i in tags:
            elem = Tag.query.filter_by(name=i).first()
            if not elem:
                new_tag = Tag(name=i)
                elem = new_tag
                db.session.add(new_tag)
            new_record = Atable_tag(post_id=post.id, tag_id=elem.id)
            db.session.add(new_record)
        db.session.add(post)
        notification = Notification(username=current_user.username, post_id=post.id, type='upload', content=" uploaded a new ")
        db.session.add(notification)
        followers_id = [i.sub_id for i in Atable_subs.query.filter_by(cmaker_id=current_user.id)]
        for f_id in followers_id:
            rel_notif = Atable_notif(notif_id=notification.id, recip_id=f_id)
            db.session.add(rel_notif)
        db.session.commit()
        return redirect(url_for('main.home'))
    return render_template('upload.html', title='Upload', uploadform=uploadform, info=info, searchform=searchform)
