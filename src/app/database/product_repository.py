from database.connection import fetch_all


def get_products():
    return fetch_all(
        """
        SELECT p.product_id, p.category, p.subcategory, p.product_name, p.production,
               p.description, p.composition, p.image_url AS image_path, p.base_price AS price,
               COALESCE(SUM(s.stock_quantity), 0) AS total_quantity
        FROM products p
        LEFT JOIN stock_items s 
          ON s.product_name_raw = p.product_name 
         AND s.production = p.production
        GROUP BY p.product_id
        ORDER BY p.product_id
        """
    )


def get_categories():
    rows = fetch_all("SELECT DISTINCT category FROM products ORDER BY category")
    return [row["category"] for row in rows]


def get_product_variants(product_id):
    return fetch_all(
        """
        SELECT v.variant_id, v.variant_name, st.stock_quantity AS quantity_available, st.variant_price
        FROM stock_items st
        JOIN products p ON p.product_name = st.product_name_raw AND p.production = st.production
        JOIN variants v ON v.variant_name = st.variant_name_raw
        WHERE p.product_id = %s
        ORDER BY v.variant_name
        """,
        (product_id,),
    )


def get_ordered_product_ids(period_start, period_end):
    rows = fetch_all(
        """
        SELECT DISTINCT p.product_id
        FROM orders o
        JOIN products p ON p.product_name = o.product_name_raw AND p.production = o.production
        WHERE o.order_date >= %s AND o.order_date < %s
        """,
        (period_start, period_end),
    )
    return {row["product_id"] for row in rows}