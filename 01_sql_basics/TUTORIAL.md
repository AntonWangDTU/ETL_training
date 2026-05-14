#h Tutorial — SQL Basics

This covers the concepts you need for the assignments. Examples below use a generic `products` / `orders` schema so they don't give away the answers. Read top to bottom, then open `assignment.sql`.

---
## The database you're working with

The `ibis.db` SQLite database models a research programme that tests bacterial strains on crops:

```
strains      — the bacteria being tested
sites        — field locations around the world
researchers  — the scientists running experiments
experiments  — one strain applied to one crop at one site (strain_id is NULL for controls)
measurements — plant readings taken during an experiment
```

---

## 1. SELECT

Retrieve all columns:

```sql
SELECT * FROM products;
```

Retrieve specific columns:

```sql
SELECT name, price FROM products;
```

Prefer naming columns over `SELECT *` — it makes queries easier to read and faster on large tables.

---

## 2. WHERE — filtering rows

```sql
SELECT * FROM products WHERE category = 'electronics';
SELECT * FROM orders  WHERE quantity > 10;
```

Common operators: `=`, `!=`, `<`, `>`, `<=`, `>=`, `IS NULL`, `IS NOT NULL`, `IN (...)`, `LIKE 'prefix%'`.

Combine conditions with `AND` / `OR`:

```sql
SELECT * FROM orders WHERE status = 'shipped' AND quantity > 5;
```

Filtering NULLs requires `IS NULL`, not `= NULL`:

```sql
SELECT * FROM orders WHERE discount IS NOT NULL;
```

---

## 3. ORDER BY — sorting

```sql
SELECT * FROM products ORDER BY price DESC;   -- highest first
SELECT * FROM products ORDER BY name ASC;     -- alphabetical (default)
```

---

## 4. Aggregation — COUNT, AVG, SUM, MIN, MAX

These collapse many rows into a single number:

```sql
SELECT COUNT(*)        AS total_orders  FROM orders;
SELECT AVG(price)      AS avg_price     FROM products;
SELECT MAX(quantity)   AS largest_order FROM orders;
```

`COUNT(*)` counts rows. `COUNT(column)` counts non-NULL values in that column — the difference matters when a column has NULLs.

---

## 5. GROUP BY — aggregate per group

Without `GROUP BY`, an aggregate gives one result for the whole table. With it, you get one result per group:

```sql
SELECT category, COUNT(*) AS product_count
FROM products
GROUP BY category;
```

**Rule:** every column in `SELECT` must either appear in `GROUP BY` or be wrapped in an aggregate function (`COUNT`, `AVG`, etc.).

---

## 6. HAVING — filtering groups

`WHERE` filters rows before grouping. `HAVING` filters groups after aggregation:

```sql
-- only categories with more than 5 products
SELECT category, COUNT(*) AS product_count
FROM products
GROUP BY category
HAVING COUNT(*) > 5;
```

The mental split: `WHERE` = "filter the raw rows", `HAVING` = "filter the grouped summary".

---

## 7. JOINs — combining tables

### INNER JOIN

Returns only rows where the join condition matches in **both** tables:

```sql
SELECT orders.id, customers.name
FROM orders
JOIN customers ON orders.customer_id = customers.id;
```

If a customer has no orders, they won't appear. If an order has no matching customer, it won't appear either.

Aliases shorten table names:

```sql
SELECT o.id, c.name
FROM orders o
JOIN customers c ON o.customer_id = c.id;
```

### LEFT JOIN

Returns **all** rows from the left table, even with no match on the right. Unmatched right-side columns are NULL:

```sql
SELECT c.name, o.id AS order_id
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id;
```

Customers with no orders still appear — `order_id` is NULL for them.

**When to use LEFT JOIN:** whenever you want to keep rows from the left table even if the relationship is optional. In `ibis.db`, control experiments have no strain — an INNER JOIN on strains would silently drop them.

### Joining more than two tables

Chain joins one at a time:

```sql
SELECT o.id, c.name, p.name AS product
FROM orders o
JOIN customers c ON o.customer_id = c.id
JOIN products  p ON o.product_id  = p.id;
```

### COALESCE — replacing NULLs in output

```sql
SELECT name, COALESCE(discount, 0) AS discount
FROM products;
```

`COALESCE(a, b)` returns `a` if it's not NULL, otherwise `b`. Useful for making NULL values readable in output.

---

## 8. Query execution order (mental model)

SQL runs in this order regardless of how you write it:

```
FROM / JOIN  →  WHERE  →  GROUP BY  →  HAVING  →  SELECT  →  ORDER BY
```

This explains two common surprises:
- You can't use a `SELECT` alias in a `WHERE` clause — the alias doesn't exist yet.
- `HAVING` can filter on an aggregate but `WHERE` cannot.

---

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `SELECT category, COUNT(*) FROM products` with no `GROUP BY` | Add `GROUP BY category` |
| Filtering an aggregate with `WHERE` | Use `HAVING` instead |
| Losing NULL-valued rows after a JOIN | Switch to `LEFT JOIN` |
| `WHERE col = NULL` never matches | Use `WHERE col IS NULL` |

---

Now open `assignment.sql`.
