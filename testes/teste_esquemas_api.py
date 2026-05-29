import pytest
from pydantic import ValidationError

from chronos_seguro.aplicativos.api.esquemas import RequisicaoGerarGeneralista


def test_esquema_generalista_rejeita_intervalo_corpos_invalido() -> None:
    with pytest.raises(ValidationError):
        RequisicaoGerarGeneralista(output_dir="dados/processados/invalido", min_bodies=5, max_bodies=3)
