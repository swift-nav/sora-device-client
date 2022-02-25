from . import keaclient
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

  keaclient.show_log_output(verbose=args.verbose, debug=args.debug)
  logger = logging.getLogger("KeaClient")

  config = confuse.Configuration('keaclient', keaclient.__name__)
  if args.config:
    try:
      config.set_file(args.config)
    except confuse.exceptions.ConfigReadError:
      sys.exit(f"Configuration file not found: {args.config}")
  config.set_env()
  config.set_args(args)

  config['host'].add(keaclient.DEFAULT_HOST)
  config['port'].add(keaclient.DEFAULT_PORT)

  client = keaclient.KeaClient(
    device_id=config['device-id'].get(),
    host=config['host'].get(),
    port=config['port'].as_number()
  )
  client.start()

  from sbp.client.drivers.network_drivers import TCPDriver
  from sbp.client import Handler, Framer
  from sbp.navigation import SBP_MSG_POS_LLH

  tcp_host = config['sources']['tcp']['host'].get()
  tcp_port = config['sources']['tcp']['port'].get()
  logger.info(f"Using TCP source {tcp_host}:{tcp_port}")
  FIX_MODES = ['Invalid','SPP','DGNSS','Float RTK','Fixed RTK','Dead Reckoning','SBAS Position']
  with TCPDriver(tcp_host, tcp_port) as driver:
        with Handler(Framer(driver.read, None, verbose=True)) as source:
            try:
                for msg, metadata in source.filter(SBP_MSG_POS_LLH):
                    state = {
                      'n_sats': msg.n_sats,
                      'h_accuracy': msg.h_accuracy,
                      'v_accuracy': msg.v_accuracy,
                      'flags': msg.flags,
                      'fix_mode': msg.flags & 3,
                      'fix_mode_str': FIX_MODES[msg.flags & 3],
                    }
                    client.send_state(
                      state,
                      lat=msg.lat,
                      lon=msg.lon,
                    )
            except KeyboardInterrupt:
                pass

  state = {"i": 0}
  LAT0 = 37.7911485304507
  LON0 = -122.3956400156021
  RADIUS = 0.01
  RAD_PER_STEP = 6/360.0
  while False:
      client.send_state(
        state,
        lat=LAT0 + RADIUS*math.cos(state["i"]*RAD_PER_STEP),
        lon=LON0 + RADIUS*math.sin(state["i"]*RAD_PER_STEP),
      )
      state["i"] += 1
      time.sleep(1)
