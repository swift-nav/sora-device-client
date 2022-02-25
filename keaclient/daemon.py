from . import client
from . import drivers
from . import formats
import time
import logging
import argparse
import confuse
import sys
import math

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("-c", "--config", help="Config file path")
  parser.add_argument("-i", "--device-id", help="Device ID")
  parser.add_argument("-v", "--verbose", help="Enable verbose output",
                    action="store_true")
  parser.add_argument("-d", "--debug", help="Enable debugging output",
                    action="store_true")
  parser.add_argument("-s", "--host", help="Kea server hostname")
  parser.add_argument("-p", "--port", help="Kea server port")
  args = parser.parse_args()

  client.show_log_output(verbose=args.verbose, debug=args.debug)
  logger = logging.getLogger("KeaClient")

  config = confuse.Configuration('keaclient', client.__name__)
  if args.config:
    try:
      config.set_file(args.config)
    except confuse.exceptions.ConfigReadError:
      sys.exit(f"Error: Configuration file not found: {args.config}")
  config.set_env()
  config.set_args(args)

  config['host'].add(client.DEFAULT_HOST)
  config['port'].add(client.DEFAULT_PORT)

  try:
    device_id = config['device-id'].get()
  except confuse.exceptions.NotFoundError:
    sys.exit("Error: Device ID must be specified")

  client = client.KeaClient(
    device_id=config['device-id'].get(),
    host=config['host'].get(),
    port=config['port'].as_number()
  )

  client.start()

  from sbp.navigation import SBP_MSG_POS_LLH

  FIX_MODES = ['Invalid','SPP','DGNSS','Float RTK','Fixed RTK','Dead Reckoning','SBAS']
  try:
    with drivers.driver_from_config(config) as driver:
          with formats.format_from_config(config, driver) as source:
              try:
                  for msg, metadata in source.filter(SBP_MSG_POS_LLH):
                      state = {
                        'n_sats': msg.n_sats,
                        'h_accuracy': msg.h_accuracy,
                        'v_accuracy': msg.v_accuracy,
                        'flags': msg.flags,
                        'fix_mode': msg.flags & 7,
                        'fix_mode_str': FIX_MODES[msg.flags & 7],
                      }
                      client.send_state(
                        state,
                        lat=msg.lat,
                        lon=msg.lon,
                      )
              except KeyboardInterrupt:
                  pass
  except confuse.exceptions.ConfigError as err:
    sys.exit(f'Error: {err}')
