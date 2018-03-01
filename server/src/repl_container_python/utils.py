import asyncio
import pathlib


def write_source_files(dir_path, data):
    """Write files found in `data` to a directory.

    Args:
      dir_path: a `pathlib.Path` referring to the directory into which to write
        the files. This must exist.
      data: a dict of information received as the JSON data of REPL creation
        POST. This function looks for entries in that specify source code files
        and writes those files to the currently configured temporary direction.
        The REPL will be directed to run in that directory.
    """

    # This converts the request data of the form [{'name': ..., 'value':
    # ...}] to a dict of the form {'filename': 'contents'}
    FILE_PREFIX = 'file_content['
    files = {entry['name'][len(FILE_PREFIX):-1]: entry['value']
             for entry in data
             if entry['name'].startswith(FILE_PREFIX)}

    # Now we actually write the files
    for filename, contents in files.items():
        filepath = dir_path / filename
        with filepath.open(mode='wt') as handle:
            handle.write(contents)


async def run_setup_py(dir_path):
    """Run setup.py in `dir_path` if one exists.
    """

    setup_path = dir_path / 'setup.py'
    if not setup_path.exists():
        return

    proc = await asyncio.subprocess.create_subprocess_exec(
        'python3', 'setup.py', 'install',
        cwd=str(dir_path))

    # TODO: What about the output from compilation? How can we communicate
    # that the user?
    await proc.wait()
