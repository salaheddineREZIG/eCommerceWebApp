async function AdminSearchBar() {
    const typeInput = document.getElementById('typeInput');
    const searchInput = document.getElementById('searchInput');
    const submitButton = document.getElementById('searchButton');
    const searchResults = document.getElementById('searchResults');

    typeInput.addEventListener('change', function () {
        if (typeInput.value) {
            searchInput.disabled = false;
            submitButton.disabled = false;
        } else {
            searchInput.disabled = true;
            submitButton.disabled = true;
        }
    });

    searchInput.addEventListener('input', async function () {
        const typeValue = typeInput.value;
        const searchValue = searchInput.value;

        if (typeValue && searchValue) {
            try {
                let response = await fetch(`/AdminPanel/Dashboard/Search?search=${encodeURIComponent(searchValue)}&type=${encodeURIComponent(typeValue)}`);
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

                let data = await response.json();

                searchResults.innerHTML = "";
                data.forEach(item => {
                    let li = document.createElement("li");
                    li.className = "list-group-item";
                    li.textContent = Object.values(item)[0];
                    li.addEventListener("click", function () {
                        searchInput.value = Object.values(item)[0];
                        searchResults.innerHTML = "";
                        searchResults.style.display = 'none';
                    });
                    searchResults.appendChild(li);
                });
                searchResults.style.display = 'block';
            } catch (error) {
                console.error('Error fetching search results:', error);
                searchResults.innerHTML = `<li class="list-group-item text-danger">Error fetching search results</li>`;
                searchResults.style.display = 'block';
            }
        } else {
            searchResults.innerHTML = "";
            searchResults.style.display = 'none';
        }
    });
}

function FlashMessage(message,type){
    const FlashMessage = document.getElementById('flashMessage');
    FlashMessage.innerHTML = `<div class="alert  alert-` + type +` alert-dismissible fade show" role="alert">`+ message + `<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>`;

}



async function FetchStats() {
    try {
        let response = await fetch("/AdminPanel/Dashboard/Stats");
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

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
                div.innerHTML = `<h6 class="mb-1"> new orders ${stats.newOrders[i].order_items}</h6><span class="mb-0"></span>`;
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
    } catch (error) {
        console.error('Error fetching stats:', error);

        let errorDiv = document.getElementById("error");
        if (errorDiv) {
            errorDiv.innerHTML = `<div class="alert alert-danger" role="alert">Error fetching stats: ${error.message}</div>`;
        }
    }
}

