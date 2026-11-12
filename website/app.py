import os
import re
import uuid
import pymysql
import bcrypt
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from dotenv import load_dotenv
from functools import wraps
from contextlib import contextmanager
from library_queries import QUERIES
from flask import Flask, render_template, request, redirect, url_for, session, flash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default-dev-secret-key')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024


UPLOAD_DIR = os.path.join(app.root_path, 'static', 'uploads')
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'jfif', 'gif', 'webp'}


EMAIL_PATTERN = re.compile(r'^[^\s@]+@(gmail|icloud|hotmail|yahoo|outlook)\.com$', re.IGNORECASE)


def get_db_connection(database=None):
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=database or os.getenv('DB_NAME', 'registration'),
        charset='utf8mb4',
        port=int(os.getenv('DB_PORT', 3306)),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )


@contextmanager
def get_cursor():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            yield cursor
    finally:
        conn.close()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('todo_list'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('todo_list'))

    errors = []
    form_data = {'name': '', 'email': ''}

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        form_data['name'] = name
        form_data['email'] = email

        if not name:
            errors.append('Name is required')
        if not email:
            errors.append('Email is required')
        elif not EMAIL_PATTERN.match(email):
            errors.append('Email must be @gmail.com, @icloud.com, @hotmail.com, @yahoo.com or @outlook.com')
        if not password:
            errors.append('Password is required')
        if not confirm_password:
            errors.append('Confirm password is required')
        if password and confirm_password and password != confirm_password:
            errors.append('Passwords do not match')

        if not errors:
            with get_cursor() as cursor:
                cursor.execute("SELECT user_id FROM users WHERE email = %s;", (email,))
                if cursor.fetchone():
                    errors.append('Email Already Exists')
                else:
                    salt = bcrypt.gensalt()
                    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
                    cursor.execute(
                        "INSERT INTO users (email, name, password_hash) VALUES (%s, %s, %s);",
                        (email, name, hashed_pw)
                    )
                    user_id = cursor.lastrowid
                    session['user_id'] = user_id
                    session['name'] = name
                    return redirect(url_for('todo_list'))

    return render_template('register.html', errors=errors, form_data=form_data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('todo_list'))

    errors = []
    form_data = {'email': ''}

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        form_data['email'] = email

        if not email:
            errors.append('Email is required')
        if not password:
            errors.append('Password is required')

        if not errors:
            with get_cursor() as cursor:
                cursor.execute(
                    "SELECT user_id, name, password_hash FROM users WHERE email = %s;",
                    (email,)
                )
                user = cursor.fetchone()

                if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                    session['user_id'] = user['user_id']
                    session['name'] = user['name']
                    return redirect(url_for('todo_list'))
                else:
                    errors.append('Invalid email or password')

    return render_template('login.html', errors=errors, form_data=form_data)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/todos', methods=['GET'])
@login_required
def todo_list():
    now_dt = datetime.now()
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT todo_id, title, is_done, due_date, created_at
            FROM todos
            WHERE user_id = %s
            ORDER BY is_done ASC, due_date IS NULL ASC, due_date ASC, todo_id DESC;
            """,
            (session['user_id'],)
        )
        todos = cursor.fetchall()


        for todo in todos:
            d = todo.get('due_date')
            if d is not None and not isinstance(d, datetime) and isinstance(d, date):
                todo['due_date'] = datetime.combine(d, datetime.min.time())


        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_count,
                COALESCE(SUM(CASE WHEN is_done = 0 THEN 1 ELSE 0 END), 0) AS active_count,
                COALESCE(SUM(CASE WHEN is_done = 1 THEN 1 ELSE 0 END), 0) AS done_count,
                COALESCE(SUM(CASE WHEN is_done = 0 AND due_date IS NOT NULL AND due_date < %s THEN 1 ELSE 0 END), 0) AS overdue_count
            FROM todos
            WHERE user_id = %s;
            """,
            (now_dt, session['user_id'])
        )
        counts = cursor.fetchone()
        total_count = int(counts['total_count'] or 0)
        active_count = int(counts['active_count'] or 0)
        done_count = int(counts['done_count'] or 0)
        overdue_count = int(counts['overdue_count'] or 0)

    return render_template(
        'todos.html',
        todos=todos,
        user_name=session.get('name'),
        total_count=total_count,
        active_count=active_count,
        done_count=done_count,
        overdue_count=overdue_count,
        now=now_dt
    )


