let run = () => {
    console.log(`\n\nTLS browser extension loaded`)

    // https://developer.chrome.com/extensions/match_patterns
    var ALL_SITES = { urls: ['<all_urls>'] }

    // Mozilla doesn't use tlsInfo in extraInfoSpec
    var extraInfoSpec = ['blocking'];

    // https://developer.mozilla.org/en-US/Add-ons/WebExtensions/API/webRequest/onHeadersReceived
    browser.webRequest.onHeadersReceived.addListener(async function(details) {
        console.log(`\n\nGot a request for ${details.url} with ID ${details.requestId}`)

        // Yeah this is a String, even though the content is a Number
        var requestId = details.requestId

        var securityInfo = await browser.webRequest.getSecurityInfo(requestId, {
            certificateChain: true,
            rawDER: false
        });

        console.log(`securityInfo: ${JSON.stringify(securityInfo, null, 2)}`)

    }, ALL_SITES, extraInfoSpec)

    console.log('Added listener')

}

// Set up a mutation observer to listen for title changes
// Will fire if framework AJAX stuff switches page title
let createObserver = function() {
    let observer = new MutationObserver((mutations) => {
        // Disconnect the MO so there isn't an infinite title update loop
        // Run title cleanup again
        // Create a new MO to listen for more changes
        console.log('Mutations!', mutations)
        observer.disconnect()
        observer = null
        run()
        createObserver()
    })

    observer.observe(
        document.querySelector('input'),
        { subtree: true, characterData: true, childList: true }
    )
}
createObserver()

// Kick off initial page load check
run()
