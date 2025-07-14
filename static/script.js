function filterTable() {
    var filter = document.getElementById("companyFilter").value;
    var rows = document.querySelectorAll("#studentTable tr");

    rows.forEach(row => {
        var company = row.getAttribute("data-company");
        if (filter === "all" || company === filter) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
}
