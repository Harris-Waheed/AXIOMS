DECLARE item_table_count NUMBER;
BEGIN
    SELECT COUNT(*) INTO item_table_count FROM USER_TABLES
    WHERE TABLE_NAME = 'ORDER_ITEMS';

    IF item_table_count = 0 THEN
        EXECUTE IMMEDIATE 'CREATE TABLE ORDER_ITEMS(
            order_item_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            order_id NUMBER NOT NULL,
            product_id NUMBER NOT NULL,
            quantity NUMBER NOT NULL,

            CONSTRAINT fk_order FOREIGN KEY (order_id) REFERENCES ORDERS(order_id) ON DELETE CASCADE,
            CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES INVENTORY(product_id)
        )';
    ELSE
        DBMS_OUTPUT.PUT_LINE('TABLE ORDER_ITEMS ALREADY EXISTS!');
    END IF;
END;

CREATE OR REPLACE PROCEDURE p_add_order_item(
    p_order_id IN NUMBER,
    p_product_id IN NUMBER,
    p_quantity IN NUMBER
) AS
BEGIN
    INSERT INTO ORDER_ITEMS (order_id, product_id, quantity)
    VALUES (p_order_id, p_product_id, p_quantity);

    COMMIT ;
END;

select PRODUCT_ID from INVENTORY;