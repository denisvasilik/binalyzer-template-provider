import io
import pytest

from binalyzer_core import Binalyzer
from binalyzer_template_provider import XMLTemplateProviderExtension


@pytest.mark.skip()
def test_from_url():
    binalyzer = Binalyzer()
    XMLTemplateProviderExtension(binalyzer)
    binalyzer.xml.from_url(
        "https://admin:emFHi5in6raX93w@denisvasilik-artifactory.westeurope.cloudapp.azure.com/artifactory/binalyzer/wasm_module.xml",
        data=io.BytesIO(bytes([0x00, 0x61, 0x73, 0x6D, 0x01, 0x00, 0x00, 0x00])),
        cert=(
            "/home/ubuntu-dev/git/denisvasilik-iac/secrets/denisvasilik-client-1.cert.pem",
            "/home/ubuntu-dev/git/denisvasilik-iac/secrets/denisvasilik-client-1.decrypted.key.pem",
        ),
        verify="/home/ubuntu-dev/git/denisvasilik-iac/secrets/denisvasilik-sa-root1-server1.chain.pem",
    )
    print(binalyzer.template.magic.value)
