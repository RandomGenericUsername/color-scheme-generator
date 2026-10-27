from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from oci_runtime.domain.enums import ContainerState
from oci_runtime.domain.types import ContainerInfo

from color_scheme_generator.adapters.oci_container_runtime import (
    OciContainerRuntimeAdapter,
)
from color_scheme_generator.domain.exceptions import ColorSchemeError
from color_scheme_generator.domain.models import ManagedContainer


@pytest.fixture
def engine() -> MagicMock:
    engine = MagicMock()
    engine.containers.run.return_value = "container-id"
    engine.containers.exec_container.return_value = SimpleNamespace(
        returncode=0, stdout="", stderr=""
    )
    return engine


@pytest.fixture
def adapter(engine: MagicMock) -> OciContainerRuntimeAdapter:
    return OciContainerRuntimeAdapter(engine)


def _info(
    *,
    name: str = "csg-wrapper",
    state: ContainerState = ContainerState.EXITED,
    created: str | None = "2026-01-01T00:00:00.123456789Z",
    labels: object = None,
    container_id: str = "",
) -> ContainerInfo:
    return ContainerInfo(
        id=container_id,
        name=name,
        image="localhost/csg-wallust-podman:v0.2.0",
        state=state,
        status=str(state),
        created=created,
        labels={} if labels is None else labels,  # type: ignore[arg-type]
    )


class TestRunLabels:
    def test_labels_threaded_into_run_config(
        self, adapter: OciContainerRuntimeAdapter, engine: MagicMock
    ) -> None:
        labels = {"csg.managed": "true", "csg.session": "session-1"}

        adapter.run(
            image="test:latest",
            command=["csg-inner"],
            mounts=[],
            timeout=30,
            labels=labels,
        )

        config = engine.containers.run.call_args.args[0]
        assert config.labels == labels

    def test_missing_labels_default_to_empty_mapping(
        self, adapter: OciContainerRuntimeAdapter, engine: MagicMock
    ) -> None:
        adapter.run(
            image="test:latest",
            command=["csg-inner"],
            mounts=[],
            timeout=30,
        )

        config = engine.containers.run.call_args.args[0]
        assert config.labels == {}

    def test_run_still_removes_its_wrapper_in_finally(
        self, adapter: OciContainerRuntimeAdapter, engine: MagicMock
    ) -> None:
        adapter.run(
            image="test:latest",
            command=["csg-inner"],
            mounts=[],
            timeout=30,
            labels={"csg.managed": "true"},
        )

        engine.containers.remove.assert_called_once_with("container-id", force=True)

    def test_run_removes_wrapper_when_exec_fails(
        self, adapter: OciContainerRuntimeAdapter, engine: MagicMock
    ) -> None:
        engine.containers.exec_container.side_effect = RuntimeError("exec failed")

        with pytest.raises(ColorSchemeError, match="exec failed"):
            adapter.run(
                image="test:latest",
                command=["csg-inner"],
                mounts=[],
                timeout=30,
                labels={"csg.managed": "true"},
            )

        engine.containers.remove.assert_called_once_with("container-id", force=True)


class TestListContainers:
    def test_filter_and_show_all_forwarded(
        self, adapter: OciContainerRuntimeAdapter, engine: MagicMock
    ) -> None:
        engine.containers.list.return_value = []

        result = adapter.list_containers(filters={"label": "csg.managed=true"}, show_all=True)

        assert result == []
        engine.containers.list.assert_called_once_with(
            show_all=True, filters={"label": "csg.managed=true"}
        )

    def test_defaults_ask_for_all_containers(
        self, adapter: OciContainerRuntimeAdapter, engine: MagicMock
    ) -> None:
        engine.containers.list.return_value = []

        adapter.list_containers()

        engine.containers.list.assert_called_once_with(show_all=True, filters=None)

    def test_maps_container_info_to_managed_container(
        self, adapter: OciContainerRuntimeAdapter, engine: MagicMock
    ) -> None:
        info = _info(
            name="csg-wrapper",
            state=ContainerState.RUNNING,
            labels={"csg.managed": "true"},
        )
        engine.containers.list.return_value = [info]

        containers = adapter.list_containers()

        assert len(containers) == 1
        container = containers[0]
        assert isinstance(container, ManagedContainer)
        assert container.name == "csg-wrapper"
        assert container.state == "running"
        assert container.labels == {"csg.managed": "true"}
        assert container.created == "2026-01-01T00:00:00.123456789Z"

    def test_docker_style_string_labels_normalised_to_empty_mapping(
        self, adapter: OciContainerRuntimeAdapter, engine: MagicMock
    ) -> None:
        # Docker's list payload returns Labels as a comma-separated string.
        info = _info(labels="csg.managed=true,csg.session=abc")
        engine.containers.list.return_value = [info]

        container = adapter.list_containers()[0]

        assert container.labels == {}


class TestInspectAndRemove:
    def test_inspect_uses_name_not_docker_list_id(
        self, adapter: OciContainerRuntimeAdapter, engine: MagicMock
    ) -> None:
        info = _info(
            name="csg-wrapper",
            container_id="",
            labels={"csg.managed": "true", "csg.session": "abc"},
        )
        engine.containers.inspect.return_value = info

        container = adapter.inspect_container("csg-wrapper")

        engine.containers.inspect.assert_called_once_with("csg-wrapper")
        assert container.name == "csg-wrapper"
        assert container.labels == {"csg.managed": "true", "csg.session": "abc"}

    def test_inspect_maps_non_mapping_labels_to_empty_mapping(
        self, adapter: OciContainerRuntimeAdapter, engine: MagicMock
    ) -> None:
        engine.containers.inspect.return_value = _info(labels="not-a-mapping")

        container = adapter.inspect_container("csg-wrapper")

        assert container.labels == {}

    def test_remove_forwards_force_flag(
        self, adapter: OciContainerRuntimeAdapter, engine: MagicMock
    ) -> None:
        adapter.remove_container("csg-wrapper", force=True)

        engine.containers.remove.assert_called_once_with("csg-wrapper", force=True)

    def test_remove_defaults_to_force(
        self, adapter: OciContainerRuntimeAdapter, engine: MagicMock
    ) -> None:
        adapter.remove_container("csg-wrapper")

        engine.containers.remove.assert_called_once_with("csg-wrapper", force=True)
