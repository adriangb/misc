use pyo3::{prelude::*, PyVisit, PyTraverseError};

#[pyclass]
struct WithoutGc {
    #[pyo3(get)]
    obj: Option<Py<PyAny>>,
}

#[pymethods]
impl WithoutGc {
    #[new]
    fn new(obj: Py<PyAny>) -> Self {
        Self { obj: Some(obj) }
    }
}

#[pyclass]
struct WithTraverse {
    #[pyo3(get)]
    obj: Option<Py<PyAny>>,
}

#[pymethods]
impl WithTraverse {
    #[new]
    fn new(obj: Py<PyAny>) -> Self {
        Self { obj: Some(obj) }
    }
    fn __traverse__(&self, visit: PyVisit<'_>) -> Result<(), PyTraverseError> {
        visit.call(&self.obj)
    }
    fn __clear__(&mut self) {}
}


#[pyclass]
struct WithTraverseAndClear {
    #[pyo3(get)]
    obj: Option<Py<PyAny>>,
}

#[pymethods]
impl WithTraverseAndClear {
    #[new]
    fn new(obj: Py<PyAny>) -> Self {
        Self { obj: Some(obj) }
    }
    fn __traverse__(&self, visit: PyVisit<'_>) -> Result<(), PyTraverseError> {
        if let Some(obj) = &self.obj {
            visit.call(obj)?;
        }
        Ok(())
    }
    fn __clear__(&mut self) {
        self.obj = None;
    }
}


/// A Python module implemented in Rust.
#[pymodule]
fn demo(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<WithoutGc>()?;
    m.add_class::<WithTraverse>()?;
    m.add_class::<WithTraverseAndClear>()?;
    Ok(())
}
