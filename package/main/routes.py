from flask import Blueprint, render_template, request
from package.models import Post, Tag
from package.posts.forms import SearchForm

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
    empty = True
    try:
        tags = request.form['query'].split(', ')
    except KeyError:
        tags = [request.args.get('tag', type=str)]
    searchform = SearchForm()
    page = request.args.get('page', 1, type=int)
    sets = list()
    select = list()
    for tag in tags:
        post_ids = Tag.query.filter_by(name=tag).first()
        if post_ids is not None:
            post_ids = post_ids.post_list
            id_set = set()
            for post_id in post_ids:
                id_set.add(post_id.post_id)
            print(id_set)
            sets.append(set(id_set))
            while len(sets) > 1:
                try:
                    sets[0] = sets[0].intersection(sets[1])
                    sets.pop(1)
                except:
                    break
            sets = list(sets)
            select = list(sets[0])
            print(list(sets[0]))
            empty = False
<<<<<<< HEAD
    posts = Post.query.filter(Post.id.in_(select)).order_by(Post.date_posted.desc()).paginate(per_page=24, page=page)
    return render_template('search.html', posts=posts, emptry=empty, searchform=searchform, filter=', '.join(tags))
=======
    posts = Post.query.filter(Post.id.in_(sets)).order_by(Post.date_posted.desc()).paginate(per_page=24, page=page)
    return render_template('search.html', posts=posts, emptry=empty, searchform=searchform, filter=', '.join(tags), tag_list=extract_tags(posts.items))
>>>>>>> bfdcfdb11c91f53e8fec313402b6ccda86114fa6
