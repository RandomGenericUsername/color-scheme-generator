from rich_logging import (
    LogLevels,
    Log,
    ConsoleHandlers,
    FileHandlerSpec,
    FileHandlerTypes,
    FileHandlerSettings,
    RichHandlerSettings,
    RichLogger,
)
from pathlib import Path



def create_log_file(log_dir: Path) -> None:
    assert log_dir is not None, "Directory must be set when logging to file"
    if log_dir.exists():
        return
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise RuntimeError(
            f"Failed to create log directory {log_dir}: {e}"
        ) from e


def create_logger(
    name: str,
    log_level: LogLevels,
    show_time: bool = True,
    show_path: bool = True,
    markup: bool = True,
    rich_tracebacks: bool = True,
    show_task_context: bool = True,
    output_to_file: bool = False,
    log_dir: Path | None = None,
) -> RichLogger:

    file_handlers: list[FileHandlerSpec] = []
    if output_to_file:
        assert log_dir is not None
        file_handlers = [
            FileHandlerSpec(
                handler_type=FileHandlerTypes.FILE,
                config=FileHandlerSettings(
                    filename=str(log_dir),
                    mode="w",
                ),
            )
        ]
    
    if output_to_file and log_dir is not None:
        create_log_file(log_dir)
    
    return Log.create_logger(
           name=name,
           log_level=log_level,
           console_handler_type=ConsoleHandlers.RICH,
           handler_config=RichHandlerSettings(
               show_time=show_time,
               show_path=show_path,
               markup=markup,
               rich_tracebacks=rich_tracebacks,
               show_task_context=show_task_context,
               task_context_format="[{task_name}] ",
               task_context_style="cyan",
           ),
           file_handlers=file_handlers,
       )