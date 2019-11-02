// Rules

/*

Here you can update the rules used when calulating discount.
These three methods 
- _isValidEvent
- _isValidEntry
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
- Räkna bort eventuell efteranälningskostnad från subventione

*/

/* Verifies, by string parsing (since no other options are possible), if this event is valid for discount or not */
function _isValidEvent(text) {
	// Must start with
	const must_contain = new RegExp(/^Anmälan för .* i /).test(text)
	// Cannot contain any of the following text fragments
	const invalid = new RegExp(/punch|card rental|hyrbricka|o-ringen|måltider|subvention/ig).test(text);
	return must_contain && !invalid
}
/* Verify, by string parsing (since no other options are possible), if this entry is valid for discount or not */
function _isValidEntry(status) {
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
function _calculateDiscount(text, age, fee, lateFee) {
	let amount = fee; // This will round down for a fee like fee=112,50 -> amount=112
	if(lateFee != 0) {
		amount -= lateFee;
	}
	if(amount == 0 && lateFee == 0) {
		return {amount:amount, percent: 0}
	}
	if(age < 21) {
		const fullDiscount = /sm, |dm, |mästerskap|swedish league/ig;
		if(fullDiscount.test(text)) {
		  return {amount:amount, percent: 100}
		}
	}
	// Now, only 40% is the only alternative left
	amount = Math.round(0.4 * amount);
	return {amount:amount, percent: 40}
}

// Return object representing current rows discount status
function getDiscountStatus(rowText, age, fee, lateFee, status) {
	const validEvent = _isValidEvent(rowText)
	const validEntry = _isValidEntry(status)
	let invoiceNote = _filterName(rowText)
	fee = parseInt(fee)
	if(isNaN(fee)) {
		fee = 0
	}
	lateFee = parseInt(lateFee)
	if(isNaN(lateFee)) {
		lateFee = 0
	}
	const result = {valid: false, fee: fee, lateFee: lateFee, discountAmount: 0, discountPercent: 0, invoiceNote: invoiceNote, status: ""}
	if(!validEvent) {
		result.status = "Ej subvention"
		return result
	}
	if(!validEntry) {
		result.status = "Ej start"
		return result
	}
	// Assume valid at this point
	result.valid = true 
	let discount = _calculateDiscount(invoiceNote, age, fee, lateFee)
	result.discountAmount = discount.amount
	result.discountPercent = discount.percent
	return result
}

// Export API
module.exports.getDiscountStatus = getDiscountStatus