async function FetchCategories() {
    try {
        const response = await fetch('/AdminPanel/Categories/OPS');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const data = await response.json();
        const table = document.getElementById('categoriesTableBody');
        table.innerHTML = '';

        data.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.id}</td>
                <td>${item.name}</td>
                <td>${item.description}</td>
                <td><img src="/static/images/uploads/${item.image_file}" alt="Category Image" width="50" height="50"></td>
                <td>${item.slug}</td>
                <td>${new Date(item.created_at).toLocaleString()}</td>
                <td>${new Date(item.updated_at).toLocaleString()}</td>
                <td>
                    <button class="btn btn-warning btn-sm editButton" data-bs-toggle="modal" data-bs-target="#editCategoryModal"
                            data-name="${item.name}" data-description="${item.description}" data-image="${item.image_file}" data-slug="${item.slug}">Edit</button>
                    <button class="btn btn-danger btn-sm deleteButton" data-bs-toggle="modal" data-bs-target="#confirmDeleteModal"
                            data-slug="${item.slug}">Delete</button>
                </td>`;
            table.appendChild(row);
        });
    
    } catch (error) {
        console.error('Error fetching categories:', error);
        DisplayError(`Error fetching categories: ${error.message}`);
    }
}


function DisplayError(message) {
    const errorDiv = document.getElementById("error");
    if (errorDiv) {
        errorDiv.innerHTML = `<div class="alert alert-danger" role="alert">${message}</div>`;
    }
}

async function AddCategory() {
    const form = document.getElementById("addCategoryForm");
    form.addEventListener("submit", async function(event) {
        event.preventDefault();

        const formData = new FormData(form);

        try {
            const submitButton = form.querySelector('button[type="submit"]');
            submitButton.disabled = true; // Disable submit button to prevent multiple submissions
            submitButton.innerText = 'Submitting...'; // Indicate submission process

            const response = await fetch('/AdminPanel/Categories/OPS', {
                method: 'POST',
                body: formData
            });

            submitButton.disabled = false; // Re-enable submit button
            submitButton.innerText = 'Submit'; // Reset button text

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const data = await response.json();

            if (data.error) throw new Error(data.error);

            FlashMessage(data.message, 'success');

            const addCategoryModal = bootstrap.Modal.getInstance(document.getElementById('addCategoryModal'));
            addCategoryModal.hide();
            form.reset();
            FetchCategories();
        } catch (error) {
            console.error('Error:', error);
            alert(`An error occurred while adding the category: ${error.message}`);
        }
    });
}


async function DeleteAndEditCategory() {
    document.getElementById('categoriesTableBody').addEventListener('click', function(event) {
        const target = event.target;
        
        if (target.classList.contains('editButton')) {
            HandleEditButtonClick(target);
        } else if (target.classList.contains('deleteButton')) {
            HandleDeleteButtonClick(target);
        }
    });

    document.getElementById('deleteCategoryForm').addEventListener('submit', async function(event) {
        event.preventDefault();
        const slug = event.target.getAttribute('data-slug'); // Retrieve the slug from the form's attribute

        const submitButton = event.target.querySelector('button[type="submit"]');
        submitButton.disabled = true; // Disable submit button to prevent multiple submissions
        submitButton.innerText = 'Deleting...'; // Indicate submission process

        try {
            const response = await fetch(`/AdminPanel/Categories/OPS/${slug}`, {
                method: 'DELETE'
            });
    
            submitButton.disabled = false; // Re-enable submit button
            submitButton.innerText = 'Delete'; // Reset button text

            if (!response.ok) throw new Error(`Failed to delete category. Status: ${response.status}`);
            const data = await response.json();
            const deleteCategoryModal = bootstrap.Modal.getInstance(document.getElementById('confirmDeleteModal'));
            deleteCategoryModal.hide();
            
            FlashMessage(data.message, 'success');
            FetchCategories();
        } catch (error) {
            console.error('Error:', error);
            alert(`An error occurred while deleting the category: ${error.message}`);
        }
    });

    document.getElementById('editCategoryForm').addEventListener('submit', async function(event) {
        event.preventDefault();
        const editForm = document.getElementById('editCategoryForm');
        const formData = new FormData(editForm);

        const submitButton = event.target.querySelector('button[type="submit"]');
        submitButton.disabled = true; // Disable submit button to prevent multiple submissions
        submitButton.innerText = 'Updating...'; // Indicate submission process

        try {
            const categorySlug = editForm.getAttribute('data-slug');
            const response = await fetch(`/AdminPanel/Categories/OPS/${categorySlug}`, {
                method: 'PUT',
                body: formData
            });

            submitButton.disabled = false; // Re-enable submit button
            submitButton.innerText = 'Update'; // Reset button text

            if (!response.ok) throw new Error(`Failed to update category. Status: ${response.status}`);

            const data = await response.json();
            FlashMessage(data.message, 'success');

            const editCategoryModal = bootstrap.Modal.getInstance(document.getElementById('editCategoryModal'));
            editCategoryModal.hide();

            FetchCategories();
        } catch (error) {
            console.error('Error:', error);
            alert(`An error occurred while updating the category: ${error.message}`);
        }
    });

    document.getElementById("deleteCategoryImageButton").addEventListener("click", async function(event) {
        event.preventDefault();

        const submitButton = event.target;
        submitButton.disabled = true; // Disable submit button to prevent multiple submissions
        submitButton.innerText = 'Deleting...'; // Indicate submission process

        try {
            const imageFile = event.target.getAttribute("data-image_file");
            const slug = event.target.getAttribute("data-slug");

            if (!imageFile) throw new Error("No image file selected");
            if (!slug) throw new Error("No slug provided");

            const response = await fetch(`/AdminPanel/Files/${imageFile}?slug=${slug}&type=category`, {
                method: 'DELETE'
            });
    
            submitButton.disabled = false; // Re-enable submit button
            submitButton.innerText = 'Delete Image'; // Reset button text
    
            if (!response.ok) throw new Error(`Failed to delete image. Status: ${response.status}`);
    
            const data = await response.json();
            FetchCategories();
            FlashMessage(data.message, 'success');

            const deleteCategoryModal = bootstrap.Modal.getInstance(document.getElementById('editCategoryModal'));
            deleteCategoryModal.hide();
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while deleting the image: ' + error.message);
        }
    });
}

function HandleEditButtonClick(editButton) {
    const categoryName = editButton.getAttribute('data-name');
    const categoryDescription = editButton.getAttribute('data-description');
    const categoryImage = editButton.getAttribute('data-image');
    const categorySlug = editButton.getAttribute('data-slug');
    const editForm = document.getElementById('editCategoryForm');

    editForm.setAttribute('data-slug', categorySlug);
    document.getElementById('editName').value = categoryName;
    document.getElementById('editDescription').value = categoryDescription;
    document.getElementById('editSlug').value = categorySlug;
    document.getElementById('editCategoryImageFileSpan').innerHTML = `Image File: ${categoryImage}`;

    const deleteButton = document.getElementById('deleteCategoryImageButton');
    if (categoryImage !== 'default.jpg') {
        deleteButton.removeAttribute('disabled');
    }
    deleteButton.setAttribute('data-slug', categorySlug);
    deleteButton.setAttribute('data-image_file', categoryImage);
}

function HandleDeleteButtonClick(deleteButton) {
    const categorySlug = deleteButton.getAttribute('data-slug');
    const deleteForm = document.getElementById('deleteCategoryForm');
    deleteForm.setAttribute('data-slug', categorySlug); // Correctly set the slug here
}

async function FetchProducts() {
    const table = document.getElementById('productsTableBody');
    table.innerHTML = '<tr><td colspan="23">Loading...</td></tr>'; // Add a loading indicator

    try {
        let response = await fetch('/AdminPanel/Products/OPS');

        if (!response.ok) {
            throw new Error(`Failed to fetch products. Status: ${response.status}`);
        }

        let data = await response.json();
        table.innerHTML = ''; // Clear existing table rows if any

        data.forEach(item => {
            let row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.id}</td>
                <td>${item.name}</td>
                <td>${item.description}</td>
                <td>${item.slug}</td>
                <td>${item.price}</td>
                <td>${item.category_name}</td>
                <td><img src="/static/images/uploads/${item.image_file}" alt="Product Image" width="50" height="50"></td>
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
                <td>${new Date(item.date_added).toLocaleString()}</td>
                <td>${new Date(item.date_modified).toLocaleString()}</td>
                <td>${item.reviews}</td>
                <td>
                    <button class="btn btn-warning btn-sm editButton" data-bs-toggle="modal" data-bs-target="#editProductModal" 
                            data-name="${item.name}" data-description="${item.description}" data-slug="${item.slug}" data-price="${item.price}" 
                            data-category_id="${item.category_id}" data-image_file="${item.image_file}" data-stock_quantity="${item.stock_quantity}" 
                            data-sku="${item.sku}" data-brand="${item.brand}" data-weight="${item.weight}" data-dimensions="${item.dimensions}" 
                            data-color="${item.color}" data-size="${item.size}" data-material="${item.material}" data-features="${item.features}" 
                            data-tags="${item.tags}" data-discount_price="${item.discount_price}" data-availability_status="${item.availability_status}">Edit</button>
                    <button class="btn btn-danger btn-sm deleteButton" data-bs-toggle="modal" data-bs-target="#confirmDeleteModal" 
                            data-slug="${item.slug}">Delete</button>
                </td>`;
            table.appendChild(row);
        });
    } catch (error) {
        console.error('Error:', error);
        table.innerHTML = '<tr><td colspan="23">An error occurred while fetching the products. Please try again later.</td></tr>';
    }
}


