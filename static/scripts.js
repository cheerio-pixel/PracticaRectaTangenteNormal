 // Redirigir a la sección de Home al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    window.location.href = '#Home'
});



//Sidebar activado
const btnToggle = document.querySelector('.toggle-btn');
const sidebar = document.getElementById('sidebar');

btnToggle.addEventListener('click', function(){
    sidebar.classList.toggle('active');
});
//Barra de navegacion
const navbarToggler = document.querySelector('.navbar-toggler');
const navScrollable = document.querySelector('.nav-scrollable');

navbarToggler.addEventListener('click', () => {
    navScrollable.classList.toggle('collapse');
});
async function click_image() {
    var res = await fetch(`/pyplot`)
    var blob = await res.blob()
    var imageUrl = URL.createObjectURL(blob);
    document.querySelector("#image").src = imageUrl;
}
function showAlert(message) {
const alertElement = document.querySelector('.alert');
const alertMessage = alertElement.querySelector('.msg');
alertMessage.textContent = message;

const closeBtn = alertElement.querySelector('.close-btn');
closeBtn.addEventListener('click', () => {
    alertElement.classList.add('hide');
});

  alertElement.classList.remove('hide'); // Mostrar la alerta solo cuando hay un error
}

//Efecto boton del landing
const landingCtaButton = document.querySelector('.landing-cta .btn');
const landingSection = document.querySelector('.landing-cta');
const landingSectionTittle = document.querySelector('.landing-header');
const calculatorSection = document.getElementById('Calculadora');

    landingCtaButton.addEventListener('click', function(event) {
        event.preventDefault();
        landingSection.style.display = 'none';
        landingSectionTittle.style.display = 'none';
        calculatorSection.style.display = 'block';
        calculatorSection.scrollIntoView({ behavior: 'smooth' });
    });
    
//No poder funcionalidad del home en el sidebar
    const homeLink = document.querySelector('[data-content-id="Home"]');
    homeLink.addEventListener('click', function() {
        landingSection.style.display = 'block';
        landingSectionTittle.style.display= 'block';
        calculatorSection.style.display = 'none';
    });

//Ocultar y mostrar contenidos
document.addEventListener('DOMContentLoaded', function() {
  const links = document.querySelectorAll('.nav-item a');
  const contentSections = document.querySelectorAll('.page');

  links.forEach(link => {
      link.addEventListener('click', function(event) {
          event.preventDefault();
          const contentId = this.getAttribute('data-content-id');

          // Oculta todas las secciones de contenido
          contentSections.forEach(section => {
              section.style.display = 'none';
          });

          // Muestra solo la sección de contenido
          const contentSection = document.getElementById(contentId);
          if (contentSection) {
              contentSection.style.display = 'block';
          }
      });
  });

  // Mostrar la primera imagen por defecto al cargar la página
    const firstImage = document.getElementById('image4');

    const selectCheckbox = document.querySelectorAll('.select-checkbox');
    selectCheckbox.forEach(checkbox => {
        checkbox.addEventListener('click', onCheckBox);
        firstImage.classList.add('active');
    });
});


document.addEventListener('DOMContentLoaded', function() {
    const selectButtons = document.querySelectorAll('.select-button');
    selectButtons.forEach(button => {
        button.addEventListener('click', function() {
            const imageNumber = parseInt(this.getAttribute('data-image-number'));
            selectImage(imageNumber);

            // Agregar/Quitar la clase 'active' solo al botón clickeado
            selectButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
        });
    });
});

function onCheckBox() {
    const selectCheckbox = document.querySelectorAll('.select-checkbox');
    let state = 1;
    selectCheckbox.forEach(
        checkbox => {
            if (checkbox.checked) {
                state += parseInt(checkbox.value)
            }
        }
    )
    selectImage(state);
}

// Función para seleccionar una imagen específica y superponerla
function selectImage(imageNumber) {
  const images = document.querySelectorAll('.image');
  images.forEach(image => image.classList.remove('active'));

  const selectedImage = document.getElementById(`image${imageNumber}`);
  selectedImage.classList.add('active');
}

async function click_multiple_images() {
    // encodeURIComponent para encodee los caracteres especiales
    var f = encodeURIComponent(document.querySelector("#Operacion").value)
    var c = encodeURIComponent(document.querySelector("#punto").value)
    try {
        document.querySelector(".loader").style.display = "block"
        document.querySelector(".image-stack").style.display = "none"
        var res = await fetch(String.raw`/pyplot/?&f=${f}&c=${c}`)
        document.querySelector(".loader").style.display = "none"
        document.querySelector(".image-stack").style.display = "block"

        if (!res.ok) {
            throw new Error("Network response was not OK");
        }
        var blob_json = await res.json();
        if (blob_json["status"] === -1) {
            showAlert("Hubo un error en la expresion");
        } else if (blob_json["status"] === -2) {
            showAlert("Hubo un problema con el numero ingresado");
        } else if (blob_json["status"] === -3) {
            showAlert("Solo se puede usar la variable 'x'");
        } else if (blob_json["status"] === -4) {
            showAlert("La función está fuera de su dominio");
        } else if (blob_json["status"] === -5) {
            showAlert("No se puede dividir por 0");
        }
        else {
            for (let index = 0; index < blob_json["result"].length; index++) {
                var buf = blob_json["result"][index];
                const image = document.querySelector(`#image${index + 1}`);
                image.src = "data:image/png;base64, " + buf;
                image.style.display = 'block';
            }
        }
    } catch (error) {
        console.log("Catched an error")
    }
}
