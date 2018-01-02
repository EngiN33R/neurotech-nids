import psycopg2
import psycopg2.extras
import datetime

conn = psycopg2.connect(
    "dbname=neurotech user=neurotech password=neurotech host=127.0.0.1")
cur = conn.cursor()
psycopg2.extras.register_composite('neurotech.packet', cur)

cur.execute("SELECT * FROM neurotech.packets;")
print(cur.fetchone())

cur.execute("INSERT INTO packets (packet, label) VALUES (%s, %s)",
            ((datetime.datetime.utcnow(), 9.004991, [2, 3277, 1, 25, 1, 3, 186, 186, 1]), 1))

conn.commit()
cur.close()
conn.close()
