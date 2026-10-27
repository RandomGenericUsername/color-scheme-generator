from __future__ import annotations

import os
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from color_scheme_generator.domain.enums import Backend
from color_scheme_generator.domain.models import ManagedContainer

if TYPE_CHECKING:
    from oci_runtime.domain.types import BuildContext
    from oci_runtime.ports.engine import ContainerEngine as OciContainerEngine

    from color_scheme_generator.domain.models import ContainerMount, ContainerResult


class OciContainerRuntimeAdapter:
    def __init__(self, engine: OciContainerEngine) -> None:
        self._engine = engine

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
        if timeout <= 0:
            raise ValueError(f"Invalid timeout: {timeout}")

        from oci_runtime.domain.enums import NetworkMode, VolumeMountType
        from oci_runtime.domain.types import RunConfig, VolumeMount

        volumes = tuple(
            VolumeMount(
                source=str(m.source),
                target=str(m.target),
                type=VolumeMountType.BIND,
                read_only=m.read_only,
            )
            for m in mounts
        )
        host_user = f"{os.getuid()}:{os.getgid()}"
        config = RunConfig(
            image=image,
            command=(),
            volumes=volumes,
            timeout=float(timeout),
            detach=True,
            remove=False,
            environment=environment or {},
            user=host_user,
            network=NetworkMode.NONE,
            memory_limit=memory_limit,
            labels=labels or {},
        )
        from color_scheme_generator.adapters.error_mapping import map_oci_error

        container_id = None
        try:
            container_id = self._engine.containers.run(config)
            result = self._engine.containers.exec_container(
                container=container_id,
                command=list(command),
                timeout=float(timeout),
            )
        except Exception as exc:
            raise map_oci_error(exc) from exc
        finally:
            if container_id is not None:
                self._engine.containers.remove(container_id, force=True)

        from color_scheme_generator.domain.models import ContainerResult

        return ContainerResult(
            return_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            duration=0.0,
        )

    @staticmethod
    def _map_container(info: Any) -> ManagedContainer:
        labels = info.labels
        if not isinstance(labels, Mapping):
            # Docker's list payload reports Labels as a comma-separated string;
            # only inspect yields a mapping. The filtered list is used for names.
            labels = {}
        return ManagedContainer(
            name=str(info.name),
            state=str(info.state),
            labels=dict(labels),
            created=info.created,
        )

    def list_containers(
        self,
        filters: dict[str, str] | None = None,
        show_all: bool = True,
    ) -> list[ManagedContainer]:
        from color_scheme_generator.adapters.error_mapping import map_oci_error

        try:
            containers = self._engine.containers.list(show_all=show_all, filters=filters)
        except Exception as exc:
            raise map_oci_error(exc) from exc
        return [self._map_container(info) for info in containers]

    def inspect_container(self, name: str) -> ManagedContainer:
        from color_scheme_generator.adapters.error_mapping import map_oci_error

        try:
            info = self._engine.containers.inspect(name)
        except Exception as exc:
            raise map_oci_error(exc) from exc
        return self._map_container(info)

    def remove_container(self, name: str, force: bool = True) -> None:
        from color_scheme_generator.adapters.error_mapping import map_oci_error

        try:
            self._engine.containers.remove(name, force=force)
        except Exception as exc:
            raise map_oci_error(exc) from exc

    def image_exists(self, image: str) -> bool:
        from color_scheme_generator.adapters.error_mapping import map_oci_error

        try:
            return self._engine.images.exists(image)
        except Exception as exc:
            raise map_oci_error(exc) from exc

    def pull_image(self, image: str) -> None:
        from color_scheme_generator.adapters.error_mapping import map_oci_error

        try:
            self._engine.images.pull(image)
        except Exception as exc:
            raise map_oci_error(exc) from exc

    def build_image(
        self,
        context: BuildContext,
        image_name: str,
        timeout: int | None = 600,
        backend: Backend | None = None,
    ) -> str:
        from oci_runtime.domain.exceptions import ImageError

        from color_scheme_generator.domain.exceptions import ImageBuildError

        if timeout is not None and timeout <= 0:
            raise ImageBuildError(
                image=image_name, reason=f"Invalid timeout: {timeout}", backend=backend
            )
        try:
            return self._engine.images.build(context, image_name, timeout)
        except ImageError as exc:
            raise ImageBuildError(
                image=image_name,
                reason=str(exc),
                backend=backend,
            ) from exc

    def remove_image(self, image: str, force: bool = False, backend: Backend | None = None) -> None:
        from oci_runtime.domain.exceptions import ImageError

        from color_scheme_generator.domain.exceptions import ImageRemoveError

        try:
            self._engine.images.remove(image, force=force)
        except ImageError as exc:
            raise ImageRemoveError(
                image=image,
                reason=str(exc),
                backend=backend,
            ) from exc
