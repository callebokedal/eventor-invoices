// Helper functions
const DEBUG=false

// Get date now of format: "yy-mm-dd hh:mm"
function timestamp() {
  const d = new Date()
  return d.toLocaleDateString("sv-SE") + " " + d.toTimeString().substring(0,5)
}

// To be used for common debug log during development
function debug(msg, obj) {
	if(DEBUG) {
	 	if(obj) {
			console.log(msg, obj)
		} else {
			console.log(msg)
		}
	}
}
// To be used to log to stdout
function log(msg, obj) {
	if(obj) {
		console.log(msg, obj)
	} else {
		console.log(msg)
	}
}
// Calculate time diff
// if 'full' is true, return as object representing minutes and seconds {m: x, s: y}
function timediff(timestamp, full = false) {
    let diff = new Date().getTime() - timestamp;
    //var daysDifference = Math.floor(difference/1000/60/60/24);
    let seconds = Math.floor(diff/1000);
    return seconds;
}

// Return diff as {m: <minutes>, s: <seconds>}
function timediffMS(timestamp) {
    let diff = new Date().getTime() - timestamp;
    //var daysDifference = Math.floor(difference/1000/60/60/24);
    let seconds = Math.floor(diff/1000);
    let minutes = Math.floor(seconds/60);
    seconds = seconds - (minutes * 60);
    return {m: minutes, s: seconds};
}

module.exports.timestamp = timestamp
module.exports.timediff = timediff
module.exports.timediffMS = timediffMS
module.exports.log = log
module.exports.debug = debug
