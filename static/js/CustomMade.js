async function AdminSearchBar()
{
        const typeInput = document.getElementById('typeInput');
        const searchInput = document.getElementById('searchInput');
        const submitButton = document.getElementById('searchButton');
    
        typeInput.addEventListener('change', function () {
            if (typeInput.value) {
                searchInput.disabled = false;
                submitButton.disabled = false;
            } else {
                searchInput.disabled = true;
                submitButton.disabled = true;
            }
    
        searchInput.addEventListener('input', async function () {
            const typeValue = typeInput.value;
            const searchValue = searchInput.value;
    
            if (typeValue && searchValue) {
                let response = await fetch(`/AdminPanel/Dashboard/Search?search=${encodeURIComponent(searchValue)}&type=${encodeURIComponent(typeValue)}`);
                let data = await response.json();
    
                let ul = document.getElementById("searchResults");
                ul.innerHTML = "";
                data.forEach(item => {
                    let li = document.createElement("li");
                    li.className = "list-group-item";
                    li.textContent = Object.values(item)[0];
                    li.addEventListener("click", function() {
                        searchInput.value = Object.values(item)[0];
                        ul.innerHTML = "";
                        ul.style.display = 'none';
                    });
                    ul.appendChild(li);
                });
                ul.style.display = 'block';
            }
        });
    });
}

async function fetchStats() {
    let response = await fetch("/AdminPanel/Dashboard/Stats");
    let stats = await response.json();

    let div = document.getElementById("totalSales");
    if (div) {
        div.innerHTML = `<h6 class="mb-1">sales ${stats.totalSales}</h6>`;
    }
    div = document.getElementById("totalProducts");
    if (div) {
        div.innerHTML = `<h6 class="mb-1">Products ${stats.totalProducts}</h6>`;
    }
    div = document.getElementById("totalCategories");
    if (div) {
        div.innerHTML = `<h6 class="mb-1">categories ${stats.totalCategories}</h6>`;
    }
    div = document.getElementById("totalUsers");
    if (div) {
        div.innerHTML = `<h6 class="mb-1">users ${stats.totalUsers}</h6>`;
    }
    div = document.getElementById("totalOrders");
    if (div) {
        div.innerHTML = `<h6 class="mb-1">orders ${stats.totalOrders}</h6>`;
    }
    div = document.getElementById("adminInfo");
    if (div) {
        div.innerHTML = `<h6 class="mb-1"> admin ${stats.adminInfo.userName}</h6>`;
    }
    for (let i = 0; i < 5; i++) {
        div = document.getElementById(`topSales${i}`);
        if (div && stats.topSales[i]) {
            div.innerHTML = `<h6 class="mb-1"> top sales ${stats.topSales[i].total_sales}</h6><span class="mb-0">${stats.topSales[i].product_id}</span>`;
        }

        div = document.getElementById(`newOrders${i}`);
        if (div && stats.newOrders[i]) {
            div.innerHTML = `<h6 class="mb-1"> new orders${stats.newOrders[i].order_items}</h6><span class="mb-0"></span>`;
        }

        div = document.getElementById(`newReviews${i}`);
        if (div && stats.newReviews[i]) {
            let stars = '';
            for (let j = 0; j < stats.newReviews[i].rating; j++) {
                stars += '<i class="fa fa-star" aria-hidden="true"></i>';
            }
            div.innerHTML = `<h6 class="mb-1">new reviews ${stars}</h6><span class="mb-0">${stats.newReviews[i].comment}</span>`;
        }
    }
}


