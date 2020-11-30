// Rules

/*

Here you can update the rules used when calulating discount.
These three methods 
- _isValidEvent
- _didStart
- _calculateDiscount
are probably the one's you want to update for this.

// "Rules":
- Om ok -> 40% rabatt
- Om <21 år 
	- Om SM -> 100% rabatt
	- Om mästerskap -> 100% rabatt
- Varje rad
- Inte "punch", "hyrbricka" m.fl.
- Inte om "ej start"
- Ej O-Ringen
- Räkna bort eventuell efteranälningskostnad från subventioner

*/

/* Verifies, by string parsing (since no other options are possible), if this event is valid for discount or not */
function _isValidEvent(text) {
	// Must start with
	const must_contain = new RegExp(/^Anmälan för .* i /).test(text)
	// Cannot contain any of the following text fragments
	// Note leading space in " o-ringen" to allow competions like "GO-ringen"
	const invalid = new RegExp(/punch|card rental|hyrbricka| o-ringen|måltider|subvention/ig).test(text);
	return must_contain && !invalid
}
/* Verify, by string parsing (since no other options are possible), if this entry is valid for discount or not */
function _didStart(status) {
	const invalid = /ej start/ig;
	return !invalid.test(status);
}
/* Filter unneccessary text from name */
function _filterName(text) {
	let name = text.replace(/Anmälan för .* i /mg, "")
	let i = name.lastIndexOf(" - ")
	if(i == -1) {
		return name
	}
	return name.substr(0, i) // Shorten invoice text
}
/* This method excpect that the event has been tested valid prior */
function _calculateDiscount(text, age, amount, lateFee) {
	// Special case for "stafett" and "veteran" - always discount full amount
	const specificDiscount = /stafett|veteran/ig;
	if(specificDiscount.test(text)) {
	  return {amount:amount, percent: 100}
	}
	if(lateFee != 0) {
		// Don't give discount for late fee
		amount -= lateFee
		if(amount < 0) {amount = 0}
	}
	if(amount == 0 && lateFee == 0) {
		return {amount: 0, percent: 0}
	}
	if(age < 21) {
		const fullDiscount = /vårserie|dm, /ig;
		if(fullDiscount.test(text)) {
		  return {amount:amount, percent: 100}
		}
	}
	const noPubliktavling = /publiktävling/ig;
	if(/sm, /ig.test(text) && !noPubliktavling.test(text)) {
	  return {amount:amount, percent: 100}
	}
	// Now, only 40% is the only alternative left
	amount = Math.round(0.4 * amount);
	return {amount:amount, percent: 40}
}

// Return object representing current rows discount status
function getDiscountStatus(rowText, age, amount, lateFee, status) {
	const validEvent = _isValidEvent(rowText)
	const noStart = _didStart(status)
	let invoiceNote = _filterName(rowText)
	amount = parseFloat((amount+"").replace(",","."))
	if(isNaN(amount)) {
		amount = 0
	}
	lateFee = parseFloat((lateFee+"").replace(",","."))
	if(isNaN(lateFee)) {
		lateFee = 0
	}
	const result = {valid: false, amount: amount, lateFee: lateFee, discountAmount: 0, discountPercent: 0, invoiceNote: invoiceNote, status: ""}
	if(!validEvent) {
		result.status = "Ej subvention"
		return result
	}
	if(!noStart) {
		result.status = "Ej start"
		const specificCase = /veteran/ig;
		if(!specificCase.test(invoiceNote)) {  
			return result
		}
	}
	// Assume valid at this point
	result.valid = true 
	let discount = _calculateDiscount(invoiceNote, age, amount, lateFee)
	result.discountAmount = discount.amount
	result.discountPercent = discount.percent
	return result
}

// Export API
module.exports.getDiscountStatus = getDiscountStatus