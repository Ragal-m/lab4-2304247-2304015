USE library;
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

-- F2.1 Search: category dropdown
SELECT category_id, name FROM category ORDER BY name;

SET @keyword = '';
SET @min_price = 0;
SET @max_price = 99999999.99;
SET @category_id = NULL;

-- F2.1 Search books (example parameters below)
SELECT b.book_id, b.title, b.price, b.publish_year, a.name AS author, c.name AS category
FROM book b JOIN author a ON b.author_id = a.author_id
JOIN category c ON b.category_id = c.category_id
WHERE b.title LIKE CONCAT('%', @keyword, '%') AND b.price BETWEEN @min_price AND @max_price
  AND (@category_id IS NULL OR b.category_id = @category_id)
ORDER BY b.price ASC, b.book_id ASC;

-- F2.2 Catalogue
SELECT b.book_id, b.title, b.price, b.publish_year,
       a.name AS author, p.name AS publisher, c.name AS category
FROM book b JOIN author a ON b.author_id = a.author_id
JOIN publisher p ON b.publisher_id = p.publisher_id
JOIN category c ON b.category_id = c.category_id
ORDER BY b.title, b.book_id;

-- F2.3 (a) Categories
SELECT c.name AS category, COUNT(b.book_id) AS book_count, ROUND(AVG(b.price), 2) AS average_price
FROM category c LEFT JOIN book b ON c.category_id = b.category_id
GROUP BY c.category_id, c.name ORDER BY c.name;

-- F2.3 (b) Authors with at least two books
SELECT a.name AS author, COUNT(b.book_id) AS book_count
FROM author a JOIN book b ON a.author_id = b.author_id
GROUP BY a.author_id, a.name HAVING COUNT(b.book_id) >= 2
ORDER BY book_count DESC, a.author_id;

-- F2.3 (c) Library prices
SELECT SUM(price) AS total_price, MIN(price) AS smallest_price, MAX(price) AS largest_price FROM book;

-- F2.4 (a) Unreturned loans
SELECT l.loan_id, b.title AS book, m.name AS member, l.loan_date
FROM loan l JOIN book b ON l.book_id = b.book_id
JOIN member m ON l.member_id = m.member_id
WHERE l.return_date IS NULL ORDER BY l.loan_date, l.loan_id;

-- F2.4 (b) Members without loans
SELECT m.member_id, m.name, m.email FROM member m
LEFT JOIN loan l ON m.member_id = l.member_id
WHERE l.loan_id IS NULL ORDER BY m.member_id;

-- F2.4 (c) Books never borrowed
SELECT b.book_id, b.title FROM book b
LEFT JOIN loan l ON b.book_id = l.book_id
WHERE l.loan_id IS NULL ORDER BY b.book_id;

-- F2.5 (a) Top three books
SELECT b.book_id, b.title, COUNT(l.loan_id) AS loan_count
FROM book b JOIN loan l ON b.book_id = l.book_id
GROUP BY b.book_id, b.title ORDER BY loan_count DESC, b.book_id ASC LIMIT 3;

-- F2.5 (b) Top member
SELECT m.member_id, m.name AS member, COUNT(l.loan_id) AS loan_count
FROM member m JOIN loan l ON m.member_id = l.member_id
GROUP BY m.member_id, m.name ORDER BY loan_count DESC, m.member_id ASC LIMIT 1;

-- F2.6 (a) All authors, including zero books
SELECT a.name AS author, a.country, COUNT(b.book_id) AS book_count
FROM author a LEFT JOIN book b ON a.author_id = b.author_id
GROUP BY a.author_id, a.name, a.country ORDER BY a.author_id;

-- F2.6 (b) Author and publisher from the same country
SELECT b.title, a.name AS author, p.name AS publisher, a.country
FROM book b JOIN author a ON b.author_id = a.author_id
JOIN publisher p ON b.publisher_id = p.publisher_id
WHERE a.country = p.country ORDER BY b.book_id;
