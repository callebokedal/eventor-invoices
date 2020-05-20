'use strict'
const rules = require('../lib/rules')

// Execute with:
// npm test

// rules.getDiscountStatus(rowText, age, fee, lateFee, status) 
// rules.getDiscountStatus("<eventlabel> - <class>", 18, 80, 0, "")
// rules.getDiscountStatus("Anmälan för Leif Orienterare i DM, stafett, Göteborg - D16", 18, 80, 0, "")
// return
// result = {valid: true/false, amount: fee, lateFee: lateFee, discountAmount: 0, discountPercent: 0, invoiceNote: invoiceNote, status: ""}

describe("100% rabatt för", function() {
	// rules.getDiscountStatus("<Event-text>", <ålder>, <Att betala>, <Efteranm. avg>, <status>)

	it("Veterantävling", function() {
		expect(rules.getDiscountStatus("Anmälan för Leif Orienterare i Veterantävling, sprint - H65", 67, 100, 0, ""))
		.toEqual({valid: true, amount: 100, lateFee: 0, discountAmount: 100, discountPercent: 100, invoiceNote: "Veterantävling, sprint", status: ""});
	});
	it("Veterantävling och efteranmälan", function() {
		expect(rules.getDiscountStatus("Anmälan för Leif Orienterare i Veterantävling - H65", 67, 100, 50, ""))
		.toEqual({valid: true, amount: 100, lateFee: 50, discountAmount: 100, discountPercent: 100, invoiceNote: "Veterantävling", status: ""});
	});
	it("Vårserie", function() {
		expect(rules.getDiscountStatus("Anmälan för Leif Orienterare i Vårserie - H12", 12, 100, 0, ""))
		.toEqual({valid: true, amount: 100, lateFee: 0, discountAmount: 100, discountPercent: 100, invoiceNote: "Vårserie", status: ""});
	});
	it("Vårserie och efteranmälan", function() {
		expect(rules.getDiscountStatus("Anmälan för Leif Orienterare i Vårserie - H12", 12, 100, 50, ""))
		.toEqual({valid: true, amount: 100, lateFee: 50, discountAmount: 50, discountPercent: 100, invoiceNote: "Vårserie", status: ""});
	});
	it("Sommarserie", function() {
		expect(rules.getDiscountStatus("Anmälan för Leif Orienterare i Sommarserie - H12", 12, 100, 0, ""))
		.toEqual({valid: true, amount: 100, lateFee: 0, discountAmount: 100, discountPercent: 100, invoiceNote: "Sommarserie", status: ""});
	});
	it("Sommarserie och efteranmälan", function() {
		expect(rules.getDiscountStatus("Anmälan för Leif Orienterare i Sommarserie - H12", 12, 100, 50, ""))
		.toEqual({valid: true, amount: 100, lateFee: 50, discountAmount: 50, discountPercent: 100, invoiceNote: "Sommarserie", status: ""});
	});
	it("DM-tävling (ungdom)", function() {
		expect(rules.getDiscountStatus("Anmälan för Leif Orienterare i Partilletrippeln, natt (med DM, natt, Göteborg) - D16", 18, 80, 0, ""))
		.toEqual({valid: true, amount: 80, lateFee: 0, discountAmount: 80, discountPercent: 100, invoiceNote: "Partilletrippeln, natt (med DM, natt, Göteborg)", status: ""});
	});
	it("SM-tävling", function() {
		expect(rules.getDiscountStatus("Anmälan för Leif Orienterare i Ungdoms-SM, sprint - D15", 18, 180, 0, ""))
		.toEqual({valid: true, amount: 180, lateFee: 0, discountAmount: 180, discountPercent: 100, invoiceNote: "Ungdoms-SM, sprint", status: ""});
	});
	it("SM-tävling (vuxen)", function() {
		expect(rules.getDiscountStatus("Anmälan för Leif Orienterare i SM, medel", 45, 100, 0, ""))
		.toEqual({valid: true, amount: 100, lateFee: 0, discountAmount: 100, discountPercent: 100, invoiceNote: "SM, medel", status: ""});
	});
	it("DM, stafett utan efteranmälningsavgift", function() {
		expect(rules.getDiscountStatus("Anmälan för Leif Orienterare i DM, stafett, Göteborg - D45", 45, 100, 0, ""))
		.toEqual({valid: true, amount: 100, lateFee: 0, discountAmount: 100, discountPercent: 100, invoiceNote: "DM, stafett, Göteborg", status: ""});
	});
	it("DM, stafett med efteranmälningsavgift", function() {
		expect(rules.getDiscountStatus("Anmälan för Leif Orienterare i DM, stafett, Göteborg - D45", 45, 150, 50, ""))
		.toEqual({valid: true, amount: 150, lateFee: 50, discountAmount: 150, discountPercent: 100, invoiceNote: "DM, stafett, Göteborg", status: ""});
	});
});

