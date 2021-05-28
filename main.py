from flask import Flask, render_template, url_for, flash, redirect, request, session
from forms import RegistrationForm, LoginForm, PostForm, UpdatePasswordForm, EditPostForm
from google.cloud import datastore
from google.cloud import storage
from datetime import datetime
import os
import uuid


import logging

app = Flask(__name__)

app.config['SECRET_KEY'] = '123egnjkan35hsjks'
#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "E:\Technologies\Projects\Cloud\GoogleKey\cc-s3797101-d26f2ff3a379.json"


datastore_client = datastore.Client()

# def store_post()


def store_image(image_url):
    uploaded_file = image_url

    # Create a Cloud Storage client.
    gcs = storage.Client()

    # Get the bucket that the file will be uploaded to.
    bucket = gcs.get_bucket('imagedatacloud')

    # Create a new blob and upload the file's content.
    blob = bucket.blob(uploaded_file.filename)

    blob.upload_from_string(
        uploaded_file.read(),
        content_type=uploaded_file.content_type
    )
    return blob.public_url


@app.route("/home", methods=['GET', 'POST'])
def home():

    form = PostForm()
    if request.method == 'GET':
        query = datastore_client.query(kind='Post')
        query.order = ['-date']
        posts = list(query.fetch())
        return render_template('home.html', posts=posts, form=form, current_user=session['user_info']['username'],
                               current_user_img=session['user_info']['user_image'])

    elif request.method == 'POST':
        form = PostForm()
        if form.validate_on_submit:
            image_url = store_image(form.picture.data)
            uniqueID = str(uuid.uuid4())
            query_user = datastore_client.query(kind='User')
            user_data = query_user.add_filter("user_id", "=", session['user_info']['user_id'])
            user_results = list(user_data.fetch())
            post_entity = datastore.Entity(
                key=datastore_client.key('User', session['user_info']['user_id'], 'Post', uniqueID))
            post_entity.update({
                "post_id": uniqueID,
                'user_name': session['user_info']['username'],
                'subject': form.subject.data,
                'message': form.content.data,
                'image': image_url,
                'user_image' : user_results[0]['user_image'],
                'date': datetime.now()

            })

            datastore_client.put(post_entity)
            query = datastore_client.query(kind='Post')
            query.order = ['-date']
            posts = list(query.fetch())

        return render_template('home.html', posts=posts, form=form, current_user=session['user_info']['username'],
                               current_user_img=session['user_info']['user_image'])



@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        form = RegistrationForm()
        return render_template("register.html", form=form)
    elif request.method == 'POST':
        form = RegistrationForm()
        if form.validate_on_submit():
            query = datastore_client.query(kind='User')
            data = query.add_filter("user_id", "=", form.id.data)
            query = datastore_client.query(kind='User')
            user_data = query.add_filter("username", "=", form.username.data)
            results = list(data.fetch())
            user_results = list(user_data.fetch())
            if len(results) > 0:
                if form.id.data == results[0]['user_id']:
                    flash('Registration Fail, ID already exists', 'danger')

            elif len(user_results) > 0:
                flash('Registration Fail, username already exists', 'danger')
            else:

                generated_image_url = store_image(form.user_image.data)

                entity = datastore.Entity(
                    key=datastore_client.key('User', form.id.data))
                entity.update({
                    'user_id': form.id.data,
                    'username': form.username.data,
                    'password': form.password.data,
                    "user_image": generated_image_url
                })
                datastore_client.put(entity)
                flash(f'Account created for {form.username.data}!', 'success')
                return redirect(url_for('login'))
        return render_template('register.html', title='Register', form=form)


@app.route("/")
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        form = LoginForm()
        return render_template("login.html", form=form)
    elif request.method == 'POST':
        form = LoginForm()
        if form.validate_on_submit():
            query = datastore_client.query(kind='User')
            data = query.add_filter("user_id", "=", form.id.data)
            results = list(data.fetch())
            if len(results) > 0 and form.id.data == results[0]['user_id'] and form.password.data == results[0]['password']:
                session['user_info'] = results[0]
                return redirect(url_for('home'))
            else:
                flash('Login Fail. Please check the login credentials', 'danger')
        return render_template('login.html', title='Login', form=form)


@app.route("/user", methods=['GET', 'POST'])
def user():

    if request.method == 'GET':
        form = UpdatePasswordForm()
        query = datastore_client.query(kind='Post')
        query.add_filter("user_name", "=", session['user_info']['username'])
        posts = list(query.fetch())
        posts
        return render_template('user.html', posts=posts, form=form, )

    elif request.method == 'POST':
        form = UpdatePasswordForm()
        if form.validate_on_submit():
            query = datastore_client.query(kind='User')
            data = query.add_filter(
                "username", "=", session['user_info']['username'])
            results = list(data.fetch())
            if len(results) > 0 and form.old_password.data == results[0]['password']:
                key = datastore_client.key(
                    'User', session['user_info']['username'])
                task = datastore_client.get(key)
                task['password'] = form.new_password.data
                datastore_client.put(task)
                return redirect(url_for('login'))
            else:
                flash('The ld password is incorrect. Please try again!', 'danger')
                return redirect(url_for('user'))
        else:
            app.logger.info("Validation fail ")

    return render_template('user.html', title='user', form=form)


@app.route("/post/<string:postId>/", methods=['GET', 'POST'])
def post(postId):
    query = datastore_client.query(kind='Post')
    query.add_filter("post_id", "=", postId)
    post = list(query.fetch())
    form = EditPostForm()
    if form.validate_on_submit():
        image_url = store_image(form.picture.data)

        query = datastore_client.query(kind='Post')
        data = query.add_filter(
            "post_id", "=", postId)
        results = list(data.fetch())
        key = datastore_client.key(
            'User', session['user_info']['username'])
        task = datastore_client.get(key)
        task['subject'] = form.subject.data
        task['message'] = form.content.data
        task['image'] = image_url
        task['date'] = datetime.now()
        datastore_client.put(task)
        flash('Your post has been updated!', 'success')
        return redirect(url_for('home', ))
    elif request.method == 'GET':
        form.subject.data = post[0]['subject']
        form.content.data = post[0]['message']
        form.picture.data = post[0]['image']

    return render_template('EditPost.html', title='Edit post',
                           form=form)


@app.route("/post/<string:postId>/edit")
def edit_post(postId):
    query = datastore_client.query(kind='Post')
    query.add_filter("post_id", "=", postId)
    post = list(query.fetch())
    return render_template('post.html', post=post)


@app.route("/logout")
def logout():
    session.pop('user_info', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
