use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use titlecase::titlecase;

#[pyfunction]
fn search_markdown(
    processing_time_ms: usize,
    estimated_total_hits: Option<usize>,
    hits: Option<&PyList>,
) -> PyResult<String> {
    let mut lines = Vec::new();
    let total_hits: usize;

    if let Some(hits) = estimated_total_hits {
        total_hits = hits;
    } else {
        total_hits = 0;
    }

    lines.push(format!(
        "## Hits: ~{total_hits} | Search time: {processing_time_ms}\n"
    ));

    if let Some(h) = hits {
        for hit in h.iter() {
            let hit_dict = hit.extract::<&PyDict>()?;
            for (k, v) in hit_dict.iter() {
                lines.push(format!("{}: {}", k, v));
            }
            lines.push(String::from("-------------------------------"));
        }
        Ok(lines.join("\n"))
    } else {
        Ok(String::from("No results found"))
    }
}

#[pyfunction]
fn settings_markdown(index: &str, results: &PyDict) -> PyResult<String> {
    let mut lines = Vec::new();

    lines.push(format!("# Settings for {index} index\n"));

    for (k, v) in results.iter() {
        lines.push(format!(
            "## {}\n{}\n",
            titlecase(&k.to_string().replace('_', " ")),
            v
        ));
    }

    Ok(lines.join("\n"))
}

#[pymodule]
fn _meilisearch_tui(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(search_markdown, m)?)?;
    m.add_function(wrap_pyfunction!(settings_markdown, m)?)?;
    Ok(())
}
