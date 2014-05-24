lamPy
=====

Linux Apache MySQL Python

 * To install run
   'make'
 * Make sure that the web user has access to edit
   '.htaccess'
 * Then navigate to
   'yoursite/setup.py'


To connect to SQL

  * Edit 'conf/db.conf'
    define source as 'sqlite" or "mysql"
    define values needed for connect
      pymysql.connect
      sqlite3.connect
  * Usernames and passwords for configuration files belong in 'conf/*.conf.private' and are ignored by default by git

Preprocessing Macros
  * General macros are defined in the pypp documentation
  * Additionally the following functions (#call) are defined
    execute name args - preprocesses a sql script in 'sql/<name>.sql' and then formats them using args, and then executes it
    query name args - same as execute, except it returns the result of the query
    queryRow name args - same as query, execpt it returns only the first row
    queryScalar name args - same as query, except it returns only the first result of the first row
  * To add additional functions, add them to html.values in webapp.py

