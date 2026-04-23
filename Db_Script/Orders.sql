
DECLARE order_count NUMBER;

BEGIN
    SELECT COUNT(*) INTO order_count FROM USER_TABLES
        WHERE TABLE_NAME = 'ORDERS';

    IF order_count = 0
        THEN

        EXECUTE IMMEDIATE 'CREATE TABLE ORDERS(
        order_id NUMBER GENERATED ALWAYS AS IDENTITY (NOCACHE) PRIMARY KEY ,
        customer_name VARCHAR2(40) NOT NULL ,
        customer_number VARCHAR2(13) NOT NULL ,
        customer_city VARCHAR2(100) NOT NULL ,
        customer_address VARCHAR2(200) NOT NULL ,
        customer_bill NUMBER NOT NULL ,
        order_status VARCHAR2(40) DEFAULT ''PENDING'' NOT NULL ,
        order_date DATE DEFAULT TRUNC(SYSDATE)
        )';
    ELSE
        DBMS_OUTPUT.PUT_LINE('TABLE ORDERS ALREADY EXISTS!');

    END IF;
END;

CREATE OR REPLACE PROCEDURE p_add_order(

    p_name IN VARCHAR2,
    p_number IN VARCHAR2,
    p_city IN VARCHAR2,
    p_address IN VARCHAR2,
    p_bill IN NUMBER,
    p_order_id OUT NUMBER
)
AS BEGIN
    INSERT INTO ORDERS(customer_name, customer_number, customer_city, customer_address, customer_bill)
    VALUES (p_name, p_number,
            p_city, p_address, p_bill
            )
            RETURNING ORDER_ID INTO p_order_id;

    COMMIT ;
END;

CREATE OR REPLACE PROCEDURE p_display_orders(

    ref_cur OUT SYS_REFCURSOR
)
AS BEGIN
    OPEN ref_cur FOR
        SELECT CUSTOMER_NAME, CUSTOMER_NUMBER, CUSTOMER_CITY, CUSTOMER_ADDRESS, CUSTOMER_BILL,
               TO_CHAR(ORDER_DATE, 'DD-MM_YYYY'), ORDER_ID
            FROM ORDERS;

END;

CREATE OR REPLACE PROCEDURE p_display_order(p_order_id IN VARCHAR2)
    AS
    p_order SYS_REFCURSOR;

    BEGIN
    OPEN p_order FOR
        SELECT CUSTOMER_NAME, CUSTOMER_NUMBER, CUSTOMER_CITY, CUSTOMER_ADDRESS, CUSTOMER_BILL,
               TO_CHAR(ORDER_DATE, 'DD-MM_YYYY'), ORDER_ID
            FROM ORDERS
                WHERE ORDER_ID = p_order_id;

    DBMS_SQL.RETURN_RESULT(p_order);

end;

CREATE OR REPLACE PROCEDURE p_verify_order(p_order_id IN NUMBER)
AS
    result_cur SYS_REFCURSOR;
BEGIN
    OPEN result_cur FOR
        SELECT ORDER_ID FROM ORDERS
            WHERE ORDER_ID = p_order_id;

    DBMS_SQL.RETURN_RESULT(result_cur);

end;


CREATE OR REPLACE PROCEDURE p_delete_order(p_order_id IN NUMBER)
AS
    BEGIN
        DELETE FROM ORDERS
               WHERE ORDER_ID = p_order_id;

        COMMIT ;
    end;

CREATE OR REPLACE PROCEDURE p_update_order_status(p_order_id IN NUMBER, new_status IN VARCHAR2)
AS
BEGIN
    update ORDERS
    set ORDER_STATUS = new_status
    WHERE ORDER_ID = p_order_id;

    COMMIT ;
END;

CREATE OR REPLACE PROCEDURE p_display_orders_admin
AS
    ref_cur SYS_REFCURSOR;

BEGIN
   OPEN ref_cur FOR
       SELECT O.ORDER_ID, O.CUSTOMER_NAME, O.CUSTOMER_NUMBER, O.CUSTOMER_CITY, O.CUSTOMER_ADDRESS, O.CUSTOMER_BILL,
               TO_CHAR(ORDER_DATE, 'DD-MM-YYYY'), O.ORDER_STATUS,

               JSON_ARRAYAGG(
               JSON_OBJECT(
                'product_id' VALUE I.product_id,
                'product_name' VALUE I.product_name,
                'product_retail' VALUE I.product_retail,
                'product_link' VALUE I.product_link,
                'product_image' VALUE I.PRODUCT_IMAGE,
                'qty' VALUE oi.quantity)
               )

       FROM ORDERS O inner join ORDER_ITEMS OI ON O.ORDER_ID = OI.ORDER_ID
        INNER JOIN INVENTORY I ON I.PRODUCT_ID = OI.PRODUCT_ID

       GROUP BY O.ORDER_ID, O.CUSTOMER_NAME, O.CUSTOMER_NUMBER, O.CUSTOMER_CITY, O.CUSTOMER_ADDRESS, O.CUSTOMER_BILL,
               TO_CHAR(ORDER_DATE, 'DD-MM-YYYY'), O.ORDER_STATUS;

    DBMS_SQL.RETURN_RESULT(ref_cur);

end;


select PRODUCT_ID, PRODUCT_DESCRIPTION from  INVENTORY;

update INVENTORY
set PRODUCT_DESCRIPTION = 'Durable Quality With Dependable Build Elegant Motivational Quotes Design

Comfortable Use With Compact

Size 8x11

Reliable Utility For Wall Decoration

Includes Double Tape For Easy Mounting

Suitable For Household Inspiration And Decoration Needs Thickness 2mm'
where PRODUCT_ID = 8 and PRODUCT_ID = 6;

commit ;