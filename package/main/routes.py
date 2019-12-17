from flask import Blueprint, render_template, request
from package.models import Post, Tag
from package.posts.forms import SearchForm

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home', methods=['GET', 'POST'])
def home():
    searchform = SearchForm()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=24, page=page)
    return render_template('home.html', posts=posts, searchform=searchform)


@main.route('/search', methods=['GET', 'POST'])
def search():
    empty = True
    try:
        tags = request.form['query'].split(', ')
    except KeyError:
        tags = [request.args.get('tag', type=str)]
    searchform = SearchForm()
    page = request.args.get('page', 1, type=int)
    sets = []
    for tag in tags:
        post_ids = Tag.query.filter_by(name=tag).first()
        if post_ids is not None:
            post_ids = post_ids.post_list
            id_set = set()
            for post_id in post_ids:
                id_set.add(post_id.post_id)
            sets.append(id_set)
            while len(sets) > 1:
                sets[0] = sets[0].intersection(sets[1])
                sets.pop(1)
            sets = sets[0]
            empty = False
    posts = Post.query.filter(Post.id.in_(sets)).order_by(Post.date_posted.desc()).paginate(per_page=24, page=page)
    return render_template('search.html', posts=posts, emptry=empty, searchform=searchform, filter=', '.join(tags))
