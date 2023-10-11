
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
    /*
        observer.observe(
            document.querySelector('input'),
            { subtree: true, characterData: true, childList: true }
        )
        */
}
createObserver()
