from flask import (
    Flask,
    make_response,
    request,
)

from application.celus import Celus

celus = Celus()


def create_app():
    app = Flask(__name__)
    return app


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
