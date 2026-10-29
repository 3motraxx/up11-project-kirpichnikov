from database.connection import DatabaseError, fetch_all, fetch_one, run_in_transaction


def get_orders():
    return fetch_all(
        """
        SELECT o.order_id, o.order_date, o.customer_fio AS client_name,
               COALESCE(SUM(o.quantity * o.unit_price), 0) AS total_sum
        FROM orders o
        GROUP BY o.order_id, o.order_date, o.customer_fio
        ORDER BY o.order_date DESC, o.order_id DESC
        """
    )


def get_order(order_id):
    return fetch_one(
        """
        SELECT o.order_id, o.order_date, o.customer_fio AS client_name
        FROM orders o
        WHERE o.order_id = %s
        """,
        (order_id,),
    )


def get_order_items(order_id):
    return fetch_all(
        """
        SELECT o.order_id AS order_item_id, o.product_name_raw AS product_name, 
               o.production, o.variant_name_raw AS variant_name,
               o.quantity, o.unit_price AS price
        FROM orders o
        WHERE o.order_number = (SELECT order_number FROM orders WHERE order_id = %s)
        ORDER BY o.order_id
        """,
        (order_id,),
    )


def create_order(user_id, cart_items):
    def action(cursor):
        cursor.execute("SELECT COALESCE(MAX(order_number), 0) + 1 AS next_num FROM orders")
        order_number = cursor.fetchone()["next_num"]
        
        # Получаем ФИО текущего пользователя
        cursor.execute("SELECT last_name, first_name, middle_name FROM users WHERE user_id = %s", (user_id,))
        u_data = cursor.fetchone()
        fio = f"{u_data['last_name']} {u_data['first_name']}"
        if u_data.get('middle_name'):
            fio += f" {u_data['middle_name']}"

        for item in cart_items:
            cursor.execute(
                """
                UPDATE stock_items
                SET stock_quantity = stock_quantity - %s
                WHERE product_name_raw = %s AND production = %s AND variant_name_raw = %s AND stock_quantity >= %s
                """,
                (item["quantity"], item["product_name"], item["production"], item["variant_text"], item["quantity"]),
            )
            if cursor.rowcount == 0:
                raise DatabaseError(
                    f"Недостаточно товара «{item['product_name']}» (вариант: {item['variant_text']}) на складе.\n"
                    "Уменьшите количество в заказе и попробуйте снова."
                )

            cursor.execute(
                """
                INSERT INTO orders (order_number, order_date, customer_fio, category, product_name_raw, production, variant_name_raw, quantity, unit_price)
                VALUES (%s, CURRENT_DATE, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    order_number, fio, item["category"], item["product_name"], 
                    item["production"], item["variant_text"], item["quantity"], 
                    item["price"]
                )
            )
        return order_number

    return run_in_transaction(action)


def delete_order(order_id):
    def action(cursor):
        cursor.execute(
            """
            UPDATE stock_items st
            SET stock_quantity = st.stock_quantity + o.quantity
            FROM orders o
            WHERE st.product_name_raw = o.product_name_raw 
              AND st.production = o.production 
              AND st.variant_name_raw = o.variant_name_raw
              AND o.order_id = %s
            """,
            (order_id,),
        )
        cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
        if cursor.rowcount == 0:
            raise DatabaseError("Заказ не найден. Возможно, он уже удалён.")

    run_in_transaction(action)


def update_order(order_id, new_date, removed_item_ids):
    def action(cursor):
        cursor.execute("UPDATE orders SET order_date = %s WHERE order_id = %s", (new_date, order_id))

    run_in_transaction(action)