describe("40% rabatt för", function() {
	// rules.getDiscountStatus("<Event-text>", <ålder>, <Att betala>, <Efteranm. avg>, <status>)
	
	it("Vanlig tävling (vuxen)", function() {
		expect(rules.getDiscountStatus("Anmälan för Leif Orienterare i Partilletrippeln, sprint - H50", 52, 100, 0, ""))
		.toEqual({valid: true, amount: 100, lateFee: 0, discountAmount: 40, discountPercent: 40, invoiceNote: "Partilletrippeln, sprint", status: ""});
	});
	it("Vanlig tävling (vuxen) och efteranmälan", function() {
		expect(rules.getDiscountStatus("Anmälan för Leif Orienterare i Partilletrippeln, sprint - H50", 52, 150, 50, ""))
		.toEqual({valid: true, amount: 150, lateFee: 50, discountAmount: 40, discountPercent: 40, invoiceNote: "Partilletrippeln, sprint", status: ""});
	});
	it("Vanlig tävling (ungdom)", function() {
		expect(rules.getDiscountStatus("Anmälan för Lina Orienterare i Partilletrippeln, sprint - H50", 16, 100, 0, ""))
		.toEqual({valid: true, amount: 100, lateFee: 0, discountAmount: 40, discountPercent: 40, invoiceNote: "Partilletrippeln, sprint", status: ""});
	});
	it("Vanlig tävling (ungdom) och efteranmälan", function() {
		expect(rules.getDiscountStatus("Anmälan för Leif Orienterare i Partilletrippeln, sprint - H12", 12, 150, 50, ""))
		.toEqual({valid: true, amount: 150, lateFee: 50, discountAmount: 40, discountPercent: 40, invoiceNote: "Partilletrippeln, sprint", status: ""});
	});
	it("DM-tävling (vuxen)", function() {
		expect(rules.getDiscountStatus("Anmälan för Leif Orienterare i DM, lång, Göteborg - D55", 55, 100, 0, ""))
		.toEqual({valid: true, amount: 100, lateFee: 0, discountAmount: 40, discountPercent: 40, invoiceNote: "DM, lång, Göteborg", status: ""});
	});
	it("DM-tävling (vuxen) med efteranmälan", function() {
		expect(rules.getDiscountStatus("Anmälan för Leif Orienterare i DM, lång, Göteborg - D55", 55, 150, 50, ""))
		.toEqual({valid: true, amount: 150, lateFee: 50, discountAmount: 40, discountPercent: 40, invoiceNote: "DM, lång, Göteborg", status: ""});
	});
	it("SM-tävling publiktävling", function() {
		expect(rules.getDiscountStatus("Anmälan för Leif Orienterare i SM, medel, final, publiktävling medel - D15", 18, 100, 0, ""))
		.toEqual({valid: true, amount: 100, lateFee: 0, discountAmount: 40, discountPercent: 40, invoiceNote: "SM, medel, final, publiktävling medel", status: ""});
	});
});

describe("Ej rabatt för", function() {
	// rules.getDiscountStatus("<Event-text>", <ålder>, <Att betala>, <Efteranm. avg>, <status>)

	it("Veterantävling med ej start", function() {
		expect(rules.getDiscountStatus("Anmälan för Leif Orienterare i Veterantävling - H50", 50, 100, 0, "Ej start"))
		.toEqual({valid: false, amount: 100, lateFee: 0, discountAmount: 0, discountPercent: 0, invoiceNote: "Veterantävling", status: "Ej start"});
	});
	it("Vanlig tävling och efteranmälan", function() {
		expect(rules.getDiscountStatus("Anmälan för Leif Orienterare i Partilletrippeln, sprint - H50", 52, 100, 50, ""))
		.toEqual({valid: true, amount: 100, lateFee: 50, discountAmount: 20, discountPercent: 40, invoiceNote: "Partilletrippeln, sprint", status: ""});
	});
	it("Hyrbricka", function() {
		expect(rules.getDiscountStatus("Hyrbricka för Leif Orienterare", 52, 100, 0, ""))
		.toEqual({valid: false, amount: 100, lateFee: 0, discountAmount: 0, discountPercent: 0, invoiceNote: "Hyrbricka för Leif Orienterare", status: "Ej subvention"});
	});
});

