from app.database.init_db import init_db
from config import Config

print(Config.DEFAULT_DB_NAME)
# create the new database and tables
init_db(Config.DEFAULT_DB_NAME,Config.DB_NAME,'app/database/init_db/create_tables.sql','app/database/init_db/test_data.sql')