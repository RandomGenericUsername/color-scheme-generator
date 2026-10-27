from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from color_scheme_generator.domain.enums import Backend

if TYPE_CHECKING:
    from oci_runtime.domain.types import BuildContext

from color_scheme_generator.domain.models import ContainerMount, ContainerResult, ManagedContainer


@runtime_checkable
class ContainerRuntimePort(Protocol):
    def run(
        self,
        image: str,
        command: list[str],
        mounts: list[ContainerMount],
        timeout: int,
        environment: dict[str, str] | None = None,
        memory_limit: str | None = None,
        labels: dict[str, str] | None = None,
    ) -> ContainerResult:
        ...

    def list_containers(
        self,
        filters: dict[str, str] | None = None,
        show_all: bool = True,
    ) -> list[ManagedContainer]:
        ...

    def inspect_container(self, name: str) -> ManagedContainer:
        ...

    def remove_container(self, name: str, force: bool = True) -> None:
        ...

    def image_exists(self, image: str) -> bool:
        ...

    def pull_image(self, image: str) -> None:
        ...

    def build_image(
        self,
        context: BuildContext,
        image_name: str,
        timeout: int | None = 600,
        backend: Backend | None = None,
    ) -> str:
        ...

    def remove_image(self, image: str, force: bool = False, backend: Backend | None = None) -> None:
        ...
