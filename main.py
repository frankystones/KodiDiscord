import requests
import time

from src.custom_logger import logger
from src.rpc import fetch_info, fetch_length, update_rp

"""
This file contains the main function of the program. Run this to start the program.
"""


def main():
    try:
        with requests.Session() as session:
            last_info, last_length = None, None
            while True:
                info = fetch_info(session)
                length = fetch_length(session)
                logger.debug(f"Fetched info: {info}")
                logger.debug(f"Fetched length: {length}")
                if info is not None and length is not None:
                    if info != last_info or length != last_length:
                        update_rp(info, length)
                        last_info, last_length = info, length
                    else:
                        time.sleep(3)  # Pause for 3 seconds if there's no new information
    except KeyboardInterrupt:
        logger.info("Program interrupted by user. Exiting...")

if __name__ == "__main__":
    main()