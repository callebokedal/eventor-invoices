#!/usr/bin/env node
//'use strict'
const fs = require('fs')
const util = require('util')
require('dotenv').config()
const puppeteer = require('puppeteer-core')
const rules = require('./lib/rules')
const helper = require('./lib/helpers')

// The purpose is to download all invoices to enable post processing
// It does not download anything, but logs invoice details that can be saved as data (so download via log/introspection)
// Export to Excel does not work according to tests in Both Firefox and Chrome (2022-12-07)

const argv = require('yargs')
  .usage('$0 [args]')
  .option('batch_id', {
    alias: 'b',
    type: 'number',
    default: 0,
    describe: 'Invoice batch id'
  })
  .option('invoice_id', {
    alias: 'i',
    type: 'number',
    default: 0,
    describe: 'Invoice id for a specific person'
  })
  .option('test', {
    alias: 't',
    type: 'boolean',
    default: false,
    describe: 'Flag for test mode. If present - no data will be saved in Eventor, only logs written to stdout'
  })
  .option('count', {
    alias: 'c',
    type: 'number',
    default: -1,
    describe: 'Decides how many items to operate on, and then cancelling the job'
  })
  .option('reset', {
    alias: 'r',
    type: 'boolean',
    default: false,
    describe: 'If to reset/clear internal note on each invoice or not. Default \'false\''
  })
  .demandOption(['batch_id'], 'Please provide batchid')
  .example("$0 -b 1234", "Excute script for all invoices in batch id '1234'")
  .example("$0 -b 1234", "Excute script for batch id '1234'")
  .epilogue('for more information, find our manual at http://example.com')
  .help()
  .argv

// Get arguments
const batchId = argv.batch_id;// Id of Invoice batch - found on page https://eventor.orientering.se/Invoicing/PersonInvoiceBatches?organisationId=321. Hover "Redigera"
const test = argv.test;
let invoiceId = argv.invoice_id;
let limit = argv.count || 0;
//let allPersonsAmount = 0; // Total amount for all persons
//let allPersonsDiscount = 0; // Total discount for all persons
const resetNote = argv.reset;

if(test) {
  helper.log("### Test - inget sparas, endast loggning ".padEnd(120, "#"))
}

const settingsFile = '.env';
fs.access(settingsFile, fs.constants.F_OK | fs.constants.R_OK, (err) => {
  if (err) {
    console.error("Settings file '.env' is missing. See Readme file");
    process.exit(1);
  } 
});

// Pages
// ; makes difference here... why?
const url_login = "https://eventor.orientering.se/Login";
const url_club_invoice_overview = "https://eventor.orientering.se/Invoicing/PersonInvoiceBatches?organisationId=321";
const page_domain = "eventor.orientering.se";
//const text_discount_title = "Vänligen ange fakturanummer vid inbetalning och betala respektive faktura separat - tack!\nSubventioner från Sjövalla FK Orientering:"
//const text_discount = "Subvention från Sjövalla FK Orientering"; // Note! Changing this text makes upcoming executions missmatch previous runs
//const text_automated = "Automatiserad uppdatering";
 
