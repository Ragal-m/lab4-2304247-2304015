USE library;
SET NAMES utf8mb4;

INSERT INTO author (author_id, name, country, photo) VALUES
(1, 'Naguib Mahfouz', 'Egypt', '305a3a50081848ce8f150260dd50ba3a.jpg'),
(2, 'Agatha Christie', 'United Kingdom', 'a35e62389c614877826f2b22aa09050c.jpg'),
(3, 'Gabriel Garcia Marquez', 'Colombia', 'f840183ee1c741828a0dd4c27ffd8232.jpg'),
(4, 'Haruki Murakami', 'Japan', '24c1da0dc10a43818ed7851d502d220b.webp'),
(5, 'Taha Hussein', 'Egypt', '1d350ce80d5248b4bb78ec78b4310423.jpg'),
(6, 'Stephen Hawking', 'United Kingdom', 'f2691120130641a4846456f340764ebb.webp'),
(7, 'Carl Sagan', 'USA', '03300584e335413c98fedcc01627ad4b.webp');

INSERT INTO publisher (publisher_id, name, country) VALUES
(1, 'Dar El Shorouk', 'Egypt'),
(2, 'Penguin Books', 'United Kingdom'),
(3, 'Shinchosha', 'Japan'),
(4, 'Bantam Books', 'USA'),
(5, 'Random House', 'USA');

INSERT INTO category (category_id, name) VALUES
(1, 'Literary Fiction'), (2, 'Mystery'), (3, 'Magical Realism'),
(4, 'Science');

INSERT INTO book (book_id, title, price, publish_year, author_id, publisher_id, category_id, cover) VALUES
(1, 'Palace Walk', 18.50, 1956, 1, 1, 1, '3cf343a8a9d34b9d8ad35d76337d02cc.jpg'),
(2, 'Children of the Alley', 15.00, 1959, 1, 1, 1, 'c86c2ac1e6e048469ca68814f2f8ca03.jpg'),
(3, 'Midaq Alley', 12.75, 1947, 1, 1, 1, 'c2222e400a7643e3b55cd77edba3b533.webp'),
(4, 'Murder on the Orient Express', 10.99, 1934, 2, 2, 2, 'd93d05436d47465a8353ef5ef101814e.jpg'),
(5, 'And Then There Were None', 9.50, 1939, 2, 2, 2, 'd9b64ea4200b4dd7be5c34fb5db019da.jpg'),
(6, 'One Hundred Years of Solitude', 16.00, 1967, 3, 2, 3, 'f4f2dd13936d4dac8f5e627355a3c98a.jpg'),
(7, 'Love in the Time of Cholera', 14.25, 1985, 3, 2, 1, '9c4393991dd146b0b19bf9bbf2e476ca.jpg'),
(8, 'Norwegian Wood', 13.40, 1987, 4, 3, 1, '502410488bf74e12ba03a1c233726fba.webp'),
(9, 'Kafka on the Shore', 17.20, 2002, 4, 3, 3, '07365c325a9546a1bd454f8f31af2d20.jpg'),
(10, 'The ABC Murders', 20.00, 1936, 2, 2, 2, '20f3c0d79c7446619a345e7e54c8a2c5.jpg'),
(11, 'A Brief History of Time', 22.50, 1988, 6, 4, 4, '9e0b9c65a2fd41d2801178e6ef8853fc.webp'),
(12, 'The Universe in a Nutshell', 24.00, 2001, 6, 4, 4, 'eff53ff4835e4d3082720155dadbc4f7.jpg'),
(13, 'Cosmos', 19.90, 1980, 7, 5, 4, '5d050e94864d48979a0ce9698d4c4129.jpg');

INSERT INTO member (member_id, name, email, join_date) VALUES
(1, 'Ahmed Ali', 'ahmed@example.com', '2026-01-10'),
(2, 'Sara Hassan', 'sara@example.com', '2026-02-15'),
(3, 'Omar Adel', 'omar@example.com', '2026-03-01'),
(4, 'Mona Samir', 'mona@example.com', '2026-03-12'),
(5, 'Youssef Mostafa', 'youssef@example.com', '2026-04-01');

INSERT INTO loan (loan_id, book_id, member_id, loan_date, return_date) VALUES
(1, 1, 1, '2026-05-01', '2026-05-15'),
(2, 1, 2, '2026-06-01', '2026-06-10'),
(3, 1, 1, '2026-07-01', '2026-07-15'),
(4, 1, 3, '2026-11-01', NULL),
(5, 4, 1, '2026-05-03', '2026-05-14'),
(6, 4, 2, '2026-08-01', '2026-08-11'),
(7, 4, 4, '2026-11-02', NULL),
(8, 6, 1, '2026-06-05', '2026-06-20'),
(9, 6, 3, '2026-09-01', '2026-09-15'),
(10, 2, 2, '2026-09-20', '2026-09-30'),
(11, 3, 4, '2026-10-01', '2026-10-14'),
(12, 8, 1, '2026-11-03', NULL);
