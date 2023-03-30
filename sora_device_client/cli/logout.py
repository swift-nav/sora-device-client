# Copyright (C) 2022 Swift Navigation Inc.
# Contact: Swift Navigation <dev@swiftnav.com>

# This source is subject to the license found in the file 'LICENCE' which must
# be be distributed together with this source. All other rights reserved.

from ..config import delete_data_file


def logout() -> None:
    """
    Log the device out of Sora Server.
    """
    delete_data_file()
