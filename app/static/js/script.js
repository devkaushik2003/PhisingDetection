document.getElementById("urlForm").addEventListener("submit", async function (e) {
    e.preventDefault(); // Prevent page reload

    // Get input URL
    const url = document.getElementById("url").value;

    // Debug log
    console.log("Input URL:", url);

    try {
        // Send POST request to Flask API
        const response = await fetch("http://127.0.0.1:5000/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json", // Important!
            },
            body: JSON.stringify({ url: url }), // Convert to JSON
        });

        console.log("Response Status:", response.status); // Log status

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        // Get and display the result
        const data = await response.json();
        console.log("Response Data:", data); // Debug log

        document.getElementById("result").innerText = `Prediction: ${data.prediction}`;
    } catch (error) {
        console.error("Error:", error); // Log errors
        document.getElementById("result").innerText = "Error: Unable to process request.";
    }
});
