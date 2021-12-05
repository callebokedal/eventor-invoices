#!/usr/bin/env node
//'use strict'
const fs = require('fs')
require('dotenv').config()
const puppeteer = require('puppeteer-core')
const rules = require('./lib/rules')
const helper = require('./lib/helpers')

const argv = require('yargs')
  //.scriptName("update_invoices")
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
let allPersonsAmount = 0; // Total amount for all persons
let allPersonsDiscount = 0; // Total discount for all persons
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
const text_discount_title = "Vänligen ange fakturanummer vid inbetalning och betala respektive faktura separat - tack!\nSubventioner från Sjövalla FK Orientering:"
const text_discount = "Subvention från Sjövalla FK Orientering"; // Note! Changing this text makes upcoming executions missmatch previous runs
const text_automated = "Automatiserad uppdatering";
 
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
    helper.debug("Found batches: ", invoiceBatches)

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
        helper.debug("jsmodel: \n", jsmodel)

        let outputNote = ""; // Note to add to invoice
        //const alreadyHandled = jsmodel.items.forEach((item) => {
        helper.log(("-[+]- Fakturanummer " + invoiceItemById.invoiceNumber + " --- [" + (i+1) +  "/" + l +  "] ").padEnd(120,"-"))
        helper.log(invoiceItemById.name + ", " + invoiceItemById.age + " år, " + invoiceItemById.email)
        helper.log(invoiceItemById.href)
        let alreadyProcessed = invoiceItemById.paymentStatus == "InvoiceSent" || invoiceItemById.paymentStatus == "InvoicePaid" 
        if(alreadyProcessed) {
          helper.log(" Redan behandlad -".padStart(120,"-"))

          let [cancel] = await Promise.all([
            page.waitForNavigation("#entryOverview"),
            page.click("#editPersonInvoice form a")
          ]);
           
        } else {


          // TODO: Logga allt i rapporten - då Eventor verkar ändra sina uppgifter över tid.

          // Due to a "bug" regarding events overlaping multiple days, these events repeat for each day, multiplying the invoice cost
          // Solution: 
          // - Test if multiple days exists. If so -> remove duplicated rows and keep only one row
          // TODO: Check amount > 200 kr -> bug is still there...
          // Eventor might fix this bug

          //let duplicatedRows = [] // Array with indexes of any duplicated rows to remove
          var newFeature = false; // To be able to toggle new feature on/off. https://stackoverflow.com/questions/46524997/return-value-from-page-evaluation-puppeteer-asnyc-programming
          // TODO: Not finished but something to work further on
          // Sync changes made in legacy version as well -> compare and see
          if (newFeature) {
            let lastObject = {text: "", amount: -1}
            const len = jsmodel.items.length
            for (let index = 0; index < len; index++) {
              let item = jsmodel.items[index]
              if(lastObject.text == item.text /*&& lastObject.amount == item.amount*/) {
                helper.log("[!] Found duplicate: " + item.text + ", " + item.id)

                // Set amount to 0, both in model and on page
                jsmodel.items[index].amount = 0
                jsmodel.items[index].fee = 0
                jsmodel.items[index].lateFee = 0
                var resultObj = await page.evaluate(async (text, index, sum_amount) => {

                  function doStuff(sum_amount) {
                      return new Promise((resolve, reject) => {
                        let dataItem = document.querySelector("#items tr:nth-child(" + index + ") input.textInput")
                        if(text == window.ko.dataFor(dataItem).text()) {
                          //window.ko.dataFor(dataItem).text("Dublett: " + index) // Set text
                          console.log("Found duplicate: " + window.ko.dataFor(dataItem).fee) 
                          // Save amount sum
                          sum_amount = sum_amount + parseFloat(window.ko.dataFor(dataItem).fee)
                          console.log("lastObject text, amount: " + text + ", " + sum_amount)
                          window.ko.dataFor(dataItem).amount(0) // Reduce amount to 0
                          window.ko.dataFor(dataItem).fee = 0 // Reduce amount to 0
                          window.ko.dataFor(dataItem).lateFee = 0 // Reduce amount to 0
                        }
                        // Return result
                        resolve({test: "foo", bar:3, sum_amount: sum_amount});
                    });
                  }

                  var returnObj = await doStuff(sum_amount);
                  return returnObj;

                }, item.text, (index+1), lastObject.amount) // JS start at 0, CSS at 1 => add 1

                console.log(resultObj)
              }
              // Store for next item verification
              lastObject.text = item.text
              lastObject.amount = parseFloat((item.amount+"").replace(",",".")) || 0
            }
          } else {
            // Legacy code
            let lastObject = {text: "", amount: -1}
            const len = jsmodel.items.length
            for (let index = 0; index < len; index++) {
              let item = jsmodel.items[index]
              /*
              2020-12-01 Disable since it is not necessary any longer? See GO-ringen 2020
  
              if(lastObject.text == item.text) {
                helper.log("[!] Found duplicate: " + item.text + ", " + item.id)

                // Set amount to 0, both in model and on page
                jsmodel.items[index].amount = 0
                jsmodel.items[index].fee = 0
                jsmodel.items[index].lateFee = 0
                await page.evaluate((text, index) => {
                  let dataItem = document.querySelector("#items tr:nth-child(" + index + ") input.textInput")
                  if(text == window.ko.dataFor(dataItem).text()) {
                    //window.ko.dataFor(dataItem).text("Dublett: " + index) // Set text
                    window.ko.dataFor(dataItem).amount(0) // Reduce amount to 0
                    window.ko.dataFor(dataItem).fee = 0 // Reduce amount to 0
                    window.ko.dataFor(dataItem).lateFee = 0 // Reduce amount to 0
                  }
                }, item.text, (index+1)) // JS start at 0, CSS at 1 => add 1
              }
              // Store for next item verification
              lastObject.text = item.text
              lastObject.amount = parseFloat((item.amount+"").replace(",",".")) || 0*/
            }
          }


          // Return object representing current rows discount status
          // function getDiscountStatus(rowText, age, fee, lateFee, status) {

          // Decide discount status for each row
          let discountInfo = []
          let discountRowIdx = -1
          jsmodel.items.forEach(function(item, index, array) {
            //discountInfo[index] = rules.getDiscountStatus(item.text, invoiceItemById.age, item.fee, item.lateFee, item.status)
            helper.debug("Count discount: " + item.text + ", " + invoiceItemById.age + " år, Att betela: " + item.amount + ", Avgift: " + item.lateFee + ", status: " + item.status)
            discountInfo[index] = rules.getDiscountStatus(item.text, invoiceItemById.age, item.amount, item.lateFee, item.status)
            //console.log("row: " + item.text)
            //console.log("test: " + (item.text == text_discount))
            if(item.text == text_discount) {
              discountRowIdx = index + 1 // JS start at 0, CSS at 1 => Add 1
            }
          })
          helper.debug("discount status: ", discountInfo)
          //helper.debug("idx: " + discountRowIdx + ", ary: " + jsmodel.items.length)

          if(discountRowIdx < 0) {
            // No discount row yet -> add
            discountRowIdx = jsmodel.items.length + 1 // 1 row to be added => Add 1
            //helper.debug("idx2: " + discountRowIdx)
            //console.log("Add discount row")
            let [add_row] = await Promise.all([
              page.click("#editPersonInvoice > button")
            ]);
          }

          let discountRowQuery = "#items tbody tr:nth-child(" + discountRowIdx + ") input.textInput"

          // Now:
          // - Calculate total discount
          // - Add row with total discount
          // - Add note with details for each row
          // - Log info 

          let totalAmount = discountInfo.reduce((total, item) => {return total + (parseFloat((item.amount+"").replace(",",".")) || 0)}, 0)
          let totalDiscount = discountInfo.reduce((total, item) => {return total + (parseFloat((item.discountAmount+"").replace(",",".")))}, 0)
          helper.debug("Total amount: " + totalAmount)
          helper.debug("Total discount: " + totalDiscount)

          /*if((totalAmount - totalDiscount) < 0) {
            helper.log("[!] Högre subvention än avgift: Avg. " + totalAmount + ", subv.: " + totalDiscount + ". Diff: " + (totalAmount - totalDiscount))
          }*/

          let invoiceResult = await page.evaluate((text_discount_title, text_discount, totalDiscount, totalAmount, discountInfo, discountRowQuery) => { 

            //let dataItem = document.querySelector("#items tbody tr:last-child input")
            let dataItem = document.querySelector(discountRowQuery)

            window.ko.dataFor(dataItem).text(text_discount) // Set text
            window.ko.dataFor(dataItem).amount(parseFloat(totalDiscount+"".replace(",",".")) * -1) // Set total discount

            //console.log("discountInfo:")
            //console.dir(JSON.stringify(discountInfo))
            
            let note = "" // Note to display on Invoice. Always all details in comparison to paperNote - that needs to fit the paper invoice
            let paperNote = "" // Shorter note on paper since not all lines can be added, for some cases
            discountInfo.forEach(function(item, index) {

              if(index == 0) {
                note += "# Aktivitet".padEnd(54) + "Subvention".padEnd(14) + "Avgift\n"
              }

              // Ex: {"valid":true,"fee":20,"lateFee":0,"discountAmount":8,"discountPercent":40,"invoiceNote":"GOFs Sommarserie Etapp 2","status":""}

              // Skip the row with discount amount on it
              if(text_discount != item.invoiceNote) { 
                let rowNote = "- " + (item.invoiceNote.trim() + ": ").padEnd(50) + (""+item.discountAmount).padStart(4) + (" kr (" + item.discountPercent + "%)").padEnd(11)
                //                                                                              
                if(!item.valid) {
                  rowNote += " (" + item.status + ")"
                }
                //rowNote += "\n"
                // Only update paperNote if all lines has place, and not the discount row itself
                if(index <= 15 && (text_discount != item.invoiceNote)) {
                  paperNote += rowNote.replace(/  /g," ") + "\n" // Remove padding spaces
                }
                note += rowNote + " [Avg.: " + (""+item.amount).replace(".5",",50").padStart(3) + " kr]" 
                //note += rowNote + " [Avg.: " + (""+item.fee).replace(".5",",50").padStart(3) + " kr]" 
                if(item.lateFee > 0) {
                  note += " [Efteranm.: " + (""+item.lateFee).replace(".5",",50").padStart(3) + " kr]" 
                }
                note += "\n"
              }
            })

            if(discountInfo.length > 15) {
              // Display additional info if all rows not in place
              paperNote += "(Alla subventioner får ej plats här men alla är inräknade i summeringen - se specifikation på nästa sida)\n"
            }
            paperNote += "Summa subventioner: " + (""+totalDiscount).replace(".5",",50").padStart(5) + " kr\n"
            note += "Summa subvention: " + (""+totalDiscount).replace(".5",",50").padStart(5) + " kr\n"
            // 2020-05-17 Comment out
            //note += "Summa att betala: " + (""+totalAmount).replace(".5",",50").padStart(5) + " kr\n"

            // 2020-05-19
            note += "Summa att betala: " + window.ko.dataFor(document.querySelector("#InvoiceInformation")).amountString() + "\n"

            //note += "Summa att betala:        " + (""+(totalAmount - totalDiscount)).replace(".5",",50").padStart(5) + " kr (för aktuell faktura)\n"

            // Update note on invoice
            window.ko.dataFor(document.querySelector("#InvoiceInformation")).invoiceInformation(text_discount_title + "\n" + paperNote)
            return {note: note, totalAmount: totalAmount, totalDiscount: totalDiscount}

          }, text_discount_title, text_discount, totalDiscount, totalAmount, discountInfo, discountRowQuery)
          helper.log(invoiceResult.note)

          allPersonsAmount += invoiceResult.totalAmount
          allPersonsDiscount += invoiceResult.totalDiscount

          // Set Note that is not visible on the generated PDF, as for internal note
          await page.evaluate((ts, text, user, reset) => {
            // Get current not
            let curr = ""
            if(!reset) {
              window.ko.dataFor(document.querySelector("#SenderNote")).senderNote() || ""
              if(curr != "") {curr+="\n"}
            }
            window.ko.dataFor(document.querySelector("#SenderNote")).senderNote(curr + "[" + ts + "] " + text + " (" + user + ")")
            return window.ko.dataFor(document.querySelector("#SenderNote")).senderNote()
          }, timestamp, text_automated, user, resetNote)



          if(test) {
            let [cancel] = await Promise.all([
              page.waitForNavigation("#entryOverview"),
              page.click("#editPersonInvoice form a")
            ]);
            let diff = helper.timediff(currentTime)
            helper.log("Faktura " + invoiceItemById.invoiceNumber  + " testad (" + diff + " sekunder) [ Test - inget sparat ]")
            helper.log(" Test klart -".padStart(120,"-"))
          } else {
            // Save updates
            let [data_saved] = await Promise.all([
              page.waitForNavigation("#entryOverview"),
              page.click("input#Save")
            ]);
            let diff = helper.timediff(currentTime)
            let result = await page.$eval("#main p.info", el => el.innerText)
            helper.log("Faktura " + invoiceItemById.invoiceNumber  + " behandlad (" + diff + " sekunder): " + result)
            helper.log(" Klar -".padStart(120,"-"))
          }
        }


      } // If 
    }//) // forEach
    helper.log("Total summa utan subventioner - för alla: " + (""+allPersonsAmount).replace(".5",",50").padStart(4) + " kr")
    helper.log("Total summa subventioner - för alla:      " + (""+allPersonsDiscount).replace(".5",",50").padStart(4) + " kr")
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