$("form").on("submit", function(e) {
    $("#loading").show();
})

const emptyContainer = document.getElementById("empty-container");
const searhContainer = document.getElementById("search-container");
const searhContainer2 = document.getElementById("search-container2");
const dataContainer = document.getElementById("data-container");
const typeSearch = document.getElementById("type-search");
let curpFilter = document.getElementById("curp-filter");
let fisicaFilter = document.getElementById("fisica-filter");
let currContainer = 0;

window.addEventListener("load", function() {
    if(typeSearch.value === "1" || typeSearch.value === "2")
        activeContainer(2);
    else
        activeContainer(currContainer);

    document.getElementById("consultar").addEventListener("click", function(e) {
        e.preventDefault();
        activeContainer(1);
    });
    document.getElementById("historial").addEventListener("click", function(e) {
        e.preventDefault();
        activeContainer(2);
    });
    curpFilter.addEventListener("click", function(e) {
        e.preventDefault();
        typeSearch.value = 1;
    });
    fisicaFilter.addEventListener("click", function(e) {
        e.preventDefault();
        typeSearch.value = 2;
    });
});

function activeContainer(index=0) {
    emptyContainer.classList.add("d-none");
    searhContainer.classList.add("d-none");
    searhContainer2.classList.add("d-none");
    dataContainer.classList.add("d-none");

    if(currContainer !== index) {
        if(index === 0)
            emptyContainer.classList.remove("d-none");
        else if(index === 1) {
            searhContainer.classList.remove("d-none");
            searhContainer2.classList.remove("d-none");
        } else if(index === 2)
            dataContainer.classList.remove("d-none");
    } else {
        index = 0;
        emptyContainer.classList.remove("d-none");
    }
    currContainer = index;
}
