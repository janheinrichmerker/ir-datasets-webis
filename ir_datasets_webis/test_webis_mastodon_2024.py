from datetime import datetime
from re import compile as re_compile, DOTALL
from uuid import UUID

from pytest import mark
from pytest_subtests import SubTests

from ir_datasets import log, load, Dataset
from ir_datasets.util import home_path

from ir_datasets_webis import register
from ir_datasets_webis.webis_mastodon_2024 import WebisMastodon2024Doc
from ir_datasets_webis.conftest import _test_docs, _test_docs_slice

_logger = log.easy()


skip_if_dir_not_found = mark.skipif(
    not (home_path() / "webis-mastodon-2024").exists(),
    reason="Webis directory not available."
)


@skip_if_dir_not_found
def test_webis_mastodon_2024_meta() -> None:
    register()

    dataset = load("webis-mastodon-2024")
    assert dataset.has_docs()
    assert not dataset.has_queries()
    assert not dataset.has_qrels()
    assert not dataset.has_scoreddocs()
    assert not dataset.has_docpairs()
    assert not dataset.has_qlogs()

    instances = ["mastodon.social"]
    for instance in instances:
        instance_dataset: Dataset = load(f"webis-mastodon-2024/{instance}")
        assert instance_dataset.has_docs()
        assert not instance_dataset.has_queries()
        assert not instance_dataset.has_qrels()
        assert not instance_dataset.has_scoreddocs()
        assert not instance_dataset.has_docpairs()
        assert not instance_dataset.has_qlogs()
        assert instance_dataset.docs_lang() is None


@skip_if_dir_not_found
def test_webis_mastodon_2024_docs(subtests: SubTests) -> None:
    register()

    _test_docs(
        subtests,
        "webis-mastodon-2024",
        count=200_000_000,
        items={
            # 0: WebisLDoc(
            #     doc_id="webis-de0000-00-00000",
            #     url="https://www.alba.info/karriere/",
            #     url_hash="EF1C364E908E1460885D7DF3C91B6FE5",
            #     language="de",
            #     text=re_compile(  # type: ignore
            #         pattern=r".*Speichert den Zustimmungsstatus des Benutzers für Cookies auf der aktuellen Domäne.$",self._coself._config.languagenfig.language
            #         flags=DOTALL,
            #     ),
            # ),
            # 1_000: WebisLDoc(
            #     doc_id="webis-de0000-00-01000",
            #     url="https://totallygamergirl.com/2021/10/22/forza-horizon-4-festival-spielliste-kw-42-2021-aufgaben-belohnungen-und-voraussetzungen/",
            #     url_hash="FCB5D1104F48D49F2F68DA4AB1D3E0A7",
            #     language="de",
            #     text=re_compile(  # type: ignore
            #         pattern=r".*Bildquelle: eigene Screenshots aus Forza Horizon 4$",
            #         flags=DOTALL,
            #     ),
            # ),
            # 100_000_000: WebisLDoc(
            #     doc_id="webis-es0000-56-11365",
            #     url="https://conjugador.reverso.net/conjugacion-espanol-verbo-parlar.html",
            #     url_hash="8AA0B21CFF8A1F0B1F0B9EFFF30D5EEA",
            #     language="es",
            #     text=re_compile(  # type: ignore
            #         pattern=r".*supervisar, meter, convocar, estructurar, graznar, implementar, desarmar, elegir, objetar%",
            #         flags=DOTALL,
            #     )
            # ),
        },
    )


@skip_if_dir_not_found
def test_webis_mastodon_2024_slice() -> None:
    register()

    dataset = load("webis-mastodon-2024")

    _test_docs_slice(
        dataset, slice(None, 100), 100, "start of file"
    )
    _test_docs_slice(
        dataset, slice(None, 100, 2), 50, "start of file with step"
    )
    _test_docs_slice(
        dataset, slice(5000, 5100), 100, "middle of file",
    )
    _test_docs_slice(
        dataset, slice(23200, 23241), 41, "end of file",
    )
    _test_docs_slice(
        dataset, slice(23241, 23300), 59, "start of new file",
    )
    _test_docs_slice(
        dataset, slice(23200, 23300), 100, "across file boundary",
    )
    _test_docs_slice(
        dataset, slice(2278243, 2278343), 100, "later file",
        skip_islice=True,
    )
    _test_docs_slice(
        dataset, slice(
            100_000_000, 100_000_100), 100, "middle of dataset",
        skip_islice=True,
    )
    _test_docs_slice(
        dataset, slice(
            180_000_000, 180_000_100), 100, "near end of dataset",
        skip_islice=True,
    )


# @skip_if_dir_not_found
# def test_webis_docstore() -> None:
#     register()

#     ids = [
#         "webis-de0000-01-00014",
#         "webis-de0000-01-12119",
#         "webis-de0000-05-19516",
#     ]
#     ids_nearby = [
#         "webis-de0000-01-00020",
#         "webis-de0000-01-12201",
#         "webis-de0000-05-19412",
#     ]
#     ids_earlier = [
#         "webis-de0000-01-00001",
#         "webis-de0000-05-08131",
#     ]

#     docstore = load("webis-mastodon-2024").docs_store()
#     docstore.clear_cache()
#     with _logger.duration("cold fetch"):
#         docstore.get_many(ids)
#     docstore.clear_cache()
#     with _logger.duration("cold fetch (cleared)"):
#         docstore.get_many(ids)
#     with _logger.duration("warm fetch"):
#         docstore.get_many(ids)
#     docstore = load("webis-mastodon-2024").docs_store()
#     with _logger.duration("warm fetch (new docstore)"):
#         docstore.get_many(ids)
#     with _logger.duration("cold fetch (nearby)"):
#         docstore.get_many(ids_nearby)
#     with _logger.duration("cold fetch (earlier)"):
#         docstore.get_many(ids_earlier)
#     docstore.clear_cache()
#     with _logger.duration("cold fetch (earlier, cleared)"):
#         docstore.get_many(ids_earlier)
