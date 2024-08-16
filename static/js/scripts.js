function editItemType(index) {
    const newType = prompt("Enter new type (Sweater, Shirt, Jacket, Bottom, Shoe, Hat, Glasses, Scarf):");

    if (newType) {
        $.ajax({
            url: '/update_item',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ index: index, new_type: newType }),
            success: function(response) {
                if (response.success) {
                    location.reload();
                } else {
                    alert('Failed to update item type. Please try again.');
                }
            }
        });
    }
}

function toggleFavorite(index) {
    $.ajax({
        url: '/toggle_favorite',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ index: index }),
        success: function(response) {
            if (response.success) {
                location.reload();
            } else {
                alert('Failed to toggle favorite status. Please try again.');
            }
        }
    });
}

function deleteItem(index) {
    if (confirm("Are you sure you want to delete this item?")) {
        $.ajax({
            url: '/delete_item',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ index: index }),
            success: function(response) {
                if (response.success) {
                    location.reload();
                } else {
                    alert('Failed to delete item. Please try again.');
                }
            }
        });
    }
}

document.getElementById('fileInput').addEventListener('change', function(event) {
    const fileName = event.target.files[0].name;
    const label = document.getElementById('fileLabel');
    label.textContent = fileName;
});