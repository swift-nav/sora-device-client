# Copyright (C) 2022 Swift Navigation Inc.
# Contact: Swift Navigation <dev@swiftnav.com>

# This source is subject to the license found in the file 'LICENCE' which must
# be be distributed together with this source. All other rights reserved.

import importlib.metadata

if not __package__:
    __version__ = "(local)"
else:
    __version__ = importlib.metadata.version(__package__)
