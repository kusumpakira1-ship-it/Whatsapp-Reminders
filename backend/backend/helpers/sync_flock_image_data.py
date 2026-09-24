import pymysql

conn = pymysql.connect(
    host='145.223.17.70',
    user='u632391467_kusumpakira',
    password='Kusum@2026Bb!',
    database='u632391467_kusumpakira'
)
cursor = conn.cursor()

image_data = [
    ('Chick 1', '2026-07-04', 27800, 27378, '22'),
    ('Grower 1', '2026-07-04', 27800, 0, None),
    ('Shead 1', '2025-07-25', 19000, 16227, '17'),
    ('Shead 2', '2025-07-25', 24000, 23116, '18'),
    ('Shead 3', '2026-02-12', 22800, 22797, '20'),
    ('Shead 4', '2025-05-10', 22500, 21041, '16'),
    ('Shead 5', '2026-04-13', 23000, 22992, '21'),
    ('Shead 6', '2025-03-12', 22000, 20535, '15'),
    ('Shead 7', '2025-01-25', 22000, 18770, '14'),
    ('Shead 8', '2025-12-01', 23500, 22561, '19'),
    ('Shead 9', '2025-12-01', 23500, 0, None)
]

for shed_name, hatch_date, chicks, live_birds, batch_id in image_data:
    cursor.execute("""
        UPDATE sunfra_flocks 
        SET hatch_date = %s, initial_chicks = %s, live_birds = %s, batch_id = %s 
        WHERE shed_name = %s
    """, (hatch_date, chicks, live_birds, batch_id, shed_name))

conn.commit()
conn.close()
print("Successfully updated sunfra_flocks data to match the reference image.")
