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
        category VARCHAR2(200) NOT NULL,
        PRODUCT_LINK VARCHAR2(500),
        status VARCHAR2(40) DEFAULT ''ACTIVE'' NOT NULL ,
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
    p_product_image IN VARCHAR2,
    p_product_link IN VARCHAR2,
    p_product_category IN VARCHAR2

)
AS BEGIN

    INSERT INTO INVENTORY(PRODUCT_NAME, PRODUCT_DESCRIPTION, PRODUCT_WHOLESALE, PRODUCT_RETAIL, PRODUCT_IMAGE,
                          PRODUCT_LINK, CATEGORY)
    VALUES(p_product_name, p_product_description,
           p_product_wholesale, p_product_retail, p_product_image,
           p_product_link, p_product_category);

    COMMIT ;
end;

CREATE OR REPLACE PROCEDURE p_display_inventory(

    ref_cur OUT SYS_REFCURSOR
)
AS BEGIN
    OPEN ref_cur FOR
        SELECT PRODUCT_ID, PRODUCT_NAME, PRODUCT_DESCRIPTION, PRODUCT_WHOLESALE,
        PRODUCT_RETAIL, PRODUCT_IMAGE, PRODUCT_LINK, CATEGORY, STATUS
        FROM INVENTORY;

end;

CREATE OR REPLACE PROCEDURE p_display_product(p_product_id IN NUMBER)
    AS
    p_product SYS_REFCURSOR;
    BEGIN
    OPEN p_product FOR
        SELECT PRODUCT_ID, PRODUCT_NAME, PRODUCT_DESCRIPTION, PRODUCT_WHOLESALE, PRODUCT_RETAIL, PRODUCT_IMAGE,
               PRODUCT_LINK, CATEGORY, STATUS
            FROM INVENTORY
                WHERE PRODUCT_ID = p_product_id;

    DBMS_SQL.RETURN_RESULT(p_product);

end;

CREATE OR REPLACE PROCEDURE p_verify_product(p_product_id IN NUMBER)
AS
    result_cur SYS_REFCURSOR;
BEGIN
    OPEN result_cur FOR
        SELECT PRODUCT_ID FROM INVENTORY
            WHERE PRODUCT_ID = p_product_id;

   DBMS_SQL.RETURN_RESULT(result_cur);
end;

CREATE OR REPLACE PROCEDURE p_delete_product(p_product_id IN NUMBER)
AS
    BEGIN
        DELETE FROM INVENTORY
               WHERE PRODUCT_ID = p_product_id;

        COMMIT ;
    end;

CREATE OR REPLACE PROCEDURE p_update_product_status(p_product_id IN NUMBER, new_status IN VARCHAR2)
AS
BEGIN
    update INVENTORY
    set STATUS = new_status
    WHERE PRODUCT_ID = p_product_id;

    COMMIT ;
END;

select * from INVENTORY;

