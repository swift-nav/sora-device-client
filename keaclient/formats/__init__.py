import logging
import confuse

logger = logging.getLogger("KeaClient")

def sbp_format_from_config(driver):
  from sbp.client import Handler, Framer
  return Handler(Framer(driver.read, None, verbose=True))

FORMATS = {
  "sbp": sbp_format_from_config,
}

def format_from_config(config, driver):
  format = config['format'].as_choice(FORMATS.keys())
  return FORMATS[format](driver)