@app.route('/todos/add', methods=['POST'])
@login_required
def add_todo():
    title = request.form.get('title', '').strip()
    due_date = request.form.get('due_date', '').strip() or None

    if due_date:
        due_date = due_date.replace('T', ' ')

    if not title:
        flash('Title is required', 'error')
    elif len(title) > 200:
        flash('Title is too long', 'error')
    else:
        with get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO todos (user_id, title, due_date) VALUES (%s, %s, %s);",
                (session['user_id'], title, due_date)
            )
    return redirect(url_for('todo_list'))


@app.route('/todos/edit/<int:todo_id>', methods=['POST'])
@login_required
def edit_todo(todo_id):
    title = request.form.get('title', '').strip()
    due_date = request.form.get('due_date', '').strip() or None

    if due_date:
        due_date = due_date.replace('T', ' ')

    if not title:
        flash('Title is required', 'error')
    elif len(title) > 200:
        flash('Title is too long', 'error')
    else:
        with get_cursor() as cursor:
            cursor.execute(
                "UPDATE todos SET title = %s, due_date = %s WHERE todo_id = %s AND user_id = %s;",
                (title, due_date, todo_id, session['user_id'])
            )
    return redirect(url_for('todo_list'))


@app.route('/todos/toggle/<int:todo_id>', methods=['POST'])
@login_required
def toggle_todo(todo_id):
    status = request.form.get('is_done', '0')
    new_status = 1 if status == '1' else 0
    with get_cursor() as cursor:
        cursor.execute(
            "UPDATE todos SET is_done = %s WHERE todo_id = %s AND user_id = %s;",
            (new_status, todo_id, session['user_id'])
        )
    return redirect(url_for('todo_list'))


@app.route('/todos/delete/<int:todo_id>', methods=['POST'])
@login_required
def delete_todo(todo_id):
    with get_cursor() as cursor:
        cursor.execute(
            "DELETE FROM todos WHERE todo_id = %s AND user_id = %s;",
            (todo_id, session['user_id'])
        )
    return redirect(url_for('todo_list'))


@contextmanager
def get_library_cursor():
    conn = get_db_connection(os.getenv('LIBRARY_DB_NAME', 'library'))
    try:
        with conn.cursor() as cursor:
            yield cursor
    finally:
        conn.close()




def is_allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def image_errors():
    upload = request.files.get('image')
    if upload and upload.filename and not is_allowed_image(upload.filename):
        return ['Image must be a PNG, JPG, JFIF, GIF or WEBP file']
    return []


def save_image(upload):
    """Save an uploaded image under a random name and return that name (None if no file was chosen)."""
    if not upload or not upload.filename:
        return None
    ext = upload.filename.rsplit('.', 1)[1].lower()
    if ext == 'jfif':
        ext = 'jpg'
    filename = f"{uuid.uuid4().hex}.{ext}"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    upload.save(os.path.join(UPLOAD_DIR, filename))
    return filename


def updated_image(current):
    """Image to keep after an edit form: a new upload, none if removed, otherwise the current one."""
    upload = request.files.get('image')
    if upload and upload.filename:
        return save_image(upload)
    if request.form.get('remove_image'):
        return None
    return current


def delete_image(filename):
    if filename:
        path = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(path):
            os.remove(path)


@app.errorhandler(413)
def upload_too_large(e):
    flash('Image is too large (max 5 MB)', 'error')
    return redirect(request.url)


