import os
from flask import Blueprint, flash, render_template, url_for, redirect, request, abort, current_app
from flask_login import current_user, login_required
from package import db
from package.models import User, Post, Tag, Atable, Comment
from package.posts.forms import SearchForm, UploadForm, CommentForm
from package.users.utils import save_picture

posts = Blueprint('posts', __name__)


@posts.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):
    commentform = CommentForm()
    searchform = SearchForm()
    post = Post.query.get_or_404(post_id)
    if commentform.validate_on_submit():
        comment = Comment(author=current_user.username, content=commentform.content.data, post_id=post_id)
        post.comment_list.append(comment)
        db.session.commit()
        return redirect(url_for('posts.post', post_id=post_id))
    return render_template('post.html', title='Post', post=post, searchform=searchform, commentform=commentform)


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
        for i in range(len(post.tag_list)):
            rel = Atable.query.filter_by(post_id=post.id).first()
            db.session.delete(rel)
            db.session.commit()
        db.session.delete(post)
        db.session.commit()
        os.remove(picture_path)
    else:
        abort(403)
    return redirect(url_for('main.home'))


@login_required
@posts.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def post_edit(post_id):
    searchform = SearchForm()
    info = "Max size is 256kB. Leave blank if you don't want to change picture"
    post = Post.query.get_or_404(post_id)
    form = UploadForm()
    if post.author != current_user and current_user.role == 0:
        abort(403)
    if form.validate_on_submit():
        if form.picture.data:
            picture_file, width, height = save_picture(form.picture.data, 'no', 'post_images')
            post.picture = picture_file
            post.width = width
            post.height = height
        post.tag_list = form.tags.data
        db.session.commit()
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.picture.data = post.picture
        form.tags.data = post.tag_list
    return render_template('upload.html', title='Edit', post=post, form=form, info=info, searchform=searchform)



@login_required
@posts.route('/upload', methods=['GET', 'POST'])
def upload():
    searchform = SearchForm()
    if current_user.status == 'banned':
        return render_template('banned.html')
    info = "Max size is 256kB."
    form = UploadForm()
    if form.validate_on_submit():
        picture_file, width, height = save_picture(form.picture.data, 'no', 'post_images')
        tags = form.tags.data.split(', ')
        print(tags)
        post = Post(picture=picture_file, picture_w=width, picture_h=height, author=current_user)
        for i in tags:
            elem = Tag.query.filter_by(name=i).first()
            if not elem:
                new_tag = Tag(name=i)
                elem = new_tag
                db.session.add(new_tag)
                db.session.commit()
            new_record = Atable(post_id=post.id, tag_id=elem.id)
            db.session.add(new_record)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.home'))
    return render_template('upload.html', title='Upload', form=form, info=info, searchform=searchform)