async function FetchCategories() {
    let response = await fetch('/AdminPanel/Categories/OPS', { method: 'GET' });
    let data = await response.json();
    const table = document.getElementById('categoriesTableBody');
    table.innerHTML = ''; // Clear existing table rows if any

    data.forEach(item => {
        let row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.id}</td>
            <td>${item.name}</td>
            <td>${item.description}</td>
            <td><img src="${item.image_file}" alt="Category Image" width="50" height="50"></td>
            <td>${item.slug}</td>
            <td>${new Date(item.created_at).toLocaleString()}</td>
            <td>${new Date(item.updated_at).toLocaleString()}</td>
            <td>
                <button class="btn btn-warning btn-sm editButton" data-bs-toggle="modal" data-bs-target="#editCategoryModal" 
                        data-id="${item.id}" data-name="${item.name}" data-description="${item.description}" data-slug="${item.slug}">Edit</button>
                <button class="btn btn-danger btn-sm deleteButton" data-bs-toggle="modal" data-bs-target="#confirmDeleteModal" 
                        data-id="${item.id}">Delete</button>
            </td>`;
        table.appendChild(row);
    });
}




async function AddCategory() {

    const form = document.getElementById("addCategoryForm");
    form.addEventListener("submit", async function(event) {
    event.preventDefault(); // Prevent default form submission

    const formData = new FormData(form);

    try {
        const response = await fetch('/AdminPanel/Categories/OPS', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        // Hide the modal
        const addCategoryModal = bootstrap.Modal.getInstance(document.getElementById('addCategoryModal'));
        addCategoryModal.hide();
        
        FetchCategories(); // Refresh the categories list

    } 
    catch (error) {
        console.error('Error:', error);
        alert('An error occurred while adding the category.');
    }
});

}


async function DeleteAndEditCategory() {
    document.getElementById('categoriesTableBody').addEventListener('click', function(event) {
        if (event.target.classList.contains('editButton')) {
            const editButton = event.target;
            const categoryId = editButton.getAttribute('data-id');
            const categoryName = editButton.getAttribute('data-name');
            const categoryDescription = editButton.getAttribute('data-description');
            const categorySlug = editButton.getAttribute('data-slug');

            const editForm = document.getElementById('editCategoryForm');
            editForm.setAttribute('data-id', categoryId);

            // Populate the edit form with the category data
            document.getElementById('editName').value = categoryName;
            document.getElementById('editDescription').value = categoryDescription;
            document.getElementById('editSlug').value = categorySlug;
        } else if (event.target.classList.contains('deleteButton')) {
            const categoryId = event.target.getAttribute('data-id');
            const deleteForm = document.getElementById('deleteCategoryForm');
            deleteForm.setAttribute('data-id', categoryId);
        }
    });

    document.getElementById('deleteCategoryForm').addEventListener('submit', async function(event) {
        event.preventDefault(); // Prevent default form submission

        const categoryId = event.target.getAttribute('data-id');

        try {
            const response = await fetch(`/AdminPanel/Categories/OPS/${categoryId}`, {
                method: 'DELETE'
            });
            const data = await response.json();

            // Hide the modal
            const deleteCategoryModal = bootstrap.Modal.getInstance(document.getElementById('confirmDeleteModal'));
            deleteCategoryModal.hide();

            FetchCategories(); // Refresh the categories list
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while deleting the category.');
        }
    });

    const editForm = document.getElementById('editCategoryForm');

    editForm.addEventListener('submit', async function(event) {
        event.preventDefault();

        const formData = new FormData(editForm);

        try {
            const categoryId = editForm.getAttribute('data-id');

            const response = await fetch(`/AdminPanel/Categories/OPS/${categoryId}`, {
                method: 'PUT',
                body: formData
            });

            const data = await response.json();

            // Hide the modal
            const editCategoryModal = bootstrap.Modal.getInstance(document.getElementById('editCategoryModal'));
            editCategoryModal.hide();

            FetchCategories(); // Refresh the categories list
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while updating the category.');
        }
    });
}


async function FetchUsers() {
    let response = await fetch('/AdminPanel/Users/OPS');
    let data = await response.json();
    const table = document.getElementById('usersTableBody');
    table.innerHTML = ''; // Clear existing table rows if any
    data.forEach(item => {
        let row = document.createElement('tr');
        row.innerHTML = `<td>${item.id}</td>
                        <td>${item.name}</td>
                        <td>${item.description}</td>
                        <td><img src="${item.image_file}" alt="Category Image" width="50" height="50"></td>
                        <td>${item.slug}</td>
                        <td>${new Date(item.created_at).toLocaleString()}</td>
                        <td>${new Date(item.updated_at).toLocaleString()}</td>
                        <td><button class="btn btn-warning btn-sm" data-bs-target="#confirmEditModal" data-bs-toggle="modal" id="editButton">Edit</button> <button class="btn btn-danger btn-sm" data-bs-targer="#confirmDeleteModal" data-bs-toggle="modal" id="deleteButton" > Delete </button></td>`;
        table.appendChild(row);
    });
}


async function FetchProducts()
{
    let response = await fetch('/AdminPanel/Products/OPS', { method: 'GET' });
    let data = await response.json();
    const table = document.getElementById('productsTableBody');
    table.innerHTML = ''; // Clear existing table rows if any
    data.forEach(item => {
        let row = document.createElement('tr');
        row.innerHTML = `<td>${item.id}</td>
                            <td>${item.name}</td>
                            <td>${item.description}</td>
                            <td>${item.price}</td>
                            <td>${item.category_name}</td>
                            <td><img src="${item.image_url}" alt="Product Image" width="50" height="50"></td>
                            <td>${item.stock_quantity}</td>
                            <td>${item.sku}</td>
                            <td>${item.brand}</td>
                            <td>${item.weight}</td>
                            <td>${item.dimensions}</td>
                            <td>${item.color}</td>
                            <td>${item.size}</td>
                            <td>${item.material}</td>
                            <td>${item.features}</td>
                            <td>${item.tags}</td>
                            <td>${item.discount_price}</td>
                            <td>${item.availability_status}</td>
                            <td>${item.rating}</td>
                            <td>${item.date_added}</td>
                            <td>${item.date_modified}</td>
                            <td>${item.reviews}</td>
                            <td>
                                <button class="btn btn-warning btn-sm editButton" data-bs-toggle="modal" data-bs-target="#confirmEditModal" data-id="${item.id}">Edit</button>
                                <button class="btn btn-danger btn-sm deleteButton" data-bs-toggle="modal" data-bs-target="#confirmDeleteModal" data-id="${item.id}">Delete</button>
                            </td>`;
        table.appendChild(row);
    });
    response = await fetch('/AdminPanel/Categories/OPS', { method: 'GET' });
    data = await response.json();    
    select = document.getElementById('categoriesNames');
    select.innerHTML="";
    data.forEach(item => {
        let option = document.createElement('option');
        option.value = item.id;
        option.text = item.name;
        select.appendChild(option);
    });


}

async function FetchSelectMenu()
{
    let response = await fetch('/AdminPanel/Categories/OPS', { method: 'GET' });
    let data = await response.json();
    let select = document.getElementById('categoryOptions');
    select.innerHTML = '';
     
    data.forEach(item => {
        let option = document.createElement('option');
        option.value = item.id;
        option.text = item.name;
        select.appendChild(option);
    });
    
}


async function AddProduct() {
    const form = document.getElementById("addProductForm");
    form.addEventListener("submit", async function(event) {
        event.preventDefault(); // Prevent default form submission

        const formData = new FormData(form);

        try {
            const response = await fetch('/AdminPanel/Products/OPS', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Hide the modal
            const addProductModal = bootstrap.Modal.getInstance(document.getElementById('addProductModal'));
            addProductModal.hide();

            FetchProducts(); // Refresh the product list

        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while adding the Product.');
        }
    });
}

async function DeleteAndEditProduct(){
    document.getElementById('productsTableBody').addEventListener('click', function(event) {
        const product_id = event.target.getAttribute('data-id');
        if (event.target.classList.contains('editButton')) {
        // Implement edit functionality here
    } else if (event.target.classList.contains('deleteButton')) {
        const deleteForm = document.getElementById('deleteProductForm');
        deleteForm.setAttribute('data-id', product_id);
    }
    });
    
    document.getElementById('deleteProductForm').addEventListener('submit', async function(event) {
        event.preventDefault(); // Prevent default form submission
    
    const productId = event.target.getAttribute('data-id');
    
    try {
        const response = await fetch(`/AdminPanel/Products/OPS/${productId}`, {
            method: 'DELETE'
        });
    const data = await response.json();

    // Hide the modal
    const deleteProductModal = bootstrap.Modal.getInstance(document.getElementById('confirmDeleteModal'));
    deleteProductModal.hide();
    
    FetchProducts(); // Refresh the categories list

    } catch (error) {
        console.error('Error:', error);
    alert('An error occurred while deleting the Product.');
    }
    });
    
}
