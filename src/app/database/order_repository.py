from database.connection import DatabaseError, fetch_all, fetch_one, run_in_transaction

CLIENT_NAME_SQL = "COALESCE(u.last_name || ' ' || u.first_name || COALESCE(' ' || u.middle_name, ''), 'Неизвестный клиент')"


def get_orders():
    return fetch_all(
        f"""
        SELECT o.order_number AS order_id, o.order_date, {CLIENT_NAME_SQL} AS client_name,
               COALESCE(SUM(o.quantity * o.unit_price), 0) AS total_sum
        FROM orders o
        LEFT JOIN users u ON u.user_id = o.user_id
        GROUP BY o.order_number, o.order_date, u.user_id, u.last_name, u.first_name, u.middle_name
        ORDER BY o.order_date DESC, o.order_number DESC
        """
    )


def get_order(order_number):
    return fetch_one(
        f"""
        SELECT o.order_number AS order_id, o.order_date, {CLIENT_NAME_SQL} AS client_name
        FROM orders o
        LEFT JOIN users u ON u.user_id = o.user_id
        WHERE o.order_number = %s
        LIMIT 1
        """,
        (order_number,),
    )


def get_order_items(order_number):
    return fetch_all(
        """
        SELECT o.order_id AS order_item_id, p.product_name, p.production, v.variant_name,
               o.quantity, o.unit_price AS price
        FROM orders o
        JOIN products p ON p.product_id = o.product_id
        JOIN variants v ON v.variant_id = o.variant_id
        WHERE o.order_number = %s
        ORDER BY o.order_id
        """,
        (order_number,),
    )


def create_order(user_id, cart_items):
    def action(cursor):
        cursor.execute("SELECT COALESCE(MAX(order_number), 0) + 1 AS next_num FROM orders")
        order_number = cursor.fetchone()["next_num"]
        
        for item in cart_items:
            cursor.execute(
                """
                UPDATE stock_items
                SET stock_quantity = stock_quantity - %s
                WHERE product_id = %s AND variant_id = %s AND stock_quantity >= %s
                """,
                (item["quantity"], item["product_id"], item["variant_id"], item["quantity"]),
            )
            if cursor.rowcount == 0:
                raise DatabaseError(
                    f"Недостаточно товара «{item['product_name']}» ({item['variant_text']}) на складе."
                )

            cursor.execute(
                """
                INSERT INTO orders (order_number, order_date, user_id, product_id, variant_id, quantity, unit_price)
                VALUES (%s, CURRENT_DATE, %s, %s, %s, %s, %s)
                """,
                (
                    order_number, user_id, item["product_id"], 
                    item["variant_id"], item["quantity"], item["price"]
                )
            )
        return order_number

    return run_in_transaction(action)


def delete_order(order_number):
    def action(cursor):
        cursor.execute(
            """
            UPDATE stock_items st
            SET stock_quantity = st.stock_quantity + o.quantity
            FROM orders o
            WHERE st.product_id = o.product_id
              AND st.variant_id = o.variant_id
              AND o.order_number = %s
            """,
            (order_number,),
        )
        cursor.execute("DELETE FROM orders WHERE order_number = %s", (order_number,))
        if cursor.rowcount == 0:
            raise DatabaseError("Заказ не найден.")

    run_in_transaction(action)


def update_order(order_number, new_date, removed_item_ids):
    def action(cursor):
        if removed_item_ids:
            for item_id in removed_item_ids:
                cursor.execute(
                    """
                    UPDATE stock_items st
                    SET stock_quantity = st.stock_quantity + o.quantity
                    FROM orders o
                    WHERE st.product_id = o.product_id
                      AND st.variant_id = o.variant_id
                      AND o.order_id = %s
                    """,
                    (item_id,),
                )
                cursor.execute("DELETE FROM orders WHERE order_id = %s", (item_id,))
        
        cursor.execute("UPDATE orders SET order_date = %s WHERE order_number = %s", (new_date, order_number))

    run_in_transaction(action)