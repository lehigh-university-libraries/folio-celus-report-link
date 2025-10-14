// ==UserScript==
// @name         FOLIO CELUS Report Link
// @namespace    http://lts.lehigh.edu/
// @version      2025-10-14a
// @description  Open a link to a CELUS report within a FOLIO Organization
// @author       You
// @match        https://*.folio.indexdata.com/erm/agreements/*
// @connect      localhost
// @icon         https://www.google.com/s2/favicons?sz=64&domain=undefined.localhost
// @grant        GM_xmlhttpRequest
// ==/UserScript==

(function () {
    'use strict';

    const exportAgreementButtonId = 'clickable-dropdown-export-agreement';
    const celusReportButtonId = 'clickable-dropdown-generate-celus-report';

    const addButton = () => {
        const exportAgreementButton = document.getElementById(exportAgreementButtonId);
        const generateReportButton = exportAgreementButton.cloneNode(true);
        generateReportButton.id = celusReportButtonId;
        const label = generateReportButton.querySelector('span > span > span');
        label.innerText = 'Export CELUS report (XLS)';
        generateReportButton.addEventListener("click", showDialog);
        const reportId = getReportId();
        if (reportId == null) {
            generateReportButton.disabled = true;
        }
        exportAgreementButton.insertAdjacentElement('afterend', generateReportButton);
        console.log("Added CELUS Report button")
    };

    const runOnDescendant = (node, targetId, targetFunction) => {
        if (node.id === targetId) {
            targetFunction();
        }
        node.childNodes.forEach((child) => runOnDescendant(child, targetId, targetFunction));
    };

    const observer = new MutationObserver((mutationsList, observer) => {
        for (const mutation of mutationsList) {
            for (const addedNode of mutation.addedNodes) {
                if (addedNode.nodeType === Node.ELEMENT_NODE) {
                    runOnDescendant(addedNode, exportAgreementButtonId, addButton);
                }
            }
        }
    });
    observer.observe(document.body, { childList: true, subtree: true });

    const buildInputDialog = () => {
        const stylesTemplate = document.createElement('template');
        stylesTemplate.innerHTML = `
          <style>
            .generate-celus-report-dialog {
              h1 {
                margin-top: 0;
              }
              div {
                margin-top: 1rem;
              }
              label {
                 display: inline-block;
                 min-width: 50px;
            }
          </style>
        `.trim();
        document.head.append(stylesTemplate.content.cloneNode(true));

        const template = document.createElement('template');
        template.innerHTML = `
        <dialog class="generate-celus-report-dialog" closedby="any">
            <!-- <form class="lehigh-form" method="dialog"> -->
                <h1>Generate CELUS Report</h1>
                <div>
                    <label for="celus-from">From:</label>
                    <input type="date" id="celus-from"/>
                </div>
                <div>
                    <label for="celus-from">To:</label>
                    <input type="date" id="celus-to"/>
                </div>
                <div>
                    <input type="submit" class="celus-submit-button" value="Generate"/>
                </div>
                <div class="celus_output">
                </div>
            <!--
            </form>
            -->
        </dialog>
        `.trim();
       document.body.append(template.content.cloneNode(true));

       document.querySelector('.celus-submit-button').addEventListener('click', () => {
           const reportId = getReportId();
           const fromDate = document.getElementById('celus-from').value;
           const toDate = document.getElementById('celus-to').value;
           GM_xmlhttpRequest({
               method: "GET",
               url: `http://localhost:8080/report?id=${reportId}&from=${fromDate}&to=${toDate}`,
               responseType: "json",
               onload: (response) => {
                   if (response.status == 200) {
                       const data = response.response;
                       const outputFile = data.output_file;
                       const link = document.createElement('a');
                       link.innerText = 'Download Report';
                       link.setAttribute('href', outputFile);
                       document.querySelector('.celus_output').append(link);

                       document.querySelector('.celus-submit-button').disabled = true;
                   }
               },

           });
       });
    };

    const showDialog = () => {
        document.getElementById('celus-from').value = '';
        document.getElementById('celus-to').value = '';
        document.querySelector('.celus-submit-button').disabled = false;
        document.querySelector('.celus_output').innerHTML = '';

        document.querySelector('.generate-celus-report-dialog').showModal();
    };

    const getReportId = () => {
        const section = document.getElementById("supplementaryProperties-accordion-Usage Reporting");
        if (section == null) {
            console.log("No usage reporting id.");
            return null;
        }
        const reportId = section.querySelector('div[data-test-kv-value="true"]').innerHTML;
        return reportId;
    };

    buildInputDialog();
})();
