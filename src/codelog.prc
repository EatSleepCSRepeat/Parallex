set test "string"
log "&[test.val] &{test.type}"
set test 4
log "&[test.val] &{test.type}"
if "(test)" is "(string)" [
    log "The test variable is a string."
]
if "(test)" is "(4)" [
    log "The test variable is 4."
]
