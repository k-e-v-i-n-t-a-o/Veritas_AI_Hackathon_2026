# well, I don't really need to keep this. but i guess its good here anyways.

import duckdb

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute("SET s3_region='us-east-1';")

query = """
COPY (
    SELECT *
    FROM read_csv_auto(
        's3://openaq-data-archive/records/csv.gz/locationid=2812625/year=202[3-6]/*/*.csv.gz',
        hive_partitioning = true
    )
    ORDER BY datetime
) TO 'location_2812625_2023_2026.csv' (HEADER, DELIMITER ',');
"""

con.execute(query)
print("Saved to location_2812625_2023_2026.csv")
