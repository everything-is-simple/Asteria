from asteria.core.contracts import MainlineModule


def test_mainline_module_id_uses_system_readout() -> None:
    values = {module.value for module in MainlineModule}

    assert MainlineModule.SYSTEM_READOUT.value == "system_readout"
    assert "system" not in values
