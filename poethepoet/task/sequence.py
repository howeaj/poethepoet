from pathlib import Path
from typing import (
    Any,
    Dict,
    Generator,
    Iterable,
    List,
    MutableMapping,
    Optional,
    Type,
    TYPE_CHECKING,
    Union,
)
from .base import PoeTask, TaskContent
from ..exceptions import ExecutionError, PoeException

if TYPE_CHECKING:
    from ..ui import PoeUi
    from ..config import PoeConfig


class SequenceTask(PoeTask):
    """
    A task consisting of a sequence of other tasks
    """

    content: List[Union[str, Dict[str, Any]]]

    __key__ = "sequence"
    __content_type__: Type = list
    __options__: Dict[str, Type] = {"ignore_fail": bool}

    def __init__(
        self,
        name: str,
        content: TaskContent,
        options: Dict[str, Any],
        ui: "PoeUi",
        config: "PoeConfig",
    ):
        super().__init__(name, content, options, ui, config)
        self.subtasks = [
            self.from_def(
                task_def=item,
                task_name=f"{name}[{index}]",
                config=config,
                ui=ui,
                array_item=True,
            )
            for index, item in enumerate(self.content)
        ]

    def _handle_run(
        self,
        extra_args: Iterable[str],
        project_dir: Path,
        env: MutableMapping[str, str],
        dry: bool = False,
        subproc_only: bool = False,
    ) -> Generator[Dict[str, Any], int, int]:
        if any(arg.strip() for arg in extra_args):
            raise PoeException(f"Sequence task {self.name!r} does not accept arguments")
        for subtask in self.subtasks:
            task_result = subtask.run(
                extra_args=tuple(),
                project_dir=project_dir,
                env=env,
                dry=dry,
                subproc_only=True,
            )
            if task_result and not self.options.get("ignore_fail"):
                raise ExecutionError(
                    f"Sequence aborted after failed subtask {subtask.name!r}"
                )
        return 0
        yield  # pylint: disable=unreachable

    @classmethod
    def _validate_task_def(
        cls, task_name: str, task_def: Dict[str, Any], config: "PoeConfig"
    ) -> Optional[str]:
        """
        Check the given task definition for validity specific to this task type and
        return a message describing the first encountered issue if any.
        """
        issue = None
        return issue
