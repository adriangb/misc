use pyo3::prelude::*;
use pyo3::Python;

use arrow::pyarrow::PyArrowConvert;
use arrow::record_batch::RecordBatch;

fn run(batch: RecordBatch) -> () {
    let rows = batch.num_rows();
    for col in batch.columns() {
        if let Some(bitmap) = col.data_ref().null_bitmap() {
            println!("bitmap bit len = {:?}", bitmap.bit_len());
        }
        for idx in 0..rows {
            println!("is_null = {:?}", col.is_null(idx));
        }
    }
}

#[pyfunction]
fn err(batch: &PyAny) -> () {
    let batch = RecordBatch::from_pyarrow(batch).unwrap();
    run(batch)
}

#[pymodule]
fn arrow_bug_demo(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(err, m)?)?;
    Ok(())
}

#[test]
fn run_test() -> () {
    use std::{fs::File, path::Path};
    use parquet::arrow::arrow_reader::ParquetRecordBatchReaderBuilder;

    let path = Path::new("bad.parquet");
    let file = File::open(&path).unwrap();
    let builder = ParquetRecordBatchReaderBuilder::try_new(file).unwrap();
    let mut reader = builder.build().unwrap();
    let record_batch = reader.next().unwrap().unwrap();
    let slice = record_batch.slice(9, record_batch.num_rows()-9);
    run(slice)
}