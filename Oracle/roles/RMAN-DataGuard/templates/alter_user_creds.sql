ALTER DATABASE OPEN;
ALTER USER sys IDENTIFIED BY {{ target_db_password }}; 
exit;
