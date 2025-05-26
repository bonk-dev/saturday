import logging
from typing import AnyStr


def write_dump(filename: str, data: AnyStr, f_module: str, logger: logging.Logger):
    """
    Write the given data to a file, logging progress and any errors encountered.

    :param filename: Path to the file where data will be written.
    :type filename: str
    :param data: Data to be written to the file. Can be either str or bytes.
    :type data: AnyStr
    :param f_module: Name of the calling module or function, used in log messages.
    :type f_module: str
    :param logger: Logger instance used for informational and error messages.
    :type logger: logging.Logger

    :returns: None. Logs an informational message on success or an error message on failure.
    :rtype: None

    :note: This function catches any file‐related exceptions (e.g., PermissionError,
           IsADirectoryError, OSError) and logs the appropriate error rather than
           propagating them. If an error occurs, no exception is raised by this function.
    """

    logger.info(f'{f_module}: writing output to "{filename}"')
    try:
        with open(filename, 'w') as export_file:
            export_file.write(data)
    except PermissionError as e:
        logger.error(f'{f_module}: permission denied to output file: {e.filename}')
    except IsADirectoryError as e:
        logger.error(f'{f_module}: output file path "{e.filename}" is a directory')
    except OSError as e:
        logger.error(f'{f_module}: os error [{e.errno}] {e.strerror}')