@app.route('/library')
@login_required
def library():
    with get_library_cursor() as cursor:
        cursor.execute("SELECT book_id, title, price, author_id, cover FROM book ORDER BY book_id;")
        books = cursor.fetchall()
        cursor.execute("SELECT author_id, name, country, photo FROM author ORDER BY author_id;")
        authors = cursor.fetchall()


    author_names = {a['author_id']: a['name'] for a in authors}
    book_counts = {a['author_id']: 0 for a in authors}
    for book in books:
        book_counts[book['author_id']] = book_counts.get(book['author_id'], 0) + 1

    return render_template(
        'library.html',
        books=books,
        authors=authors,
        author_names=author_names,
        book_counts=book_counts,
        user_name=session.get('name')
    )


def get_author_choices(cursor):
    cursor.execute("SELECT author_id, name FROM author ORDER BY name;")
    return cursor.fetchall()


def validate_book_form(cursor):
    form_data = {
        'title': request.form.get('title', '').strip(),
        'price': request.form.get('price', '').strip(),
        'author_id': request.form.get('author_id', '').strip(),
        'publisher_id': request.form.get('publisher_id', '').strip(),
        'category_id': request.form.get('category_id', '').strip(),
        'publish_year': request.form.get('publish_year', '').strip(),
    }
    errors = []

    if not form_data['title']:
        errors.append('Title is required')
    elif len(form_data['title']) > 200:
        errors.append('Title is too long')

    if not form_data['price']:
        errors.append('Price is required')
    else:
        try:
            price = Decimal(form_data['price'])
            if not price.is_finite() or price < 0 or price >= Decimal('100000000'):
                errors.append('Price must be between 0 and 99999999.99')
            else:
                form_data['price'] = str(price.quantize(Decimal('0.01')))
        except InvalidOperation:
            errors.append('Price must be a number')

    if not form_data['author_id']:
        errors.append('Author is required')
    elif not form_data['author_id'].isdigit():
        errors.append('Author does not exist')
    else:
        cursor.execute("SELECT author_id FROM author WHERE author_id = %s;", (form_data['author_id'],))
        if not cursor.fetchone():
            errors.append('Author does not exist')

    for key, table in [('publisher_id', 'publisher'), ('category_id', 'category')]:
        value = form_data[key]
        if not value.isdigit():
            errors.append(table.title() + ' is required')
        else:

            cursor.execute(f'SELECT {key} FROM {table} WHERE {key} = %s', (value,))
            if not cursor.fetchone():
                errors.append(table.title() + ' does not exist')
    year = form_data['publish_year']
    if not year.isdigit() or not 1 <= int(year) <= 9999:
        errors.append('Publish year must be between 1 and 9999')
    return form_data, errors + image_errors()


def book_choices(cursor):
    cursor.execute('SELECT publisher_id, name FROM publisher ORDER BY name')
    publishers = cursor.fetchall()
    cursor.execute(QUERIES['categories'])
    return publishers, cursor.fetchall()


@app.route('/books/add', methods=['GET', 'POST'])
@login_required
def add_book():
    errors = []
    form_data = {'title': '', 'price': '', 'author_id': request.args.get('author_id', ''),
                 'publisher_id': '', 'category_id': '', 'publish_year': ''}

    with get_library_cursor() as cursor:
        if request.method == 'POST':
            form_data, errors = validate_book_form(cursor)
            if not errors:
                cover = save_image(request.files.get('image'))
                cursor.execute(
                    "INSERT INTO book (title, price, author_id, cover, publish_year, publisher_id, category_id) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                    (form_data['title'], form_data['price'], form_data['author_id'], cover, form_data['publish_year'], form_data['publisher_id'], form_data['category_id'])
                )
                flash(f"Book \"{form_data['title']}\" added", 'success')
                return redirect(url_for('library'))
        authors = get_author_choices(cursor)
        publishers, categories = book_choices(cursor)

    return render_template('book_form.html', book_id=None, form_data=form_data,
                           errors=errors, authors=authors, publishers=publishers, categories=categories, image=None)


