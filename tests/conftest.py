import pytest

@pytest.fixture
def records():
    base = {"document_id": "GLF_TEST", "source_name": "Documento sintético de prueba",
            "page": 1, "source_url": "https://galapagoslifefund.org.ec/test.pdf", "language": "es"}
    return [dict(base, chunk_id="TEST::1", text="El manglar requiere medidas de restauración ambiental."),
            dict(base, chunk_id="TEST::2", text="El presupuesto contiene bienes y servicios.")]
