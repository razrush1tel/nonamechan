from flask import Blueprint, render_template, request
from package.models import Post, Tag, Atable_tag
from package.posts.forms import SearchForm
from functools import reduce

main = Blueprint('main', __name__)

def extract_tags(posts):
    tags = dict()
    tag_list = list()
    for post in posts:
        tag_line = post.edit_tags.split(', ')
        for tag in tag_line:
            if tag not in tags:
                tags[tag] = 1
            else:
                tags[tag] += 1
    for tag in tags:
        tag_list.append((tags[tag], tag))
    tag_list.sort(reverse=True)
    return tag_list

@main.route('/')
@main.route('/home', methods=['GET', 'POST'])
def home():
    searchform = SearchForm()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=24, page=page)
    return render_template('home.html', posts=posts, searchform=searchform, tag_list=extract_tags(posts.items))

@main.route('/search', methods=['GET', 'POST'])
def search():
    try: tags = request.form['query'].split(', ')
    except KeyError: tags = [request.args.get('tag', type=str)]
    searchform = SearchForm()

    tag_ids = list(map(lambda x: Tag.query.filter_by(name=x).first().id, tags))
    aqf = lambda x: set(list(map(lambda y: y.post_id,
            Atable_tag.query.filter_by(tag_id=x).all())))
    result = reduce(lambda x, y: x.intersection(aqf(y)), tag_ids, aqf(tag_ids.pop()))

    posts = Post.query.filter(Post.id.in_(result)).order_by(Post.date_posted.desc()).paginate(per_page=24, page=request.args.get('page', 1, type=int))
    return render_template('search.html', posts=posts, searchform=searchform, filter=', '.join(tags), tag_list=extract_tags(posts.items))