@app.route('/books/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    errors = []

    with get_library_cursor() as cursor:
        cursor.execute("SELECT title, price, author_id, cover, publish_year, publisher_id, category_id FROM book WHERE book_id = %s;", (book_id,))
        book = cursor.fetchone()
        if not book:
            flash('Book not found', 'error')
            return redirect(url_for('library'))

        form_data = {key: str(book[key]) for key in ('title', 'price', 'author_id', 'publish_year', 'publisher_id', 'category_id')}

        if request.method == 'POST':
            form_data, errors = validate_book_form(cursor)
            if not errors:
                cover = updated_image(book['cover'])
                cursor.execute(
                    "UPDATE book SET title = %s, price = %s, author_id = %s, cover = %s, publish_year = %s, publisher_id = %s, category_id = %s WHERE book_id = %s;",
                    (form_data['title'], form_data['price'], form_data['author_id'], cover, form_data['publish_year'], form_data['publisher_id'], form_data['category_id'], book_id)
                )
                if cover != book['cover']:
                    delete_image(book['cover'])
                flash(f"Book \"{form_data['title']}\" updated", 'success')
                return redirect(url_for('library'))
        authors = get_author_choices(cursor)
        publishers, categories = book_choices(cursor)

    return render_template('book_form.html', book_id=book_id, form_data=form_data,
                           errors=errors, authors=authors, publishers=publishers, categories=categories, image=book['cover'])


@app.route('/books/<int:book_id>/delete', methods=['POST'])
@login_required
def delete_book(book_id):
    with get_library_cursor() as cursor:
        cursor.execute("SELECT title, cover FROM book WHERE book_id = %s;", (book_id,))
        book = cursor.fetchone()
        if book:
            cursor.execute("DELETE FROM book WHERE book_id = %s;", (book_id,))
            delete_image(book['cover'])
            flash(f"Book \"{book['title']}\" removed", 'success')
    return redirect(url_for('library'))


def validate_author_form():
    form_data = {
        'name': request.form.get('name', '').strip(),
        'country': request.form.get('country', '').strip(),
    }
    errors = []

    if not form_data['name']:
        errors.append('Name is required')
    elif len(form_data['name']) > 100:
        errors.append('Name is too long')

    if not form_data['country']:
        errors.append('Country is required')
    elif len(form_data['country']) > 50:
        errors.append('Country is too long')

    return form_data, errors + image_errors()


@app.route('/authors/add', methods=['GET', 'POST'])
@login_required
def add_author():
    errors = []
    form_data = {'name': '', 'country': ''}

    if request.method == 'POST':
        form_data, errors = validate_author_form()
        if not errors:
            photo = save_image(request.files.get('image'))
            with get_library_cursor() as cursor:
                cursor.execute(
                    "INSERT INTO author (name, country, photo) VALUES (%s, %s, %s);",
                    (form_data['name'], form_data['country'], photo)
                )
            flash(f"Author \"{form_data['name']}\" added", 'success')
            return redirect(url_for('library'))

    return render_template('author_form.html', author_id=None, form_data=form_data,
                           errors=errors, image=None)


@app.route('/authors/<int:author_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_author(author_id):
    errors = []

    with get_library_cursor() as cursor:
        cursor.execute("SELECT name, country, photo FROM author WHERE author_id = %s;", (author_id,))
        author = cursor.fetchone()
        if not author:
            flash('Author not found', 'error')
            return redirect(url_for('library'))

        form_data = {'name': author['name'], 'country': author['country']}

        if request.method == 'POST':
            form_data, errors = validate_author_form()
            if not errors:
                photo = updated_image(author['photo'])
                cursor.execute(
                    "UPDATE author SET name = %s, country = %s, photo = %s WHERE author_id = %s;",
                    (form_data['name'], form_data['country'], photo, author_id)
                )
                if photo != author['photo']:
                    delete_image(author['photo'])
                flash(f"Author \"{form_data['name']}\" updated", 'success')
                return redirect(url_for('library'))

    return render_template('author_form.html', author_id=author_id, form_data=form_data,
                           errors=errors, image=author['photo'])


@app.route('/authors/<int:author_id>/delete', methods=['POST'])
@login_required
def delete_author(author_id):
    with get_library_cursor() as cursor:
        cursor.execute("SELECT name, photo FROM author WHERE author_id = %s;", (author_id,))
        author = cursor.fetchone()
        if author:
            cursor.execute("SELECT cover FROM book WHERE author_id = %s;", (author_id,))
            covers = [row['cover'] for row in cursor.fetchall()]


            cursor.execute("DELETE FROM author WHERE author_id = %s;", (author_id,))

            for filename in [author['photo'], *covers]:
                delete_image(filename)
            flash(f"Author \"{author['name']}\" and {len(covers)} book(s) removed", 'success')
    return redirect(url_for('library'))



@app.route('/library/search')
@login_required
def search_books():
    filters = {key: request.args.get(key, '').strip() for key in
               ('keyword', 'min_price', 'max_price', 'category_id')}
    errors = []
    bounds = []
    for key, default in [('min_price', '0'), ('max_price', '99999999.99')]:
        try:
            value = Decimal(filters[key] or default)
            if not value.is_finite() or not 0 <= value <= Decimal('99999999.99'):
                raise InvalidOperation
            bounds.append(value)
        except InvalidOperation:
            errors.append(key.replace('_', ' ').title() + ' must be a number between 0 and 99999999.99.')
    if len(bounds) == 2 and bounds[0] > bounds[1]:
        errors.append('Minimum price must not exceed maximum price.')
    category = filters['category_id']
    category_id = int(category) if category.isascii() and category.isdigit() and len(category) <= 10 else None
    if category and (category_id is None or not 1 <= category_id <= 2147483647):
        errors.append('Choose a valid category.')
    if len(filters['keyword']) > 200:
        errors.append('Title keyword must be at most 200 characters.')
    books = []
    with get_library_cursor() as cursor:
        cursor.execute(QUERIES['categories'])
        categories = cursor.fetchall()
        if category_id is not None and category_id not in {c['category_id'] for c in categories}:
            errors.append('Category does not exist.')
        if not errors:

            cursor.execute(QUERIES['search'], (
                '%' + filters['keyword'] + '%', bounds[0], bounds[1], category_id, category_id))
            books = cursor.fetchall()
    return render_template('search.html', filters=filters, errors=errors,
                           categories=categories, books=books), (400 if errors else 200)


def report_page(title, subtitle, definitions):
    sections = []
    with get_library_cursor() as cursor:
        for heading, key in definitions:
            cursor.execute(QUERIES[key])
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            sections.append({'heading': heading, 'rows': rows, 'columns': columns})
    return render_template('report.html', title=title, subtitle=subtitle, sections=sections)


@app.route('/library/catalogue')
@login_required
def catalogue():
    return report_page('Catalogue', 'All books, with their authors, publishers and categories.',
                       [('All books', 'catalogue')])


@app.route('/library/reports')
@login_required
def library_reports():
    return report_page('Library reports', 'Book counts and prices across the collection.', [
        ('Books and average price by category', 'category_report'),
        ('Authors with at least two books', 'prolific_authors'),
        ('Whole-library price summary', 'price_summary')])


@app.route('/library/loans')
@login_required
def library_loans():
    return report_page('Loans', 'Current borrowing and books and members with no loan history.', [
        ('Loans not returned yet', 'active_loans'),
        ('Members who never borrowed', 'never_members'),
        ('Books never borrowed', 'never_books')])


@app.route('/library/most-borrowed')
@login_required
def most_borrowed():
    return report_page('Most borrowed', 'Ranked by all recorded loans. Ties use the lowest ID first.', [
        ('Top 3 books', 'top_books'), ('Member with the most loans', 'top_member')])


@app.route('/library/authors')
@login_required
def authors_and_books():
    return report_page('Authors and books', 'Every author, including those still waiting for their first book.', [
        ('Books per author', 'author_counts'),
        ('Books with an author and publisher from the same country', 'same_country')])


if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG') == '1', port=5000)