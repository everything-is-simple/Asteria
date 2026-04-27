from pathlib import Path

from asteria.core.paths import AsteriaPaths


def test_default_paths_use_asteria_roots() -> None:
    paths = AsteriaPaths.from_env(Path("H:/Asteria"))

    assert paths.repo_root == Path("H:/Asteria")
    assert paths.data_root == Path("H:/Asteria-data")
    assert paths.report_root == Path("H:/Asteria-report")
    assert paths.validated_root == Path("H:/Asteria-Validated")
    assert paths.temp_root == Path("H:/Asteria-temp")


def test_database_path_appends_duckdb_suffix() -> None:
    paths = AsteriaPaths.from_env(Path("H:/Asteria"))

    assert paths.database_path("malf_core_day") == Path("H:/Asteria-data/malf_core_day.duckdb")
