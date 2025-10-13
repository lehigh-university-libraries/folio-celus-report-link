# FOLIO CELUS Report Link

**Work in progress**

## Data Preparation

* Electronic Resources Librarian creates a CELUS report for each (needed) FOLIO agreement.
* ERL stores the CELUS "report ID" in a supplementary property field of the agreement.

## Functionality

* When viewing the agreement in FOLIO, this tool adds a menu item that 
  * prompts the user for a date range, and then
  * generates and returns a link to the CELUS report.

## Architecture

* A python microservice takes the report ID and date range, calls the CELUS API and returns the report link.
* A TamperMonkey script integrates the menu item into the FOLIO UI.
