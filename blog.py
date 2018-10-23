from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, patientName, dob, diagnosis, treatment, created, author_id, username'
        ' FROM medicalInfo p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        patientName = request.form['patientName']
        dob = request.form['dob']
        diagnosis = request.form['diagnosis']
        treatment = request.form['treatment']
        error = None

        if not patientName:
            error = 'Name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO medicalInfo (patientName, dob, diagnosis, treatment, author_id)'
                ' VALUES (?, ?, ?, ?, ?)',
                (patientName, dob, diagnosis, treatment, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

def get_post(id, check_author=True):
    medicalInfo = get_db().execute(
        'SELECT p.id, patientName, dob, diagnosis, treatment, author_id, username'
        ' FROM medicalInfo p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if medicalInfo is None:
        abort(404, "Entry id {0} doesn't exist.".format(id))

    if check_author and medicalInfo['author_id'] != g.user['id']:
        abort(403)

    return medicalInfo

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    medicalInfo = get_post(id)

    if request.method == 'POST':
        patientName = request.form['patientName']
        dob = request.form['dob']
        diagnosis = request.form['diagnosis']
        treatment = request.form['treatment']
        error = None

        if not patientName:
            error = 'Name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE medicalInfo SET patientName = ?, dob = ?, diagnosis = ?, treatment = ?'
                ' WHERE id = ?',
                (name, dob, diagnosis, treatment, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', medicalInfo=medicalInfo)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM medicalInfo WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))