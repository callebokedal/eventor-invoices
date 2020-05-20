#!/usr/bin/env node
require('dotenv').config()
const puppeteer = require('puppeteer-core')
const rules = require('./lib/rules')
const helper = require('./lib/helpers')

const argv = require('yargs')
  .usage('$0 [args]')
  .option('batch_id', {
    alias: 'b',
    type: 'number',
    describe: 'Invoice batch id'
  })
  .option('debug', {
    alias: 'd',
    type: 'boolean',
    default: false,
    describe: 'For debug mode. Default \'false\''
  })
  .option('short', {
    alias: 's',
    type: 'boolean',
    default: true,
    describe: 'I only first overview screen. Default \'true\''
  })
  .option('count', {
    alias: 'c',
    type: 'number',
    default: -1,
    describe: 'Decides how many items to operate on, and then cancelling the job'
  })
  .demandOption(['batch_id'], 'Please provide batchid')
  .example("$0 -b 1234", "Excute script for batch id '1234'")
  //.epilogue('for more information, find our manual at http://example.com')
  .help()
  .argv

// Get arguments
const batchId = argv.batch_id; // Id of Invoice batch - found on page https://eventor.orientering.se/Invoicing/PersonInvoiceBatches?organisationId=321. Hover "Redigera"
const isDebug = argv.debug;
const isShort = argv.short;
let invoiceId = argv.invoice_id;
let limit = argv.count || 0;
let allPersonsAmount = 0; // Total amount for all persons
let allPersonsDiscount = 0; // Total discount for all persons

// Pages
// ; makes difference here... why?
const url_login = "https://eventor.orientering.se/Login";
const url_club_invoice_overview = "https://eventor.orientering.se/Invoicing/PersonInvoiceBatches?organisationId=321";
const url_invoice_batch_overview="https://eventor.orientering.se/Invoicing/EditPersonInvoiceBatch/";
const page_domain = "eventor.orientering.se";
 
(async () => {

  const startTime = new Date().getTime()
  const browser = await puppeteer.launch({
    //headless: false,
    executablePath: '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome' // This must match your local installation of Chrome
  });
  const page = await browser.newPage();
  // page.on('console', msg => console.log("browser: " + msg.text())); // Works but much noise
  await page.setViewport({ width: 600, height: 400 })
  await page.setCookie({name:"cookieconsent_status", value: "dismiss", domain: page_domain}, {name:"culture", value:"sv-SE", domain: page_domain});

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
    const name = await page.$eval("#userInfoLink span:nth-child(1)", el => el.innerText)
    helper.debug("Logged in as: " + name)

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

    // Goto Invoice overview page
    await page.goto(url_invoice_batch_overview + batchId); 

    let title = await page.$eval("#entryOverview h3", el => el.innerText)
    helper.log("Fakturautskick: " + title)  

    // ## Go to page with invoice batches ("Fakturautskick")
    const invoiceBatchOverview = await page.evaluate(() => {

      let delta = 0
      let cols = document.querySelectorAll("#invoices thead th").length
      if(cols > 8){
        delta = 1
      }

      return Array.from(document.querySelectorAll('#invoices tbody tr'))
          .map(row => ({
            person: row.querySelector('td:nth-child(' + (1+delta) + ')').innerText.trim(),
            href: row.querySelector('td:nth-child(' + (1+delta) + ') a').href,
            age: row.querySelector('td:nth-child(' + (2+delta) + ')').innerText,
            email: row.querySelector('td:nth-child(' + (3+delta) + ') img').getAttribute("title"),
            status: row.querySelector('td:nth-child(' + (5+delta) + ')').innerText,
            rows: row.querySelector('td:nth-child(' + (6+delta) + ')').innerText,
            amount: row.querySelector('td:nth-child(' + (7+delta) + ')').innerText.replace(" SEK",""),
            totalBatchAmount: document.querySelector('tfoot th:nth-child(' + (7+delta) + ')').innerText.replace(" SEK","")
          })
        )
    })

    // Total Batch amount
    helper.log("Belopp: " + invoiceBatchOverview[0].totalBatchAmount)

    // Summarize
    let timestamp = helper.timestamp();
    if(!isShort) {
      helper.log("= Result [" + timestamp + "] ".padEnd(120,"="))
    }
    const sep = " | "
    invoiceBatchOverview.forEach((item, idx, array) => {
      if(isShort) {
        // More compact overview
        helper.log(item.person.padEnd(25) + item.rows.padStart(3) + sep + (""+item.amount).padEnd(4)) 
      } else {
        helper.log(item.person.padEnd(25) + sep + item.age.padStart(2) + sep + item.email.padEnd(40) + sep + /*item.href.padStart(4) + sep + */ item.status.padEnd(20) + sep + item.rows.padStart(3) + sep + (""+item.amount).padEnd(4)) 
      }
    })

    if(!isShort) {
      let batches = invoiceBatchOverview.length
      if(limit > 0) {
        batches = Math.min(limit, batches) 
      }
      for (var j = 0; j < batches; j++) {
        //helper.log(invoiceBatchOverview[j].href)
        await page.goto(invoiceBatchOverview[j].href)

        let jsmodel = await page.evaluate(() => window.model)
        //helper.log(jsmodel)
        let items = jsmodel.items

        let len = items.length
        for (var i = 0; i < len; i++) {
          //helper.log(items[i].text + ". Amount: " + items[i].amount + ", fee: " + items[i].fee + ", lateFee: " + items[i].lateFee + ", status: " + items[i].status)
          helper.log(items[i].text + "| amount: " + items[i].amount + "| fee: " + items[i].fee + "| lateFee: " + items[i].lateFee + "| status: " + items[i].status)
        }

        await page.goBack() // Much faster than "cancel"
        /*let [cancel] = await Promise.all([
          page.waitForNavigation("#entryOverview"),
          page.click("#editPersonInvoice form a")
        ]);*/
      } 
    }

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