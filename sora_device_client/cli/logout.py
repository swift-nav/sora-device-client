from ..config import delete_data_file


def logout() -> None:
    """
    Log the device out of Sora Server.
    """
    delete_data_file()
