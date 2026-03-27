
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