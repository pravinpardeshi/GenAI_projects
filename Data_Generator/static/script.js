const backendURL = window.location.origin + "/generate-data-script";

document.getElementById("generateBtn").addEventListener("click", async () => {
  const schema = document.getElementById("schemaInput").value;
  const output = document.getElementById("output");
  const downloadBtn = document.getElementById("downloadBtn");

  output.textContent = "⏳ Generating script... Please wait.";
  downloadBtn.style.display = "none"; // Hide download button until ready

  try {
    const response = await fetch(backendURL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ schema })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Server responded with status ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    const code = data.code;

    if (code) {
      output.textContent = code;
      downloadBtn.style.display = "inline-block";

      // Set up download
      downloadBtn.onclick = () => {
        const blob = new Blob([code], { type: "text/x-python" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "generated_data_script.py";
        a.click();
        URL.revokeObjectURL(url);
      };
    } else {
      output.textContent = "⚠️ No code was generated.";
    }

  } catch (error) {
    console.error("Fetch error:", error);
    output.textContent = `❌ Error: ${error.message}`;
    downloadBtn.style.display = "none";
  }
});