async function FetchCategoriesSelectMenu(optionId) {

    try {
        let response = await fetch('/AdminPanel/Categories/OPS', { method: 'GET' });

        if (!response.ok) {
            throw new Error(`Failed to fetch categories. Status: ${response.status}`);
        }

        let data = await response.json();
        let select = document.getElementById(optionId);

        if (!select) {
            console.error(`Element with id '${optionId}' not found.`);
            return;
        }

        select.innerHTML = '<option disabled selected>Loading...</option>'; // Loading indicator

        // Clear existing options and remove loading indicator
        select.innerHTML = '';
        
        data.forEach(item => {
            let option = document.createElement('option');
            option.value = item.id;
            option.text = item.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error fetching categories:', error);
        let select = document.getElementById(optionId);

        if (select) {
            select.innerHTML = '<option disabled selected>Error loading categories</option>';
        }
    }
}


async function AddProduct() {
    const form = document.getElementById("addProductForm");
    
    // Ensure the form exists
    if (!form) {
        console.error("Form element not found.");
        return;
    }
    
    form.addEventListener("submit", async function(event) {
        event.preventDefault(); // Prevent default form submission

        console.log("Add Product Form Submitted");

        // Disable submit button to prevent multiple submissions
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.innerText = 'Submitting...';

        // Create FormData object
        const formData = new FormData(form);
        console.log("Form Data:", formData);

        try {
            const response = await fetch('/AdminPanel/Products/OPS', {
                method: 'POST',
                body: formData
            });

            console.log("Response:", response);

            if (!response.ok) {
                // Extract and throw error details from the response
                const errorResponse = await response.json();
                throw new Error(errorResponse.error || `HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            console.log("Data:", data);

            // Show success message
            FlashMessage(data.message, 'success');

            // Hide modal and reset form
            const addProductModal = bootstrap.Modal.getInstance(document.getElementById('addProductModal'));
            addProductModal.hide();
            form.reset();

            // Refresh the product list
            FetchProducts(); 

        } catch (error) {
            console.error('Error:', error);
            alert(`An error occurred while adding the product: ${error.message}`);
        } finally {
            // Re-enable submit button and reset text
            submitButton.disabled = false;
            submitButton.innerText = 'Submit';
        }
    });
}



async function DeleteAndEditProduct() {
    document.getElementById('productsTableBody').addEventListener('click', function(event) {
        const target = event.target;

        if (target.classList.contains('editButton')) {
            HandleEditProductButtonClick(target);
        } else if (target.classList.contains('deleteButton')) {
            HandleDeleteProductButtonClick(target);
        }
    });

    document.getElementById('deleteProductForm').addEventListener('submit', async function(event) {
        event.preventDefault();
        const slug = event.target.getAttribute('data-slug');

        const submitButton = event.target.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.innerText = 'Deleting...';

        try {
            const response = await fetch(`/AdminPanel/Products/OPS/${slug}`, {
                method: 'DELETE'
            });

            submitButton.disabled = false;
            submitButton.innerText = 'Delete';

            if (!response.ok) throw new Error(`Failed to delete product. Status: ${response.status}`);
            const data = await response.json();
            const deleteProductModal = bootstrap.Modal.getInstance(document.getElementById('confirmDeleteModal'));
            deleteProductModal.hide();

            FlashMessage(data.message, 'success');
            FetchProducts();
        } catch (error) {
            console.error('Error:', error);
            alert(`An error occurred while deleting the product: ${error.message}`);
        }
    });

    document.getElementById('editProductForm').addEventListener('submit', async function(event) {
        event.preventDefault();
        const editForm = document.getElementById('editProductForm');
        const formData = new FormData(editForm);

        const submitButton = event.target.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.innerText = 'Updating...';

        try {
            const productSlug = editForm.getAttribute('data-slug');
            const response = await fetch(`/AdminPanel/Products/OPS/${productSlug}`, {
                method: 'PUT',
                body: formData
            });

            submitButton.disabled = false;
            submitButton.innerText = 'Update';

            if (!response.ok) throw new Error(`Failed to update product. Status: ${response.status}`);

            const data = await response.json();
            FlashMessage(data.message, 'success');

            const editProductModal = bootstrap.Modal.getInstance(document.getElementById('editProductModal'));
            editProductModal.hide();

            FetchProducts();
        } catch (error) {
            console.error('Error:', error);
            alert(`An error occurred while updating the product: ${error.message}`);
        }
    });

    document.getElementById("deleteProductImageButton").addEventListener("click", async function(event) {
        event.preventDefault();

        const submitButton = event.target;
        submitButton.disabled = true;
        submitButton.innerText = 'Deleting...';

        try {
            const imageFile = event.target.getAttribute("data-image_file");
            const slug = event.target.getAttribute("data-slug");

            if (!imageFile) throw new Error("No image file selected");
            if (!slug) throw new Error("No slug provided");

            const response = await fetch(`/AdminPanel/Files/${imageFile}?slug=${slug}&type=product`, {
                method: 'DELETE'
            });

            submitButton.disabled = false;
            submitButton.innerText = 'Delete Image';

            if (!response.ok) throw new Error(`Failed to delete image. Status: ${response.status}`);

            const data = await response.json();
            FetchProducts();
            FlashMessage(data.message, 'success');

            const deleteProductModal = bootstrap.Modal.getInstance(document.getElementById('editProductModal'));
            deleteProductModal.hide();
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while deleting the image: ' + error.message);
        }
    });
}

function HandleEditProductButtonClick(editButton) {
    const productName = editButton.getAttribute('data-name');
    const productDescription = editButton.getAttribute('data-description');
    const productSlug = editButton.getAttribute('data-slug');
    const productPrice = editButton.getAttribute('data-price');
    const productCategoryId = editButton.getAttribute('data-category_id');
    const productImageFile = editButton.getAttribute('data-image_file');
    const productStockQuantity = editButton.getAttribute('data-stock_quantity');
    const productSku = editButton.getAttribute('data-sku');
    const productBrand = editButton.getAttribute('data-brand');
    const productWeight = editButton.getAttribute('data-weight');
    const productDimensions = editButton.getAttribute('data-dimensions');
    const productColor = editButton.getAttribute('data-color');
    const productSize = editButton.getAttribute('data-size');
    const productMaterial = editButton.getAttribute('data-material');
    const productFeatures = editButton.getAttribute('data-features');
    const productTags = editButton.getAttribute('data-tags');
    const productDiscountPrice = editButton.getAttribute('data-discount_price');
    const productAvailabilityStatus = editButton.getAttribute('data-availability_status');
    const editForm = document.getElementById('editProductForm');

    editForm.setAttribute('data-slug', productSlug);
    document.getElementById('editProductName').value = productName;
    document.getElementById('editProductDescription').value = productDescription;
    document.getElementById('editProductSlug').value = productSlug;
    document.getElementById('editProductPrice').value = productPrice;
    document.getElementById('editCategoryId').value = productCategoryId;
    document.getElementById('editProductImageFileSpan').innerHTML = `Image File: ${productImageFile}`;
    document.getElementById('editProductStockQuantity').value = productStockQuantity;
    document.getElementById('editProductSku').value = productSku;
    document.getElementById('editProductBrand').value = productBrand;
    document.getElementById('editProductWeight').value = productWeight; 
    document.getElementById('editProductDimensions').value = productDimensions;
    document.getElementById('editProductColor').value = productColor;
    document.getElementById('editProductSize').value = productSize;
    document.getElementById('editProductMaterial').value = productMaterial;
    document.getElementById('editProductFeatures').value = productFeatures;
    document.getElementById('editProductTags').value = productTags;
    document.getElementById('editProductDiscountPrice').value = productDiscountPrice;
    document.getElementById('editProductAvailabilityStatus').value = productAvailabilityStatus;

    const deleteButton = document.getElementById('deleteProductImageButton');
    if (productImageFile !== 'default.jpg') {
        deleteButton.removeAttribute('disabled');
    }
    deleteButton.setAttribute('data-slug', productSlug);
    deleteButton.setAttribute('data-image_file', productImageFile);
}

function HandleDeleteProductButtonClick(deleteButton) {
    const productSlug = deleteButton.getAttribute('data-slug');
    const deleteForm = document.getElementById('deleteProductForm');
    deleteForm.setAttribute('data-slug', productSlug);
}




async function FetchUsers() {
    let response = await fetch('/AdminPanel/Users/OPS');
    let data = await response.json();
    const table = document.getElementById('usersTableBody');
    table.innerHTML = ''; // Clear existing table rows if any
    data.forEach(item => {
        let row = document.createElement('tr');
        row.innerHTML = `<td>${item.id}</td>
                        <td>${item.userName}</td>
                        <td>${item.email}</td>
                        <td>${item.phoneNumber}</td>
                        <td><img src="/static/images/uploads/${item.profilePicture}" alt="Profile Picture" width="50" height="50"></td>
                        <td>${item.created_at}</td>
                        <td>${item.updated_at}</td>
                        <td>                    
                        <button class="btn btn-danger btn-sm deleteButton" data-bs-toggle="modal" data-bs-target="#confirmDeleteModal" 
                        data-id="${item.id}" data-username="${item.userName}">Delete</button>
                        </td>`;
        table.appendChild(row);
    });
}

async function DeleteUser()
{
    document.getElementById('usersTableBody').addEventListener('click', async function(event) {
        if (event.target.classList.contains('deleteButton')) {
            const deleteButton = event.target;
            const userId = deleteButton.getAttribute('data-id');
            const userName = deleteButton.getAttribute('data-username');
            document.getElementById('userInfo').innerHTML = 'User Name: ' + userName ;
            
            document.getElementById('deleteUserForm').addEventListener('submit', async function(event) {
                
                try {
                    const response = await fetch(`/AdminPanel/Users/OPS/` + userId , {
                        method: 'DELETE'
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    const data = await response.json();
                    FlashMessage(data.message,'success')
                    
                    FetchUsers(); 

                } catch (error) {
                    console.error('Error:', error);
                    alert('An error occurred while deleting the product: ' + error.message);
                }
            });
        }
    });
}


async function FetchOrders()
{
    let response = await fetch('/AdminPanel/Orders/OPS');
    let data = await response.json();
    const table = document.getElementById('ordersTableBody');
    table.innerHTML = ''; // Clear existing table rows if any
    data.forEach(item => {
        let row = document.createElement('tr');
        row.innerHTML = `<td>${item.id}</td>
                        <td>${item.userId}</td>
                        <td>${item.orderDate}</td>
                        <td>${item.status}</td>
                        <td>${item.totalAmount}</td>
                        <td>${item.shippingAddress}</td>
                        <td>${item.orderItems}</td>
                        <td>                    
                        <button class="btn btn-danger btn-sm deleteButton" data-bs-toggle="modal" data-bs-target="#confirmDeleteModal" 
                        data-id="${item.id}">Delete</button>
                        <button class="btn btn-primary btn-sm editButton" data-bs-toggle="modal" data-bs-target="changeStatusModal" data-id="${item.id}">Change Status</button>
                        </td>`;
        table.appendChild(row);
    });
}

// Home Page

async function HomePageSearchBar()
{
    let input = document.getElementById("searchInput");
    input.addEventListener("input", async function() {
        if (input.value.trim().length > 0) {
            let response = await fetch("/HomePage/Search?search=" + encodeURIComponent(input.value));
            let data = await response.json();
            let ul = document.getElementById("searchResults");
            ul.innerHTML = "";
            data.forEach(item => {
                let li = document.createElement("li");
                li.className = "list-group-item";
                li.textContent = item.productName;
                li.addEventListener("click", function() {
                    input.value = item.productName;
                    ul.innerHTML = "";
                    ul.style.display = 'none';  
                });
                ul.appendChild(li);
            });
            ul.style.display = 'block';
        } else {
            document.getElementById("searchResults").innerHTML = "";
            document.getElementById("searchResults").style.display = 'none';
        }
    });

}

async function fetchInfo(url, listId, type) {
    try {
        const response = await fetch(url);
        const data = await response.json();
        const list = document.getElementById(listId);
        list.innerHTML = ''; // Clear existing list items

        const fragment = document.createDocumentFragment();
        data.forEach(item => {
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item';
            listItem.innerHTML = `<a href="/HomePage/` + type + `?slug=` + item.slug + `">`+ item.name + `</a>`;
            fragment.appendChild(listItem);
        });

        list.appendChild(fragment);
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}


async function OrderAndAddToCart(){

    document.getElementById('addToCartButton').addEventListener('click', async function(event) {

        event.preventDefault();
        productSlug = event.target.getAttribute('data-slug');

        try {

            const response = await fetch('/HomePage/Cart/OPS/' + productSlug, {
                    method: 'POST'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            FlashMessage(data.message,'success')

        }

        catch (error) {

            console.error('Error:', error);
            alert('An error occurred while adding the product to the cart: ' + error.message);

        }
    
    });

}


async function FetchCart(){
    document.getElementById('cartItems').innerHTML = '';
    let response = await fetch('/HomePage/Cart/OPS');
    let data = await response.json();
    data.forEach(item => {
        let row = document.createElement('tr');
        row.innerHTML = `<td> <a href="/HomePage/Products?slug=${item.productSlug}">${item.productName}</a></td>
                        <td>${item.productPrice}</td>
                        <td>${item.quantity}</td>
                        <td>${item.total_price}</td>
                        <td>
                        <button class="btn btn-danger btn-sm deleteButton" data-bs-toggle="modal" data-bs-target="#confirmDeleteModal" 
                        data-slug="${item.productSlug}">Delete</button>
                        </td>`;
        document.getElementById('cartItems').appendChild(row);
    });
}

async function DeleteCartItem(){
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('deleteButton')) {
            document.getElementById('deleteCartForm').setAttribute('data-slug', event.target.getAttribute('data-slug'));
        }
    });
    document.getElementById('deleteCartForm').addEventListener('submit', async function(event) {
        try {
            event.preventDefault();
            const slug = event.target.getAttribute('data-slug');
            const response = await fetch('/HomePage/Cart/OPS/' + slug, {
                method: 'DELETE'
            });
            const data = await response.json();
            FlashMessage(data.message,'success');

            const deleteCartForm = bootstrap.Modal.getInstance(document.getElementById('confirmDeleteModal'));
            deleteCartForm.hide();
            
            FetchCart();
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while deleting the product from the cart: ' + error.message);
        }
    });

}

