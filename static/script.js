document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("upload-form").addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent page refresh

        let formData = new FormData();
        let fileInput = document.getElementById("file-input");
        if (fileInput.files.length === 0) {
            alert("Please select an image first!");
            return;
        }

        formData.append("file", fileInput.files[0]);

        fetch("/upload", {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                document.getElementById("prediction-image").src = data.predicted;
                document.getElementById("prediction-container").style.display = "block";
            }
        })
        .catch(error => console.error("Error:", error));
    });
});
