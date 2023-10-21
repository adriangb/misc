import pyarrow.parquet as pq

from arrow_bug_demo import err


arrow_table = pq.read_table("bad.parquet", columns=["passenger_count"])

slice_batches = arrow_table.slice(9).to_batches()

batch = slice_batches[0]
err(batch)
