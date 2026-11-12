# Database Lab 4 - Part II: Library Management System

**University:** Alexandria National University  
**Faculty:** Faculty of Engineering  
**Course:** Introduction to Database Systems  
**Semester:** Fall 2026

## Submitted by

| Student | Student ID |
|---|---|
| Mahmoud Hassan Elragal | 2304247 |
| Marwan Tamer Hassan | 2304015 |

## Project Overview

This project implements Part II (Problem 2) of Database Lab 4. It extends the Lab 3 Flask website with a six-table MySQL library database and the search and reporting features specified in F2.1-F2.6. The bonus requirement is implemented using parameterized queries in the book search form.

## Software Requirements

- Python 3
- MySQL 8 with a running database server
- MySQL Workbench or the MySQL command-line client
- Python dependencies listed in `website/requirements.txt`

## Installation and Execution

Run the following commands from the project root folder.

### 1. Install Python Dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r website/requirements.txt
```

### 2. Initialize the Databases

In MySQL Workbench, connect to the local MySQL server and open and execute the following scripts in order:

1. `website/database/schema.sql`
2. `problem2_DDL.sql`
3. `problem2_DML.sql`
4. `problem2_Queries.sql`

Alternatively, start the MySQL command-line client from the project root:

```powershell
mysql -u root -p
```

Then execute:

```sql
SOURCE website/database/schema.sql;
SOURCE problem2_DDL.sql;
SOURCE problem2_DML.sql;
SOURCE problem2_Queries.sql;
exit;
```

The `registration` database stores user accounts and to-do records retained from the previous assignment. The `library` database stores the six library tables. The registration setup creates missing tables without deleting existing accounts.

**Re-running `problem2_DDL.sql` deletes and recreates the `library` database.** Run the seed script once after creating the database. Books and authors subsequently added through the website are stored in MySQL; they do not automatically modify the seed SQL file.

### 3. Configure the Application

```powershell
Copy-Item website/.env.example website/.env
```

Edit `website/.env` using the credentials and port of the MySQL connection:

```dotenv
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_PORT=3306
DB_NAME=registration
LIBRARY_DB_NAME=library
SECRET_KEY=replace_with_a_long_random_value
```

Generate a secret key with:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

The local `.env` file is excluded from version control. The MySQL user must have access to both databases.

### 4. Run the Website

```powershell
.\.venv\Scripts\python.exe website/app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000), register an account or sign in, and select **Library**. Registration retains the previous assignment's validation for Gmail, iCloud, Hotmail, Yahoo and Outlook email addresses. The new library features are available through the navigation menu.

## Implemented Requirements

| Requirement | Page | Functionality |
|---|---|---|
| F2.1 | Search books | Filters titles using `LIKE`, prices using inclusive `BETWEEN`, and books by category; sorts results by ascending price |
| F2.2 | Catalogue | Displays book details with author, publisher and category names using joins |
| F2.3 | Reports | Displays book counts and average prices per category, authors with at least two books using `HAVING`, and total, minimum and maximum book prices |
| F2.4 | Loans | Displays unreturned loans with book and member names, members without loans, and books never borrowed |
| F2.5 | Most borrowed | Displays the three most borrowed books and the member with the most loans using grouping, sorting and `LIMIT` |
| F2.6 | Authors and books | Displays every author's book count, including zero, and books whose author and publisher share a country |
| Bonus | Search books | Passes user-entered values separately through PyMySQL `%s` placeholders in `cursor.execute(sql, values)` |

The SQL statements for these pages are provided in `problem2_Queries.sql` with the required `-- F2.x` labels. The F2.1 example uses MySQL variables for direct execution in Workbench or the command-line client. The application uses the corresponding parameterized query from `website/library_queries.py`.

Author and book management from Lab 3 is retained, including image uploads. The website also supports light and dark themes. Selecting a category automatically applies the search filters.

## Database Design

| Table | Primary Key | Foreign Keys |
|---|---|---|
| `author` | `author_id` | - |
| `publisher` | `publisher_id` | - |
| `category` | `category_id` | - |
| `book` | `book_id` | `author_id`, `publisher_id`, `category_id` |
| `member` | `member_id` | - |
| `loan` | `loan_id` | `book_id`, `member_id` |

Deleting an author cascades to that author's books. Deleting a book cascades to its loans. A `NULL` return date identifies a loan that has not been returned. Optional `cover` and `photo` columns store the filenames used for book covers and author photos.

## Seed Data

The seed script contains **7 authors, 5 publishers, 4 categories, 13 books, 5 members and 12 loans**.

| Required Test Case | Seed Example |
|---|---|
| Two authors from the same country | Naguib Mahfouz and Taha Hussein: Egypt |
| An author without books | Taha Hussein |
| An author with at least two books | Naguib Mahfouz |
| An author and publisher from the same country | Naguib Mahfouz and Dar El Shorouk: Egypt |
| A book priced between 15 and 20 | Palace Walk: 18.50 |
| A book never borrowed | The ABC Murders |
| A member without loans | Youssef Mostafa |
| An unreturned loan | Loans 4, 7 and 12 |

The Science category contains *A Brief History of Time*, *The Universe in a Nutshell* and *Cosmos*. Book covers and author photos are included in `website/static/uploads/`, and their filenames are included in the seed script.

## Submitted Files

```text
lab4-2304247-2304015/
|-- problem2_DDL.sql
|-- problem2_DML.sql
|-- problem2_Queries.sql
|-- README.md
`-- website/
    |-- app.py
    |-- library_queries.py
    |-- requirements.txt
    |-- .env.example
    |-- database/
    |-- templates/
    `-- static/
```

- `problem2_DDL.sql`: database creation, tables, constraints and relationships.
- `problem2_DML.sql`: seed data and image filenames.
- `problem2_Queries.sql`: SQL statements for F2.1-F2.6.
- `website/`: application source, templates, styles and uploaded image assets.
- `README.md`: project description and setup instructions.
