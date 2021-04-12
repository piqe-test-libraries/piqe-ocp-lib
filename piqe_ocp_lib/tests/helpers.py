import os

from typing import Optional

from piqe_ocp_lib.api.resources.ocp_base import OcpBase, Version


class Config:
    def __init__(self, kubeconfig: Optional[str] = None):
        self.kubeconfig = kubeconfig or os.environ.get("KUBECONFIG")

    @property  # Change to cached_property (py >= 3.8)
    def version(self) -> Version:
        ocp_base = OcpBase(self.kubeconfig)
        return ocp_base.ocp_version


config = Config()
