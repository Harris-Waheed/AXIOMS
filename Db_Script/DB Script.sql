
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
        order_date DATE DEFAULT TRUNC(SYSDATE),
        product_id NUMBER NOT NULL ,
        FOREIGN KEY (product_id) REFERENCES INVENTORY(product_id)
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
    p_product_id IN NUMBER,
    p_order_id OUT NUMBER
)
AS BEGIN
    INSERT INTO ORDERS(customer_name, customer_number, customer_city, customer_address, customer_bill, product_id)
    VALUES (p_name, p_number,
            p_city, p_address, p_bill, p_product_id)
            RETURNING ORDER_ID INTO p_order_id;

    COMMIT ;
END;

CREATE OR REPLACE PROCEDURE p_display_orders(

    ref_cur OUT SYS_REFCURSOR
)
AS BEGIN
    OPEN ref_cur FOR
        SELECT CUSTOMER_NAME, CUSTOMER_NUMBER, CUSTOMER_CITY, CUSTOMER_ADDRESS, CUSTOMER_BILL,
               TO_CHAR(ORDER_DATE, 'DD-MM_YYYY'), PRODUCT_ID, ORDER_ID
            FROM ORDERS;

END;

CREATE OR REPLACE PROCEDURE p_display_order(

    p_order_id IN VARCHAR2,
    p_order OUT SYS_REFCURSOR
)
AS BEGIN
    OPEN p_order FOR
        SELECT CUSTOMER_NAME, CUSTOMER_NUMBER, CUSTOMER_CITY, CUSTOMER_ADDRESS, CUSTOMER_BILL,
               TO_CHAR(ORDER_DATE, 'DD-MM_YYYY'), PRODUCT_ID, ORDER_ID
            FROM ORDERS
                WHERE ORDER_ID = p_order_id;

end;

DECLARE inventory_count NUMBER;

BEGIN
   SELECT COUNT(*) INTO inventory_count
    FROM USER_TABLES WHERE TABLE_NAME = 'INVENTORY';

   IF inventory_count = 0
       THEN
       EXECUTE IMMEDIATE 'CREATE TABLE INVENTORY(
        product_id NUMBER GENERATED ALWAYS AS IDENTITY (NOCACHE) PRIMARY KEY ,
        product_name VARCHAR2(100) NOT NULL ,
        product_description varchar2(1000),
        product_wholesale NUMBER NOT NULL ,
        product_retail NUMBER NOT NULL ,
        product_image VARCHAR2(200),
        created_at DATE DEFAULT TRUNC(SYSDATE) NOT NULL

                          )';
       ELSE
            DBMS_OUTPUT.PUT_LINE('Table Inventory Already Exists!');
   END IF;
END;

CREATE OR REPLACE PROCEDURE p_add_inventory(

    p_product_name IN VARCHAR2,
    p_product_description IN VARCHAR2,
    p_product_wholesale IN NUMBER,
    p_product_retail IN NUMBER,
    p_product_image IN VARCHAR2
)
AS BEGIN

    INSERT INTO INVENTORY(PRODUCT_NAME, PRODUCT_DESCRIPTION, PRODUCT_WHOLESALE, PRODUCT_RETAIL, PRODUCT_IMAGE)
    VALUES(p_product_name, p_product_description,
           p_product_wholesale, p_product_retail, p_product_image);

    COMMIT ;
end;

CREATE OR REPLACE PROCEDURE p_display_inventory(

    ref_cur OUT SYS_REFCURSOR
)
AS BEGIN
    OPEN ref_cur FOR
        SELECT PRODUCT_ID, PRODUCT_NAME, PRODUCT_DESCRIPTION, PRODUCT_WHOLESALE,
        PRODUCT_RETAIL, PRODUCT_IMAGE
        FROM INVENTORY;

end;

CREATE OR REPLACE PROCEDURE p_display_product(

    p_product_id IN NUMBER,
    p_product OUT SYS_REFCURSOR
)
AS BEGIN
    OPEN p_product FOR
        SELECT PRODUCT_ID, PRODUCT_NAME, PRODUCT_DESCRIPTION, PRODUCT_WHOLESALE, PRODUCT_RETAIL, PRODUCT_IMAGE
            FROM INVENTORY
                WHERE PRODUCT_ID = p_product_id;

end;
