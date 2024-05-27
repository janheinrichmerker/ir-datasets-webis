from dataclasses import dataclass
from datetime import datetime
from functools import cached_property
from gzip import decompress
from itertools import chain, groupby
from os import PathLike
from pathlib import Path
from typing import Annotated,  Mapping, NamedTuple, Sequence, Optional, Type, Iterator,  Iterable, Union,   overload
from uuid import UUID

from annotated_types import Ge
from pydantic import Field, TypeAdapter

from ir_datasets import registry
from ir_datasets.datasets.base import Dataset
from ir_datasets.formats import BaseDocs
from ir_datasets.indices import Docstore
from ir_datasets.util import Download, apply_sub_slice, slice_idx, home_path
from ir_datasets_webis.util import DownloadConfig, YamlDocumentation


class WebisMastodon2024AccountEmoji(NamedTuple):
    shortcode: str
    static_url: str
    url: str
    visible_in_picker: bool


class WebisMastodon2024AccountField(NamedTuple):
    name: str
    value: str
    verified_at: datetime


class WebisMastodon2024Account(NamedTuple):
    id: str
    acct: str
    """The 'username@instance' handle for remote accounts, and just the 'username' for local acconuts."""
    avatar: str
    avatar_static: str
    is_bot: Annotated[bool, Field(alias="bot")]
    created_at: datetime
    discoverable: bool
    display_name: str
    followers_count: int
    following_count: int
    is_group: Annotated[bool, Field(alias="group")]
    handle: str
    """The 'username@instance' handle for remote and local acconuts."""
    header: str
    header_static: str
    last_status_at: datetime
    is_locked: Annotated[bool, Field(alias="locked")]
    is_noindex: Annotated[bool, Field(alias="noindex")]
    note: str
    statuses_count: int
    url: str
    uri: str
    username: str
    emojis: Sequence[WebisMastodon2024AccountEmoji]
    fields: Sequence[WebisMastodon2024AccountField]


class WebisMastodon2024Application(NamedTuple):
    name: str
    website: str


class WebisMastodon2024Card(NamedTuple):
    author_name: str
    author_url: str
    blurhash: str
    description: str
    embed_url: str
    height: int
    width: int
    image: str
    image_description: str
    language: str
    provider_name: str
    provider_url: str
    published_at: datetime
    title: str
    type: str
    url: str


class WebisMastodon2024MediaAttachmentFocus(NamedTuple):
    x: float
    y: float


class WebisMastodon2024MediaAttachmentMetaInfo(NamedTuple):
    width: int
    height: int
    aspect: float
    bitrate: int
    duration: float
    frame_rate: str


class WebisMastodon2024MediaAttachmentMeta(NamedTuple):
    audio_bitrate: str
    audio_channels: str
    audio_encode: str
    focus: WebisMastodon2024MediaAttachmentFocus
    original: WebisMastodon2024MediaAttachmentMetaInfo
    small: WebisMastodon2024MediaAttachmentMetaInfo


class WebisMastodon2024MediaAttachment(NamedTuple):
    id: str
    blurhash: str
    description: str
    meta: WebisMastodon2024MediaAttachmentMeta
    preview_url: str
    remote_url: str
    type: str
    url: str


class WebisMastodon2024Mention(NamedTuple):
    id: str
    acct: str
    url: str
    username: str


class WebisMastodon2024PollOption(NamedTuple):
    title: str
    votes_count: int


class WebisMastodon2024Poll(NamedTuple):
    id: str
    expires_at: datetime
    is_expired: Annotated[bool, Field(alias="expired")]
    is_multiple_choice: Annotated[bool, Field(alias="multiple")]
    votes_count: int
    voters_count: int
    options: Sequence[WebisMastodon2024PollOption]


class WebisMastodon2024Reblog(NamedTuple):
    id: str
    url: str


class WebisMastodon2024Tag(NamedTuple):
    name: str
    url: str


class WebisMastodon2024Doc(NamedTuple):
    uuid: UUID
    doc_id: str  # TODO: UUID from ES ID.
    id: str
    """Mastodon-internal ID. Not unique across instances."""
    account: WebisMastodon2024Account
    api_url: str
    application: WebisMastodon2024Application
    card: WebisMastodon2024Card
    text: Annotated[str, Field(alias="content")]
    crawled_at: datetime
    crawled_from_api_url: str
    """API endpoint where the post was crawled from."""
    crawled_from_instance: str
    """API endpoint where the post was crawled from."""
    created_at: datetime
    edited_at: datetime
    in_reply_to_account_id: str
    in_reply_to_id: str
    instance: str
    is_local: bool
    language: str
    poll: WebisMastodon2024Poll
    reblog: WebisMastodon2024Reblog
    is_sensitive: Annotated[bool, Field(alias="sensitive")]
    spoiler_text: str
    uri: str
    url: str
    visibility: str
    emojis: Sequence[WebisMastodon2024AccountEmoji]
    media_attachments: Sequence[WebisMastodon2024MediaAttachment]
    mentions: Sequence[WebisMastodon2024Mention]
    tags: Sequence[str]

    def default_text(self):
        return self.text

_WebisMastodon2024DocAdapter = TypeAdapter(WebisMastodon2024Doc)

@dataclass(frozen=True)
class _Config:
    id: str
    instance: str | None = None

    @cached_property
    def documantation_tag(self) -> str:
        name = self.id
        name = name.removeprefix("webis-mastodon-2024")
        name = name.removeprefix("/")
        if name == "":
            return "_"
        else:
            return name


_INSTANCES = ("mastodon.social",)
_CONFIGS = [
    _Config(id="webis-mastodon-2024"),
] + [
    _Config(
        id=f"webis-mastodon-2024/{instance}",
           instance=instance,
    )
    for instance in _INSTANCES
]


