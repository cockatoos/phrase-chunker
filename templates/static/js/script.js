function buttonPress() {
    postMessage({'who': 'what'});
}

async function postMessage(message) {
    return await fetch('/receiver', {

        // Specify the method
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Cookie': document.cookie
        },
        // A JSON payload
        body: JSON.stringify(message)
    });
}