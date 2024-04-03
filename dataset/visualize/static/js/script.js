var view;
require([
    "esri/Map",
    "esri/views/MapView",
    "esri/layers/VectorTileLayer", // For adding detailed vector tiles
    "esri/layers/FeatureLayer" // For adding specific feature layers
], function (Map, MapView, VectorTileLayer, FeatureLayer) {

    var map = new Map({
        basemap: "satellite" // Start with a satellite basemap
    });

    // Optionally add a vector tile layer for detailed streets, labels, etc.
    var streetsVectorLayer = new VectorTileLayer({
        portalItem: {
            // Example ID for a detailed streets vector tile layer
            id: "30d6b8271e1849cd9c3042060001f425" // Always verify the current ID from the ArcGIS documentation
        }
    });
    map.add(streetsVectorLayer); // Add the streets vector layer to the map


    view = new MapView({
        container: "map",
        map: map,
        zoom: 12,
        center: [11.6, 48.1]
    });

});
function drawWktPolygonAndView(wkt) {
    require([
        "esri/Graphic",
        "esri/geometry/Polygon",
        "esri/geometry/SpatialReference"
    ], function (Graphic, Polygon, SpatialReference) {

        // Parse the WKT string to extract coordinates
        const coordsString = wkt.match(/\(\((.+)\)\)/)[1];

        const coordsArray = coordsString.split(',').map(coord => {
            const parts = coord.trim().split(' ');
            return [parseFloat(parts[0]), parseFloat(parts[1])];
        });
        view.graphics.removeAll();
        // Create a Polygon from the coordinates
        const polygon = new Polygon({
            type: "polygon",
            rings: [coordsArray]
        });

        // Create a Graphic from the Polygon
        const polygonGraphic = new Graphic({
            geometry: polygon,
            symbol: {
                type: "simple-fill",
                color: [227, 139, 79, 0.3],
                outline: {
                    color: [255, 255, 255],
                    width: 1
                }
            }
        });
        // Add the Graphic to the map
        view.graphics.add(polygonGraphic);

        // Navigate to the polygon
        view.goTo({
            target: polygonGraphic.geometry,
            zoom: 16 // Optional: Adjust or remove the zoom level as necessary
        }).catch(function (error) {
            console.error("Error in view.goTo:", error);
        });
    });
}
// Function to submit the file and load the table
function submitFile() {
    const fileInput = document.getElementById('fileInput');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    document.getElementById('loader').style.display = '';

    fetch('/upload', {
        method: 'POST',
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            if (data.filepath) {
                fetch('/submit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ filepath: data.filepath }),
                })
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('tableContainer').innerHTML = data.html_table;
                        truncateTableText(); // Call function to truncate text
                        addToggleButton();
                        // Call the function, e.g., after the table has been fully loaded or populated
                        adjustSecondColumnWidth();
                        document.getElementById('loader').style.display = 'none';
                        // Add event listener to the newly added toggle button
                        rowClickable();
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        // Hide the loader on error as well
                        document.getElementById('loader').style.display = 'none';
                    });
            } else {
                // Handle the case where the file path isn't returned as expected
                // Hide the loader
                document.getElementById('loader').style.display = 'none';
            }

        })
        .catch(error => {
            console.error('Error:', error);
            // Hide the loader on error
            document.getElementById('loader').style.display = 'none';
        });;
}