(async () => {

  const startTime = new Date().getTime()
  let browser;
  let browser_path = process.env.BrowserPath || '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome';
  // console.log("Browser path:", browser_path);
  try {
    browser = await puppeteer.launch({
      //headless: false,
      // Executable path must match your local installation of Chrome - configure your .env file accordingly
      executablePath: browser_path 
    });
  } catch (e) {
    console.error("Unable to launch browser!", e);
    process.exit(1);
  }
  const page = await browser.newPage();
  //page.on('console', msg => console.log("browser: " + msg.text())); // Works but much noise
  await page.setViewport({ width: 1200, height: 800 })
  await page.setCookie(
    {name:"cookieconsent_status", value: "dismiss", domain: page_domain}, 
    {name:"culture", value:"sv-SE", domain: page_domain});

  var cancel = async function(msg) {
    console.log("Cancelling - " + msg);
    await browser.close();
  }

  try {

    // Block images
    await page.setRequestInterception(true);
    page.on('request', request => {
      if (request.resourceType() === 'image' || request._url.startsWith("https://quantcast.mgr.consensu.org") ) {
        request.abort();
      } else {
        request.continue();
      }
    });

    // Login page
    await page.goto(url_login);
    // Insert login credentials - from file '.env' via module 'dotenv'
    helper.debug("Log in as: " + process.env.PersonUsername);
    await page.type("#PersonUsername", process.env.PersonUsername); 
    await page.type("#PersonPassword", process.env.PersonPassword);
    const [response] = await Promise.all([
      page.click("input[name='PersonLogin']"),
      page.waitForNavigation("#userInfoLink")
    ]);
    const user = await page.$eval("#userInfoLink span:nth-child(1)", el => el.innerText)
    helper.debug("Logged in as: " + user)

    //await page.screenshot({path: "loggedin.png"})

    // Utility function to get id for URL of format
    // <anything>/<id>
    // Ex:
    // https://eventor.orientering.se/Invoicing/EditPersonInvoice/12345 -> 12345
    const getIdFromURL = function(href) {
      let lastSlash = href.lastIndexOf("/");
      if(lastSlash > -1) {
        return href.substr(lastSlash+1);
      }
      return 0 // Fallback
    }

    // ## Go to page with invoice batches ("Fakturautskick")
    await page.goto(url_club_invoice_overview); 
    const invoiceBatches = await page.evaluate(() => 
        Array.from(document.querySelectorAll('#invoices tbody tr'))
          .map(row => ({
            title: row.querySelector('td:nth-child(1)').innerText.trim(),
            startDate: row.querySelector('td:nth-child(2)').innerText,
            endDate: row.querySelector('td:nth-child(3)').innerText,
            competitions: row.querySelector('td:nth-child(4)').innerText,
            members: row.querySelector('td:nth-child(5)').innerText,
            amount: row.querySelector('td:nth-child(6)').innerText,
            href: row.querySelector('td:nth-child(7) a').href,
            id: (function(href) {
              let lastSlash = href.lastIndexOf("/");
              if(lastSlash > -1) {
                return parseInt(href.substr(lastSlash+1));
              }
              return 0 // Fallback
            })(row.querySelector('td:nth-child(7) a').href)
          }))
    )
    helper.log("Found batches: ", invoiceBatches)

    // Now navigate to chosen invoice batch
    function findBatchId(batchItem) {
      return batchItem.id == batchId;
    }
    const batchItemById = invoiceBatches.find(findBatchId);
    if(!batchItemById) {
      cancel("Invoice batch item not found for: " + batchId);
      return;
    }
    helper.debug("Work with batch id: " + batchItemById.href)

    // Start batch job
    helper.log(("= Fakturautskick '" + batchItemById.title + "' ").padEnd(120,"="))
    helper.log("Tävlingar: " + batchItemById.competitions)
    helper.log("Medlemmar: " + batchItemById.members)
    helper.log("Från: " + batchItemById.startDate)
    helper.log("Till: " + batchItemById.endDate)
    helper.log(batchItemById.href)

    await page.goto(batchItemById.href);

    // ## Get personal invoices
    // window.model.items.forEach((el, idx) => {console.log(el.text + " " + el.fee)})
    
    // For debugging
    page.on('console', (msg) => {
      if(msg._type !== "error") {
        //console.log('PAGE LOG:', msg._text)
      }
    });

    let invoiceList = await page.evaluate(() => {
      // Depending on invoice status, number of columns differ between 8-9
      let delta = 0
      let cols = document.querySelectorAll("#invoices thead th").length
      if(cols > 8){
        delta = 1
      }

      return Array.from(document.querySelectorAll('#invoices tbody tr'))
        //.map((row, fo, ary, delta) => ({
        //  debug: ((row, foo, delta) => {
        .map((row) => ({
          debug: ((row, delta) => {
            //console.log("s")
            //console.log("delta: " + delta)
            //console.log(row.getAttribute("data-payment-status"))
            //console.log(row.querySelector('td:nth-child(' + (1+delta) + ') a').innerText)
          })(row, delta),
          paymentStatus: row.getAttribute("data-payment-status"),
          name: row.querySelector('td:nth-child(' + (1+delta) + ') a').innerText,
          href: row.querySelector('td:nth-child(' + (1+delta) + ') a').href,
          age: parseInt(row.querySelector('td:nth-child(' + (2+delta) + ')').innerText),
          email: row.querySelector('td:nth-child(' + (3+delta) + ') img').getAttribute("title"),
          invoiceNumber: row.querySelector('td:nth-child(' + (4+delta) + ')').innerText,
          status: row.querySelector('td:nth-child(' + (5+delta) + ')').innerText,
          rows: parseInt(row.querySelector('td:nth-child(' + (6+delta) + ')').innerText),
          amount: row.querySelector('td:nth-child(' + (7+delta) + ')').innerText,
          invoiceId: (function(href) {
            let lastSlash = href.lastIndexOf("/");
            if(lastSlash > -1) {
              return parseInt(href.substr(lastSlash+1));
            }
            return 0 // Fallback
          })(row.querySelector('td:nth-child(' + (1+delta) + ') a').href)
        }))
    })

    let timestamp = helper.timestamp();
    helper.log("Tidpunkt: " + timestamp);
    helper.log("Användare: " + user);

    //helper.log("invoiceId: " + invoiceId + ", " + invoiceList.length)
    //helper.log(JSON.stringify(invoiceList))
    if(invoiceId) {
      // Handle case when invoiceId is an argument...
      let invoice = invoiceList.find((item) => {return item.invoiceId == invoiceId})
      //helper.log(invoice)

      if(invoice === undefined) {
        console.log("Invoice with id '" + invoiceId + "' not found!")
        invoiceList = []
      } else {
        // Reduce list to one item
        invoiceList = new Array( invoice )
        console.log("Invoice with id '" + invoiceId + "' found!")
      }

    }

    let l = invoiceList.length
    if(limit > 0) {
      l = Math.min(limit, invoiceList.length) 
    }
    //let all_invoices = {}
    for (var i = 0; i < l; i++) {
      invoiceId = invoiceList[i].invoiceId
      
      if(invoiceId != 0) {
        //let invoiceItemById = item //invoiceList.find(function(item){return item.invoiceId == invoiceId});
        let invoiceItemById = invoiceList.find(function(item){return item.invoiceId == invoiceId});

        helper.debug(invoiceItemById)

        // Go to this specific invoice
        await page.goto(invoiceItemById.href);

        // Keep track of time
        let currentTime = new Date().getTime()

        // This Eventor page operates on the javascript object 'windows.model'
        let jsmodel = await page.evaluate(() => window.model);
        //helper.log(typeof(jsmodel));
        //console.log(jsmodel);
        //console.dir(jsmodel);
        //helper.log("invoiceId: "+ invoiceId + "\n", jsmodel);
        
        
        //console.dir(jsmodel, { depth: null }); // Funkar
        //console.log(util.inspect(jsmodel, { depth: null, compact: true }));
        //all_invoices["invoiceId-"+invoiceId] = JSON.parse (util.inspect(jsmodel, { depth: null, compact: true }).replace(/\n/g,""));
        //data = JSON.stringify(util.inspect(jsmodel, { depth: null, compact: true }));
        //jsmodel["test1"] = "Testing1";
        //extraObj = {"etxra":true};
        //helper.log("extra before", extraObj);

        // Add other data to object
        var invoiceDetails = await page.evaluate(async (data) => {
          console.log("data in", data)
          function getPageDetails(data) {
              console.log("data in function", data)
              return new Promise((resolve, reject) => {
                data["e-mail"] = document.querySelector("#editPersonInvoice fieldset div span").innerText;
                data["invoiceNo"] = document.querySelector("#editPersonInvoice fieldset ul li:nth-of-type(6) span").innerText;
                data["created"] = document.querySelector("#editPersonInvoice fieldset ul li:nth-of-type(7) span").innerText;
                data["amount"] = window.ko.dataFor(document.querySelector("#InvoiceInformation")).amountString();
                // Return result
                resolve(data);
            });
          }
          var returnObj = await getPageDetails(data);
          //console.log("data out", returnObj)
          return returnObj;

        }, {/* input can be added here... */});
        //helper.log("extra after", extraObj);
        //helper.log("invoiceDetails", invoiceDetails);

        jsmodel["invoiceDetails"] = invoiceDetails;
        data = JSON.stringify(jsmodel);

        helper.log(data);
        //all_invoices["invoiceId-"+invoiceId] = data;
      } // If 
    }
    //helper.log(all_invoices);

    let timeDiff = helper.timediffMS(startTime)
    helper.log("Tid: " + timeDiff.m + " minuter, " + timeDiff.s + " sekunder")
    helper.log(" Slut rapport =".padStart(120,"="))
  }
  catch (e) {
    if (e instanceof puppeteer.errors.TimeoutError) {
      // Do something if this is a timeout.
      console.log("Timeout Error")
    } else {
      // Other error
      console.log(e);
    }
  }
  await browser.close();

})();