class _InstanceOffset(NamedTuple):
    uuid: UUID
    file: str
    offset: Annotated[int, Ge(0)]
    length: Annotated[int, Ge(0)]

_InstanceOffsetAdapter = TypeAdapter(_InstanceOffset)

class _Offset(NamedTuple):
    uuid: UUID
    path: Path
    offset: Annotated[int, Ge(0)]
    length: Annotated[int, Ge(0)]


@dataclass(frozen=True)
class WebisMastodon2024Docs(BaseDocs):
    _name: str
    _source: Download
    _config: _Config

    @cached_property
    def _path(self) -> Path:
        return Path(self.docs_path())

    def docs_path(self, force: bool = True) -> Union[str, PathLike]:
        return self._source.path(force)

    def docs_iter(self) -> Iterator[WebisMastodon2024Doc]:
        return WebisMastodon2024Iterator(self)

    def docs_store(self) -> "WebisMastodon2024Docstore":
        return WebisMastodon2024Docstore(self)

    def docs_cls(self) -> Type[WebisMastodon2024Doc]:
        return WebisMastodon2024Doc

    @cached_property
    def _instances(self) -> Sequence[str]:
        if self._config.instance is not None:
            return [self._config.instance]
        return sorted(
            path.name
            for path in self._path.iterdir()
        )

    def _count_offsets(self, instance: str) -> int:
        with (self._path / instance / "offsets.jsonl").open("rt", encoding="utf8") as file:
            return sum(1 for _ in file)

    @cached_property
    def _offsets_count(self) -> int:
        return sum(
            self._count_offsets(path)
            for path in self._offsets_paths
        )

    def docs_count(self) -> int:
        return self._offsets_count

    def docs_namespace(self) -> str:
        return self._name

    def docs_lang(self) -> Optional[str]:
        return None

    def _iter_offsets(self, instance: str) -> Iterator[_Offset]:
        print("Iterating offsets for instance:", instance)
        with (self._path / instance / "offsets.jsonl").open("rt", encoding="utf8") as file:
            for line in file:
                offset = _InstanceOffsetAdapter.validate_json(line)
                yield _Offset(
                    uuid=offset.uuid,
                    path=self._path / instance / offset.file,
                    offset=offset.offset,
                    length=offset.length,
                )

    @cached_property
    def _offsets(self) -> Sequence[_Offset]:
        return list(chain.from_iterable(
            self._iter_offsets(instance)
            for instance in self._instances
        ))

    @cached_property
    def _offsets_dict(self) -> Mapping[UUID, _Offset]:
        return {
            offset.uuid: offset
            for offset in self._offsets
        }

    def _iter_docs(self, offsets: Iterable[_Offset]) -> Iterator[WebisMastodon2024Doc]:
        # Sort offsets by file path.
        offsets = sorted(offsets, key=lambda o: o.path)

        # Group offsets by file path.
        path_offsets: Iterable[_Offset]
        for path, path_offsets in groupby(offsets, key=lambda o: o.path):
            # Sort offsets by offset in the file.
            path_offsets = sorted(path_offsets, key=lambda o: o.offset)

            with Path(path).open("rb") as file:
                for offset in path_offsets:
                    file.seek(offset.offset)
                    buffer = file.read(offset.length)
                    buffer = decompress(buffer)
                    yield _WebisMastodon2024DocAdapter.validate_json(buffer)


@dataclass
class WebisMastodon2024Docstore(Docstore):
    _docs: WebisMastodon2024Docs

    def __post_init__(self):
        super().__init__(WebisMastodon2024Doc, "doc_id")

    def get_many_iter(self, doc_ids: Iterable[str]) -> Iterator[WebisMastodon2024Doc]:
        offsets = {
            self._docs._offsets_dict[UUID(doc_id)]
            for doc_id in doc_ids
        }
        return self._docs._iter_docs(offsets)


@dataclass(frozen=True)
class WebisMastodon2024Iterator(Iterator[WebisMastodon2024Doc]):
    _docs: WebisMastodon2024Docs

    @cached_property
    def _iterator(self) -> Iterator[WebisMastodon2024Doc]:
        return self._docs._iter_docs(self._docs._offsets)

    def __next__(self) -> WebisMastodon2024Doc:
        return next(self._iterator)

    @overload
    def __getitem__(self, key: int) -> WebisMastodon2024Doc:
        pass

    @overload
    def __getitem__(self, key: slice) -> Iterator[WebisMastodon2024Doc]:
        pass

    def __getitem__(
        self, key: int | slice
    ) -> WebisMastodon2024Doc | Iterator[WebisMastodon2024Doc]:
        docs_count = self._docs.docs_count()
        full_slice = slice(0, docs_count)
        processed_slice: slice
        if isinstance(key, slice):
            processed_slice = apply_sub_slice(full_slice, key)
        elif isinstance(key, int):
            processed_slice = slice_idx(full_slice, key)
        else:
            raise TypeError("The key must be int or slice.")

        offsets = self._docs._offsets[processed_slice]
        return self._docs._iter_docs(offsets)


def register() -> None:
    if "webis-mastodon-2024" in registry:
        # Already registered.
        return

    documentation = YamlDocumentation("webis_mastodon_2024.yaml")
    base_path = home_path() / "webis-mastodon-2024"
    download = DownloadConfig.context("webis-mastodon-2024", base_path)

    for config in _CONFIGS:
        registry.register(
            config.id,
            Dataset(
                documentation(config.documantation_tag),
                WebisMastodon2024Docs(
                    config.id,
                    download["docs"],
                    config,
                )
            ),
        )
