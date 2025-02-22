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

        document.querySelector(".spinner-border").style.display = "inline-block";  

        fetch("/upload", {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            document.querySelector(".spinner-border").style.display = "none";  

            if (data.error) {
                alert(data.error);
            } else {
                document.getElementById("prediction-image").src = data.predicted;
                document.getElementById("prediction-image").style.display = "block";
                document.getElementById("prediction-container").style.display = "block";
            }
        })
        .catch(error => {
            document.querySelector(".spinner-border").style.display = "none";  
            console.error("Error:", error);
        });
    });
});