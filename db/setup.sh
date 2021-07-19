[ -f mt.db ] && rm mt.db

sqlite3 mt.db < schema.sqlite3;
