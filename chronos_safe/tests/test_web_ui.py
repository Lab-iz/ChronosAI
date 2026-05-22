from chronos_safe.apps.api.web_ui import build_catalog_payload, render_dashboard_html


def test_dashboard_html_contains_core_sections() -> None:
    html = render_dashboard_html()
    assert "Missao Apophis em 3D" in html
    assert "Comece aqui" in html
    assert "Objetivo da plataforma" in html
    assert "simulacao de muitos corpos" in html
    assert "O que e Apophis?" in html
    assert "Opcoes de professor e pesquisa" in html
    assert "Por que esta cor?" in html
    assert "Exemplo com alerta" in html
    assert "Mostrar caminho no espaco" in html
    assert "Revisar Apophis com detalhes" in html
    assert "trajectory-plot" in html
    assert "Area de professor" in html
    assert "/static/chronosfav.png" in html


def test_catalog_payload_exposes_defaults() -> None:
    payload = build_catalog_payload()
    assert "defaults" in payload
    assert "fixtures" in payload
    assert "default_fixture" in payload["defaults"]
