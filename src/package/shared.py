import os
from pathlib import Path

from joblib import dump


def export_directory_path(filename):
    """ Get or create export directory """

    project_root = Path(__file__).parent.parent.parent
    export_directory = os.path.join(project_root, r'export')
    if not os.path.exists(export_directory):
        os.makedirs(export_directory)

    return os.path.join(export_directory, filename)


def serialize_object(to_serialize, name):
    """ Serialize object with joblib """

    export_directory = export_directory_path(f'{name}.joblib')
    print(f'Location: {export_directory}')

    dump(to_serialize, export_directory)
