import os


def create_dir_in_current_folder(dirname: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    result_dir_path = os.path.join(current_dir, dirname)
    if not os.path.exists(result_dir_path):
        os.mkdir(result_dir_path)
