# Tutorial — SQL Intermediate

This covers CTEs, window functions, subqueries, and data quality checks. Examples use a generic schema — not the assignment questions. Read top to bottom, then open `assignment.sql`.

---

## 1. CTEs — Common Table Expressions

A CTE is a named subquery you write once and reference like a table. It lives only for the duration of the query.

```sql
WITH active_customers AS (
    SELECT id, name, city
    FROM customers
    WHERE status = 'active'
)
SELECT city, COUNT(*) AS active_count
FROM active_customers
GROUP BY city;
```

**Why use a CTE instead of a subquery?**
- You can give it a meaningful name, making the query self-documenting.
- You can reference it multiple times in the same query.
- It's easier to debug: comment out the final SELECT and just `SELECT * FROM the_cte` to inspect what it produces.

### Chaining CTEs

You can define multiple CTEs, each building on the previous:

```sql
WITH monthly_sales AS (
    SELECT
        strftime('%Y-%m', order_date) AS month,
        SUM(amount) AS total
    FROM orders
    GROUP BY month
),
avg_sales AS (
    SELECT AVG(total) AS overall_avg FROM monthly_sales
)
SELECT month, total, overall_avg
FROM monthly_sales, avg_sales
WHERE total > overall_avg;
```

---

## 2. Window Functions

Window functions compute a value for each row **using a set of related rows**, without collapsing them into a single output row. This is the key difference from `GROUP BY`.

```sql
SELECT
    department,
    employee,
    salary,
    AVG(salary) OVER (PARTITION BY department) AS dept_avg
FROM employees;
```

Every employee row is kept. The `dept_avg` column shows the average for that employee's department.

### PARTITION BY and ORDER BY

- `PARTITION BY` divides rows into groups (like `GROUP BY`, but rows aren't collapsed).
- `ORDER BY` inside `OVER (...)` defines the ordering within each partition — required for ranking and lag functions.

```sql
AVG(salary)  OVER (PARTITION BY department)                        -- avg per department
RANK()       OVER (PARTITION BY department ORDER BY salary DESC)   -- rank within department
LAG(salary)  OVER (PARTITION BY department ORDER BY hire_date)     -- previous row's salary
```

### RANK()

Assigns a rank within each partition, starting at 1. Ties get the same rank, and the next rank is skipped:

```sql
SELECT
    country,
    city,
    population,
    RANK() OVER (PARTITION BY country ORDER BY population DESC) AS rank_in_country
FROM cities;
```

### LAG() and LEAD()

`LAG(col)` returns the value from the **previous** row in the partition. `LEAD(col)` returns the value from the **next** row. Both return NULL at the boundary.

```sql
SELECT
    account_id,
    transaction_date,
    amount,
    LAG(amount) OVER (PARTITION BY account_id ORDER BY transaction_date) AS prev_amount,
    amount - LAG(amount) OVER (PARTITION BY account_id ORDER BY transaction_date) AS change
FROM transactions;
```

### MAX() / MIN() OVER

Aggregate window functions let you compare each row to a group-level value:

```sql
SELECT
    product,
    category,
    price,
    MAX(price) OVER (PARTITION BY category) AS category_max,
    ROUND(100.0 * price / MAX(price) OVER (PARTITION BY category), 1) AS pct_of_max
FROM products;
```

---

## 3. Subqueries

A subquery is a query nested inside another query.

### Subquery in WHERE with IN

```sql
-- orders placed by customers in Germany
SELECT * FROM orders
WHERE customer_id IN (
    SELECT id FROM customers WHERE country = 'Germany'
);
```

### NOT IN subquery

```sql
-- products that have never been ordered
SELECT * FROM products
WHERE id NOT IN (
    SELECT DISTINCT product_id FROM order_lines
);
```

**Caution with NOT IN and NULLs:** if the subquery returns any NULL values, `NOT IN` will match nothing. Use `NOT EXISTS` if there's any chance of NULLs in the inner query.

### EXISTS / NOT EXISTS

More reliable than `NOT IN` when NULLs are possible:

```sql
SELECT * FROM products p
WHERE NOT EXISTS (
    SELECT 1 FROM order_lines ol WHERE ol.product_id = p.id
);
```

### Scalar subquery (single value)

A subquery that returns exactly one row and one column can be used like a value:

```sql
SELECT name, salary,
       (SELECT AVG(salary) FROM employees) AS company_avg
FROM employees;
```

### Subquery vs CTE

Both work; CTEs are generally easier to read when the subquery is complex or reused. Subqueries are fine for simple, one-off filters.

---

## 4. Data Quality Checks

Before loading external data you need to verify it doesn't violate your database's rules. These are standard patterns.

### Referential integrity — does a foreign key point to something real?

```sql
-- orders referencing a customer that doesn't exist
SELECT order_id, 'bad customer_id' AS issue
FROM orders
WHERE customer_id NOT IN (SELECT id FROM customers);
```

### Out-of-range values

```sql
SELECT * FROM measurements
WHERE temperature_c < -90     -- colder than anywhere on Earth
   OR temperature_c > 60;
```

### Duplicates

```sql
SELECT email, COUNT(*) AS count
FROM users
GROUP BY email
HAVING COUNT(*) > 1;
```

### Rows that should have data but don't

```sql
-- users who registered but never placed an order
SELECT u.id, u.email
FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);
```

---

## Putting it together

Real analytical queries often combine all of the above:

```sql
WITH regional_totals AS (
    SELECT
        c.region,
        SUM(o.amount) AS total_sales
    FROM orders o
    JOIN customers c ON o.customer_id = c.id
    GROUP BY c.region
)
SELECT
    region,
    total_sales,
    RANK() OVER (ORDER BY total_sales DESC) AS rank,
    ROUND(100.0 * total_sales / SUM(total_sales) OVER (), 1) AS pct_of_all
FROM regional_totals
ORDER BY rank;
```

---

Now open `assignment.sql`.
