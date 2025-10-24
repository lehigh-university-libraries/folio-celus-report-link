import logging
import os
import requests
import time

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

BASE_URL = "https://k5.celus.net/api"

JOB_STATUS_NOT_STARTED = 0
JOB_STATUS_RUNNING = 1
JOB_STATUS_FINISHED = 2


class Celus:

    def __init__(self, config):
        self.init_config(config)
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self.api_key}",
        }
        pass

    def init_config(self, config):
        self.init_config_item(config, "Celus", "api_key")
        self.init_config_item(config, "Celus", "load_report_timeout", "int")
        self.init_config_item(config, "Celus", "load_report_delay", "int")

    def init_config_item(self, config, section, key, valueType="str"):
        value = config.get(section, key)
        if valueType == "int":
            value = int(value)
        setattr(self, key, value)

    def generate_report(self, report_id, start_date, end_date):
        # Start the report export
        report_data = self.start_export(report_id, start_date, end_date)
        if not report_data:
            return None
        if report_data.get("status") == JOB_STATUS_FINISHED:
            return report_data
        export_id = report_data.get("pk")

        # Retry periodically until the report is ready
        start_time = time.time()
        while time.time() - start_time < self.load_report_timeout:
            report_data = self.check_export_status(export_id)
            if not report_data:
                return None
            if report_data.get("status") == JOB_STATUS_FINISHED:
                return report_data

            # Pause an try again, if time timeout won't be reached
            if (
                time.time() - start_time + self.load_report_delay
                < self.load_report_timeout
            ):
                logger.info("Waiting before trying again.")
                time.sleep(self.load_report_delay)
            else:
                break

        logger.error("Timed out waiting for report to complete")
        return None

    def start_export(self, report_id, start_date, end_date):
        logger.info("Start export")
        try:
            payload = {
                "report": report_id,
                "start_date": start_date,
                "end_date": end_date,
                "file_format": "XLSX",
            }
            response = requests.post(
                BASE_URL + "/reporting-export/", json=payload, headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            report_data = self.parse_response_data(data)
            return report_data

        except requests.exceptions.RequestException as e:
            logger.exception("Exception generating report.")
            return None

    def check_export_status(self, export_id):
        logger.info("Check export status")
        response = requests.get(
            BASE_URL + "/reporting-export/" + str(export_id) + "/", headers=self.headers
        )
        response.raise_for_status()
        data = response.json()
        report_data = self.parse_response_data(data)
        return report_data

    def parse_response_data(self, response_data):
        report_data = None
        if not isinstance(response_data, list):
            report_data = response_data
        else:
            for item in response_data:
                # why am I getting multiple results?  What is the order?
                # if item.get("report") == report_id:
                report_data = item
                break
        if not report_data:
            logger.error("Could not start generating report.")
            return None

        return report_data
