from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    query = StringField('Query',
                            validators=[DataRequired()], default="")
    submit = SubmitField('Search')


class UploadForm(FlaskForm):
    tags = StringField('Tags',
                            validators=[DataRequired()])
    picture = FileField('Select file',
                            validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Upload')
