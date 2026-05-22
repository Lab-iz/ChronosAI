from chronos_safe.apps.api.web_ui import build_catalog_payload, render_dashboard_html


def test_dashboard_html_contains_core_sections() -> None:
    html = render_dashboard_html()
    assert "Aula para criancas" in html
    assert "Apophis em 3D" in html
    assert "Comece aqui" in html
    assert "O que voce aprende" in html
    assert "Muitos corpos puxando uns aos outros" in html
    assert "O que e Apophis?" in html
    assert "Area do professor" in html
    assert "Epocas sao rodadas de estudo" in html
    assert "Por que esta cor?" in html
    assert "Verde mostra um caminho bom" in html
    assert "Mostrar desenho" in html
    assert "Revisar Apophis" in html
    assert "trajectory-plot" in html
    assert "/static/chronosfav.png" in html


def test_catalog_payload_exposes_defaults() -> None:
    payload = build_catalog_payload()
    assert "defaults" in payload
    assert "fixtures" in payload
    assert "default_fixture" in payload["defaults"]