let currentExpandedCell = null;
let truncate_size = 150
// Function to truncate text in table cells
function truncateTableText() {
    const cells = document.querySelectorAll('.data td');
    cells.forEach(cell => {
        // Only truncate if cell content is large
        if (cell.textContent.length > truncate_size) { // Adjust limit as needed
            const fullText = cell.textContent;
            const truncatedText = fullText.substring(0, truncate_size) + '...'; // Adjust truncation as needed
            cell.style.cursor = 'pointer';
            // Set the cell to display truncated text initially
            cell.innerHTML = `<span class="truncated" title="Click to view more">${truncatedText}</span>`;

            // Add click event listener to toggle full text display
            cell.addEventListener('click', function () {
                if (currentExpandedCell && currentExpandedCell !== cell) {
                    // If there's a different cell expanded, truncate its text first
                    const currentFullText = currentExpandedCell.textContent;
                    currentExpandedCell.innerHTML = `<span class="truncated" title="Click to view more">${currentFullText.substring(0, truncate_size) + '...'}</span>`;
                }
                const isTruncated = cell.querySelector('.truncated');
                if (isTruncated) {
                    cell.innerHTML = `<span class="full-text">${fullText}</span>`;
                    currentExpandedCell = cell; // Update reference to the currently expanded cell

                } else {
                    cell.innerHTML = `<span class="truncated">${truncatedText}</span>`;
                    if (currentExpandedCell === cell) {
                        currentExpandedCell = null; // Clear reference if this cell was the expanded one
                    }

                }
            });
        }
    });
}
last_color = "";
last_row = "";
function rowClickable() {
    document.querySelectorAll('.data tbody tr').forEach((row, index) => {
        // Assuming the first cell in every row should be clickable
        const firstCell = row.cells[0];
        firstCell.addEventListener('click', () => {
            const rowId = index; // Using row index as ID, adjust based on your needs
            var rows = document.querySelectorAll("table tr");
            if (last_row !== "") {
                rows[last_row + 1].style.backgroundColor = last_color;
            }
            last_color = rows[rowId + 1].style.backgroundColor;
            last_row = rowId;
            rows[rowId + 1].style.backgroundColor = "#1B263B";
            fetch('/process-row', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ rowId: rowId }),
            })
                .then(response => response.json())
                .then(data => {
                    drawWktPolygonAndView(data['image_polygon']);
                    //toggleTableVisibility();
                    const imageUrl = data.image_path;
                    // Make the table invisibl
                    const imageContainer = document.getElementById('dataImage');
                    imageContainer.src = imageUrl;
                    imageContainer.style.border = "5px solid #1B263B";
                })
                .catch(error => console.error('Error:', error));
        });

        // Optional: Add a style to indicate clickable cells
        firstCell.style.cursor = 'pointer';
    });
}


function addToggleButton() {
    if (document.getElementById('toggleTable')) {
        document.getElementById('toggleTable').remove();
    }
    const toggleButtonHTML = `
                    <button id="toggleTable" class="toggle-button">
                        <img src="static/images/up-arrow.svg" alt="Toggle Table" class="arrow-icon" id="toggleButton">
                    </button>
                `;

    // Append the toggle button HTML after the table
    document.getElementById('Table').insertAdjacentHTML('beforeend', toggleButtonHTML);

    // Add event listener to the newly added toggle button
    document.getElementById('toggleTable').addEventListener('click', toggleTableVisibility);
    document.getElementById('tableContainer').querySelector('table').style.display = 'block';
    return;
}
lastScrollTop = 0; // To hold the scroll position

function toggleTableVisibility() {
    const tableContainer = document.getElementById('tableContainer');
    const table = tableContainer.querySelector('table'); // Assuming the table exists
    var img = document.getElementById('toggleButton')// Reference the img within the button
    if (table.style.display === 'none' || !table.style.display) {
        table.style.display = 'block'; // Show table
        tableContainer.scrollTop = lastScrollTop;
        img.src = 'static/images/up-arrow.svg'; // Change to up-arrow
    } else {
        lastScrollTop = tableContainer.scrollTop;
        console.log(lastScrollTop, "AFFFF");
        table.style.display = 'none'; // Hide table
        img.src = 'static/images/down-arrow.svg'; // Change back to down-arrow
    }
}


function adjustSecondColumnWidth() {
    const table = document.querySelector('.data');
    const tableWidth = table.offsetWidth;
    const columns = table.querySelectorAll('th');
    let remainingWidth = tableWidth;

    columns.forEach((column, index) => {
        if (index !== 1) { // Skip the second column (index 1)
            remainingWidth -= column.offsetWidth;
        }
    });

    // Set the width of the second column header
    columns[1].style.width = `${remainingWidth}px`;

    // Optionally, adjust cells in the second column as well
    const rows = table.querySelectorAll('tr');
    rows.forEach(row => {
        const cells = row.querySelectorAll('td, th');
        if (cells.length > 1) { // Check if the row has enough cells
            cells[1].style.width = `${remainingWidth}px`;
        }
    });
}

