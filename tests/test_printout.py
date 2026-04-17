from cpl50.io import summarize_dataset


def test_summary_runs(tmp_path):
    content = """10.3390/molecules23102606,mol,293.15,1e-5,meoh,250,di,0
0,1
1,2
"""
    d = tmp_path / "spectra"
    d.mkdir()

    f = d / "a.csv"
    f.write_text(content)

    summary = summarize_dataset(str(d))

    assert "mol" in summary