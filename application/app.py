from configparser import ConfigParser
from flask import (
    Flask,
    make_response,
    request,
)
import os
import logging

from application.celus import Celus

celus = None
config = None


def create_app():
    global celus

    app = Flask(__name__)
    init_config()
    celus = Celus(config)
    return app


def init_config():
    global config
    config = ConfigParser()
    dir = os.path.dirname(__file__)
    dir = os.path.dirname(dir)
    config_path = os.path.join(dir, "config", "config.properties")
    with open(config_path, "r", encoding="utf-8") as f:
        config.read_file(f)


app = create_app()


@app.route("/report", methods=["GET"])
def get_report():
    report_id = request.args.get("id")
    from_date = request.args.get("from")
    to_date = request.args.get("to")

    report_data = celus.generate_report(report_id, from_date, to_date)
    if not report_data:
        return make_response("Could not generate report", 400)
    response_fields = ["report", "start_date", "end_date", "output_file", "error_info"]
    response_data = {
        field: report_data[field] for field in response_fields if field in report_data
    }
    error = response_data.get("error_info")
    if error and error.get("code"):
        response_code = 400
    else:
        response_code = 200
    return make_response(response_data, response_code)


@app.route("/healthcheck")
def healthcheck():
    return "OK"


class HealthCheckFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("healthcheck") == -1


# Remove /healthcheck from application server logs
logging.getLogger("gunicorn.access").addFilter(HealthCheckFilter())
