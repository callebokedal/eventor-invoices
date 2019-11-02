# Invoice scripts for Eventor
Scripts to handle Invoice discounts in Eventor. Based on Node.js, (https://nodejs.org) and Puppeteer (https://developers.google.com/web/tools/puppeteer/).

## Installation
Prerequisites are ```nodejs``` and ```npm``` (https://www.npmjs.com/), along with ```git``` (https://git-scm.com/)

```bash
$ npm init
$ npm i puppeteer-core
$ npm install
# And also
$ npm install dotenv
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

### Updating invoices
```bash
	node update_invoices.js <args>
	node update_invoices.js --help
```

### Invoices overview
```bash
	node compare_invoices.js <args>
	node compare_invoices.js --help
```

## Examples

### Browser scripts
To be used in the web browser

```js
	// Log event text and fee
	window.model.items.forEach((el, idx) => {console.log(el.text + " " + el.fee)})
```
 
### Bash scripts

```bash
	# Return sorted and unique event names
	grep '^\- ' result.log | cut -d ':' -f1 | sed 's/^- //' | sort | uniq 
```
```bash
	# Return events matching "stafett"
	grep '^\- ' result.log | cut -d ':' -f1 | sed 's/^- //' | grep -i 'stafett'
```

### Coding

- https://github.com/checkly/puppeteer-examples/blob/master/1.%20basics/get_text_value.js
- https://developers.google.com/web/tools/puppeteer/examples
- https://www.npmjs.com/package/dotenv
- https://devdocs.io/puppeteer/

## Regler

För medlem som deltar aktivt i klubbens arbete som funktionär vid arrangemang, ledare eller på annat sätt bidrar till klubben sponsrar Sjövalla FK individuellt tävlande enligt nedanstående regler:

- Om ok -> 40% rabatt
- Om <21 år 
	- Om SM -> 100% rabatt
	- Om mästerskap -> 100% rabatt
- Om stafett -> 100%
- Varje rad
	- Inte "punch card" och inte "hyrbricka"
	- Inte om "ej start"
	- Ej O-Ringen (inte säker dessa äe med på listorna)
- Räkna bort eventuell efteranälningskostnad




### För varje sponsrad tävlingsstart erhålles subvention med 40%
Vi vill gärna att subventionen tydligt ska synas på det som faktureras ut
-> Välj ut vilka som är sanktionerade, se nedan. Notering kommer med tydligt på fakturan

### För flerdagarsarrangemang räknas varje deltävling som en tävlingsstart. 
Inga problem idag eftersom allt går genom Eventor

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




