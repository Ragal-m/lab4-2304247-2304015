# Database Lab 4 - Part II: Library

**Team:** Mahmoud Hassan Elragal (2304247) and Marwan Tamer Hassan (2304015).

This continues our Lab 3 Flask/MySQL website and completes **Part II / Problem 2, F2.1-F2.6 and the prepared-statements bonus**. Part I (company database) is outside this project's scope.

## Run step by step (Windows / PowerShell)

Requires Python 3, MySQL 8.0.16+ (tested with MySQL 8.4.3), and a running MySQL server. Start MySQL in Laragon or your normal MySQL installation. Open a terminal in this project's root folder.

1. Install the Python packages:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r website/requirements.txt
   ```

2. Open the MySQL client from the project root:

   ```powershell
   mysql -u root -p
   ```

   If `mysql` is not on PATH, use the MySQL command prompt supplied by Laragon, or execute its full path. Enter your own database password. At the `mysql>` prompt run, in order:

   ```sql
   SOURCE website/database/schema.sql;
   SOURCE problem2_DDL.sql;
   SOURCE problem2_DML.sql;
   SOURCE problem2_Queries.sql;
   exit;
   ```

   `schema.sql` creates the `registration` database and account/to-do tables only if missing. It preserves existing users and tasks. **The library DDL drops and recreates the `library` database**, as required for repeatable assignment setup. Re-running DDL then DML restores the original demonstration data. Run DML once per rebuild.

3. Create your local configuration:

   ```powershell
   Copy-Item website/.env.example website/.env
   ```

   Edit `website/.env` to match your MySQL server:

   ```dotenv
   DB_HOST=127.0.0.1
   DB_USER=root
   DB_PASSWORD=your-own-mysql-password
   DB_PORT=3306
   DB_NAME=registration
   LIBRARY_DB_NAME=library
   SECRET_KEY=replace-with-a-long-random-value
   ```

   Use an empty `DB_PASSWORD=` only if your local server has no password. The MySQL user needs access to both databases. Generate a secret with `python -c "import secrets; print(secrets.token_hex(32))"`. Keep `.env` out of Git.

4. Start the website from the project root:

   ```powershell
   .\.venv\Scripts\python.exe website/app.py
   ```

5. Open **http://127.0.0.1:5000**, register or sign in, then click **Library**. The library navigation links open all six new features. Direct search URL: **http://127.0.0.1:5000/library/search**. Registration retains the original email-provider validation: Gmail, iCloud, Hotmail, Yahoo or Outlook addresses. There is no seeded account; create one through Register.

The new Lab 4 pages use local CSS and work without an external styling service. The preserved Lab 2/3 pages retain their original Tailwind CDN styling. Set `FLASK_DEBUG=1` only when developing locally; it is off by default.

## Features and SQL mapping

| Requirement | Page | Implemented behavior |
|---|---|---|
| F2.1 | `/library/search` | Title LIKE, inclusive min/max price BETWEEN, category dropdown, cheapest first; blank filters search all books |
| F2.2 | `/library/catalogue` | Books with author, publisher and category names through JOINs |
| F2.3 | `/library/reports` | Book count and average price per category, authors with at least 2 books using HAVING, total/min/max library price |
| F2.4 | `/library/loans` | Unreturned loans with member/book names, members without loans, books never borrowed |
| F2.5 | `/library/most-borrowed` | Top 3 borrowed books and single most active member; equal counts resolved by ascending ID |
| F2.6 | `/library/authors` | Every author's book count including zero, books with author/publisher in the same country |
| Bonus | F2.1 search handler | PyMySQL `%s` placeholders and a separate parameter tuple; no user input is interpolated into SQL |
| Lab 3 retained | `/library` | Author/book CRUD, book covers, author photos; book forms include year/publisher/category |

Every SELECT used by the new pages is in `problem2_Queries.sql`, with the required `-- F2.x` comments. It can run directly in the MySQL client. The F2.1 example uses MySQL variables: edit the four SET values to try filters (`NULL` category means all). The live website uses the corresponding queries from `website/library_queries.py` with bound values. PyMySQL handles parameter binding through `execute(sql, values)`; it is not a manually concatenated SQL search.

## Schema and seed cases

The assignment's six tables live in `library`: `author`, `publisher`, `category`, `book`, `member`, `loan`. Every table has a primary key. Books reference authors, publishers and categories; loans reference books and members. Deleting an author cascades to books, and deleting a book cascades to loans. `return_date IS NULL` means the book is still borrowed. Optional `author.photo` and `book.cover` columns preserve Lab 3 image uploads. Prices use DECIMAL; required foreign keys and valid loan date order are enforced.

| Required seed condition | Seed example |
|---|---|
| At least 4 authors / 3 publishers / 3 categories / 10 books / 5 members / 12 loans | 7 / 5 / 4 / 13 / 5 / 12 |
| Two authors from the same country | Naguib Mahfouz and Taha Hussein: Egypt |
| Author without books | Taha Hussein (5) |
| Author with at least 2 books | Naguib Mahfouz has 3 |
| Author and publisher from same country | Naguib Mahfouz / Dar El Shorouk: Egypt |
| Book priced between 15 and 20 | Palace Walk: 18.50; includes exact boundary prices 15.00 and 20.00 |
| Never-borrowed book | The ABC Murders (10), plus 5, 7 and 9 |
| Member without loans | Youssef Mostafa (5) |
| Unreturned loan | Loans 4, 7 and 12 |
| Science books | A Brief History of Time, The Universe in a Nutshell, and Cosmos |

Seeded top books: Palace Walk (4 loans), Murder on the Orient Express (3), One Hundred Years of Solitude (2). Top member: Ahmed Ali (5 loans). Total book prices: 213.99. These are demonstration prices, not current market prices.

All 13 seeded books include their uploaded covers, and all 7 seeded authors include their uploaded photos. The image files are bundled in `website/static/uploads/`; `problem2_DML.sql` restores their filenames when installing the database. Keep this folder in your GitHub repository. Existing database image links are already configured, so no database reset is needed for this packaging update.

## Files for Part II

- `problem2_DDL.sql`: repeatable six-table library schema.
- `problem2_DML.sql`: seed rows for every required case.
- `problem2_Queries.sql`: executable SQL for F2.1-F2.6.
- `website/`: extended original Flask app and pages.
- `README.md`: step-by-step setup and usage.

This repository contains the Part II library assignment and its prepared-search bonus. Submit the GitHub repository link through the assignment form when ready.
