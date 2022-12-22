# Invoice scripts for Eventor
Scripts to handle Invoice discounts in Eventor. Based on Node.js, (https://nodejs.org) and Puppeteer (https://developers.google.com/web/tools/puppeteer/).

## Installation

### Node
Prerequisites are ```nodejs``` and ```npm``` (https://www.npmjs.com/), along with ```git``` (https://git-scm.com/)

```bash
$ npm init
$ npm i puppeteer-core
$ npm install
# And also
$ npm install dotenv
```

### Python
```sh
# Always activate virtual env first
# source <your virtual environment directory>/bin/activate
source venv/bin/activate
pip install tabulate
# Update installed libs
pip freeze > requirements.txt
```

### Settings
You need to create the following file
```bash
.env
```
with login credentials 
```bash
PersonUsername=<Username>
PersonPassword=<Password>
```

## Start

### Update invoices
```bash
	node update_invoices.js <args>
	node update_invoices.js --help

	# Example
	node update_invoices.js -b 751 >> report.txt
	node update_invoices.js -b 751 -t >> only_testing.txt
	node update_invoices.js -b 751 -t -c3 >> only_testing_a_few.txt
```

### Invoices overview/comparison
(To create simple text-files that can be compared)
```bash
	node compare_invoices.js <args>
	node compare_invoices.js --help

	# To extract comparions
	node compare_invoices.js -b 581 >> report_581.txt
	node compare_invoices.js -b 750 >> report_750.txt

	# Other example
	node compare_invoices.js -b 444 -s false -c 3 >> report_444.txt
	node compare_invoices.js -b 555 -s false -c 3 >> report_555.txt

	# Now compare
	vimdiff report_581.txt report_750.txt
	vimdiff report_444.txt report_555.txt
```

### Reports
```bash
grep -e '-\[+' -e 'Summa subvention' -e 'Summa att' -e ' år, ' -e 'https://' report_809.txt | sed 's/--//g' | sed 's/-\[+\]- Fakturanummer //' | sed 's/ - \[/|/' | sed 's/\]//g'
```

## Testning

```bash
npm test
```

## Examples

### Browser scripts
To be used in the web browser

```js
	// Log event text and fee
	window.model.items.forEach((el, idx) => {console.log(el.text + " " + el.fee)})
```

To be executed in the browser console (typically Option + CMD + I -> Console)
```js
	// Get names for invoice batch
	s=""; document.querySelectorAll("#invoices tbody tr").forEach((item) => { s += item.querySelector("td").innerText + "\n" }); console.log(s)

	// For already processed invoices
	s=""; document.querySelectorAll("#invoices tbody tr").forEach((item) => { s += item.querySelector("td:nth-child(2)").innerText + "\n" }); console.log(s)

	// Calculated sum to pay ("Att betala" column)
	s=0;document.querySelectorAll("input.amountInput").forEach(function(item) {if(!isNaN(parseFloat(item.value))) {s += parseFloat(item.value)}}); console.log(s)

	// Calculated sum of amount ("Avg" column)
	s=0;document.querySelectorAll("td.feeText[data-bind='text: fee']").forEach(function(item) {if(!isNaN(parseFloat(item.innerText))) {s += parseFloat(item.innerText)}}); console.log(s)

	// document.querySelectorAll("#items td[data-bind='text: fee']").forEach(item => console.log(item.innerHTML))

	1995 - 1159
```

```js
// Calculate price for one person
var x = function() {

let items = window.model.items
let len = items.length
let s=0
for (var i = 0; i < len; i++) {
     s+= !isNaN(parseFloat(items[i].fee)) ? parseFloat(items[i].fee) : 0
}
console.log(s)
}
x()
```

To retreive event model via browser console for a person
```js
var x = function() {

let items = window.model.items
let len = items.length
let s=""
for (var i = 0; i < len; i++) {
     s+= items[i].text + ". Amount: " + items[i].amount + ", fee: " + items[i].fee + ", lateFee: " + items[i].lateFee + ", status: " + items[i].status + "\n"
}
console.log(s)
}
x()
```
 
### Bash scripts
Various script to verify

```bash
	# Return sorted and unique event names
	grep '^\- ' result.txt | cut -d ':' -f1 | sed 's/^- //' | sort | uniq 
```
```bash
	# Return events matching "stafett"
	grep '^\- ' result.txt | cut -d ':' -f1 | sed 's/^- //' | grep -i 'stafett'
```

```bash
	# Get e-mail addresses
	grep "@" reports/report_808.txt | cut -d',' -f1,3 | sort
```

```bash
	cat *.txt | grep -v "^Mem" | grep -v "^Email" | cut -d',' -f1-3 | sed 's/,member//' | sed 's/,owner//' | sed 's/\\(/"/' 
	cat *.txt | grep -v "^Mem" | grep -v "^Email" | cut -d',' -f1-3 | sed 's/,member//' | sed 's/,owner//'
```

```bash
# 2020-07-06 Check multiday events
cat all_events.txt | grep -v -e Veteran -e 'Ej start' -e 'Ej subve' | sort -nr | uniq -c | sort | grep ' 0 kr (0%)' | grep -v -e '^   1'
   2 Herkules Skogsdåd:                                   0 kr (0%)    
   2 Morokulien 2-dagars:                                 0 kr (0%)    
   3 KSK-sprinten:                                        0 kr (0%)    
   4 O-Event, dag 3, Zoorientering:                       0 kr (0%)    
  13 Gotland 3-dagars:                                    0 kr (0%)    
  56 Hallands 3-dagars:                                   0 kr (0%)    
  60 Göteborg O-meeting:                                  0 kr (0%) 

## Följande blir fel
   2 Morokulien 2-dagars:                                 0 kr (0%)    
  13 Gotland 3-dagars:                                    0 kr (0%)    
  56 Hallands 3-dagars:                                   0 kr (0%)    
  60 Göteborg O-meeting:                                  0 kr (0%) 
```

### Coding

- https://github.com/checkly/puppeteer-examples/blob/master/1.%20basics/get_text_value.js
- https://developers.google.com/web/tools/puppeteer/examples
- https://www.npmjs.com/package/dotenv
- https://devdocs.io/puppeteer/

## Regler

För medlem som deltar aktivt i klubbens arbete som funktionär vid arrangemang, ledare eller på annat sätt bidrar till klubben sponsrar Sjövalla FK individuellt tävlande enligt nedanstående regler:

### Regler i detalj

- Ingen subvention för (oavsett ålder)
	- "hyrbricka" eller "punch card"
	- Om "ej start"
	- Ej O-Ringen (inte säker dessa är med på listorna)
	- Räkna bort eventuell efteranmälningsavgift från subvention (undantag Våreserie, DM, 25 manna)
	- All händelser som inte startar med "Anmälan för <person>" (ex: "Camping")
- Om <21 år 
	- Om SM 			-> 100% rabatt
	- Om mästerskap 	-> 100% rabatt
- Specialfall
	- Om "stafett" 		-> 100% (oavsett ålder) 
	- Om "vårserien" 	-> 100% (oavsett ålder) 
	- Om "veteran" 		-> 100% (då dessa betalas kontant på plats, oavsett ålder)
- Övriga tävlingar 		-> 40% rabatt (oavsett ålder)

## Regler författade 2022 (bättre/sämre än ovan?)

Som medlem i Sjövalla Orientering får du subvention på tävlingar enligt följande regler!

Regler för tävlingar som ger subvention (notera även undantagsregler nedan)
- Medlem under 21 år får 100% subvention på normal anmälningsavgift (eventuell efteranmälningsavgift får man betala för själv)
- Medlem från 21 år får 40% subvention på normal anmälningsavgift (eventuell efteranmälningsavgift får man betala för själv)
- Är man med i en stafettävling med klubben subventioneras detta till 100% (exempel: 25-manna, DM-stafett)
- Tävling i SM subventioneras till 100%
- Vissa tävlingar betalas på plats vid tävling men dyker ändå upp i Eventor. Dessa försöker vi rensa bort genom att ge 100% subvention (exempel: Veterantävlingar, Skogsflickor)

Undantag:
- Om man ej startat i en tävling får man själv stå för hela kostnaden
- Man får inte subvention för annat än anmälningar till tävling. Till exempel får man inte subvention på hyra av SportIdent-pinne, måltid på arenan eller liknande.
- Tävling på O-Ringen subventioneras inte

OBS! Underlag för avgifter kommer från Eventor. Ibland händer det att ansvariga klubbar fakturerat fel, ibland har det blivit fel i Eventor. Dessa fall försöker vi hantera på bästa och smidigaste sätt och hoppas på förståelse om det skulle bli fel någon gång. 

Tanken med dessa subventioner är att hjälpa våra medlemmar att komma ut i skogen - inte minst gällande våra ungdomar!



### För varje sponsrad tävlingsstart erhålles subvention med 40%
Vi vill gärna att subventionen tydligt ska synas på det som faktureras ut
-> Välj ut vilka som är sanktionerade, se nedan. Notering kommer med tydligt på fakturan

### För flerdagarsarrangemang räknas varje deltävling som en tävlingsstart. 
Inga problem idag eftersom allt går genom Eventor.
Jo, problem eftersom Eventor räknar fel ibland. Första dagen blir rätt men inte efterföljande

### Vid utebliven start erhålls ingen sponsring. 
Syns detta i Excel utdraget från Eventor?
-> Ja, "Ej start" syns i listan för fakturan

### Efteranmälningsavgift betalas av medlemmen.
I fakturorna som jag får från tävlingarna är det en klumpsumma, är det separerat i Eventor? 
-> Efteranmälan står med i listan för fakturorna
-> Finns med i Competitor summary
-> Står med som kolumn i fakturor

### Sponsring utgår för alla OL-tävlingar med undantag av O-ringen i de fall man tävlar i Sjövallas namn 
Alla betalar ju O-ringen själva så alla tävlingar vi får i Eventor
-> Strängmatchning

### Avgift för hyrbricka betalas av den tävlande.
Syns detta?
-> Ja, "RentalPunchingCard" står med i faktura-export, samt i annan kolumn

### För deltagande i SM-tävlingar sponsrar Sjövalla normalt hela startavgiften
Kan man lägga in regel? SM = 0 kronor? Annars är det ju ett fåtal att komma ihåg och editera manuellt
-> Strängmatchning
-> Lägg också med URL för respektive faktura i logg - så blir det enkelt att gå tillbaka.

### Ungdomar <21 erhåller alltid ovanstående sponsring och dessutom betalar klubben full avgift för vårserien och mästerskap
Notera att man fortfarande ska betala om det är ”ej start”, ”efteranmälningsavgift” eller ”hyra av pinne”
-> Ålder finns, ej start finns, eft. anmälning finns. Oklart med pinne

### Alla stafetter betalas av klubben som tidigare.
Dessa kommer in i utdraget från Eventor och vi vill att de ska raderas helt.
-> Strängmatchning och med på rapport. Rader kan tas bort.

Som ni ser så är det ganska många regler och undantag vilket är utmanande.

Till detta har kommit att det har varit fel i Eventor, ex har tävlingar som löparen har betalat kontant kommit med i utdraget mm men det får vi väl hoppas att de löser.




