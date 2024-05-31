async function convert() {
    const amount = document.getElementById('amount').value;
    const response = await fetch('/convert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount })
    });
    const data = await response.json();
    document.getElementById('result').innerText = `Public Key: ${data.public_key}, Secret: ${data.secret}`;
}

async function donate() {
    const public_key = document.getElementById('public_key').value;
    const charity_id = document.getElementById('charity').value;
    const amount = document.getElementById('donate_amount').value;
    const response = await fetch('/donate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ public_key, charity_id, amount })
    });
    const data = await response.json();
    document.getElementById('donate_result').innerText = `Donation Status: ${data.status}, Transaction ID: ${data.tx_id}`;
}