from json import loads as json_loads
from pkgutil import get_data

from ir_datasets.datasets.base import YamlDocumentation as _IrdsYamlDocumentation
from ir_datasets.util import _DownloadConfig as _IrdsDownloadConfig
from yaml import load as yaml_load, BaseLoader


class YamlDocumentation(_IrdsYamlDocumentation):
    """
    Override the ir_datasets-internal implementation to instead load documentation from our package data.
    """

    def get_key(self, key):
        if not self._contents:
            data = get_data('ir_datasets_webis', self._file)
            self._contents = yaml_load(data, Loader=BaseLoader)
        return self._contents.get(key)


class _DownloadConfig(_IrdsDownloadConfig):
    """
    Override the ir_datasets-internal implementation to instead load download configurations from our package data.
    """

    def contents(self):
        if self._contents is None:
            data = get_data('ir_datasets_webis', self._file)
            self._contents = json_loads(data)
        return self._contents


DownloadConfig = _DownloadConfig(file="downloads.json")
