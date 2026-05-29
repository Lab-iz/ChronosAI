from chronos_seguro.aplicativos.api.interface_web import montar_payload_catalogo, renderizar_html_painel


def test_html_painel_contem_secoes_principais() -> None:
    html = renderizar_html_painel()
    assert "Aula para crianças" in html
    assert "Apophis em 3D" in html
    assert "Comece aqui" in html
    assert "O que voce aprende" in html
    assert "Muitos corpos puxando uns aos outros" in html
    assert "O que e Apophis?" in html
    assert "Área do professor" in html
    assert "Épocas sao rodadas de estudo" in html
    assert "Por que esta cor?" in html
    assert "Verde mostra um caminho bom" in html
    assert "Mostrar desenho" in html
    assert "Revisar Apophis" in html
    assert "trajectory-plot" in html
    assert "/static/chronosfav.png" in html


def test_payload_catalogo_expoe_padroes() -> None:
    payload = montar_payload_catalogo()
    assert "defaults" in payload
    assert "cenarios" in payload
    assert "default_fixture" in payload["defaults"]
