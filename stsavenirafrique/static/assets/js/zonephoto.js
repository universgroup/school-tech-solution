 
 // Fonction commune : affiche l'aperçu à partir d'un objet File
    function afficherApercuPhoto(file) {
    if (!file || !file.type.startsWith("image/")) return;
        var reader = new FileReader();
        reader.onload = function(e) {
        $("#photoPreview").attr("src", e.target.result).show();
        $("#photoPlaceholder").hide();
        };
        reader.readAsDataURL(file);
    }

    // Cas 1 : sélection classique via le clic (input file)
    // Photo de l'élève dans le template inscription
    function previewPhoto(input) {
        if (input.files && input.files[0]) {
        afficherApercuPhoto(input.files[0]);
        }
    }

    
    // Cette partie du code permet de glisser-deposer une photo dans la zone de photo
    var dropZone = document.getElementById("photoZone");
    var inputFile = document.getElementById("id_photo_identite");

    // Empêcher le navigateur d'ouvrir l'image dans un nouvel onglet
    ["dragenter", "dragover", "dragleave", "drop"].forEach(function(evt){
                dropZone.addEventListener(evt, function(e){
                e.preventDefault();
                e.stopPropagation();
                });
    });

    // Effet visuel pendant le survol avec un fichier
    ["dragenter", "dragover"].forEach(function(evt){
                dropZone.addEventListener(evt, function(){
                dropZone.classList.add("drag-over");
                });
    });
    
    ["dragleave", "drop"].forEach(function(evt){
                dropZone.addEventListener(evt, function(){
                dropZone.classList.remove("drag-over");
                });
    });
   
    // Cas 2 : dépôt du fichier (drag & drop)
    dropZone.addEventListener("drop", function(e){
            var files = e.dataTransfer.files;
            if (files.length > 0) {
            inputFile.files = files;
            // injecte le fichier dans l'input Django
            afficherApercu(files[0]);
            }
    });


    // Fonction commune : affiche l'aperçu du logo de l'ecole
    function afficherApercuLogo(file) {
    if (!file || !file.type.startsWith("image/")) return;
        var reader = new FileReader();
        reader.onload = function(e) {
        $("#logoPreview").attr("src", e.target.result).show();
        $("#logoPlaceholder").hide();
        };
        reader.readAsDataURL(file);
    }

    // Logo Ecole
    function previewLogoEcole(input) {
        if (input.files && input.files[0]) {
        afficherApercuLogo(input.files[0]);
        }
    }

    // Cas du template enregsitrer une ecole
    var logoZone = document.getElementById("logoZone");
    var logoinputFile = document.getElementById("id_logo_ecole");

    // Empêcher le navigateur d'ouvrir l'image dans un nouvel onglet
    ["dragenter", "dragover", "dragleave", "drop"].forEach(function(evt){
                logoZone.addEventListener(evt, function(e){
                e.preventDefault();
                e.stopPropagation();
                });
    });

    // Effet visuel pendant le survol avec un fichier
    ["dragenter", "dragover"].forEach(function(evt){
                logoZone.addEventListener(evt, function(){
                logoZone.classList.add("drag-over");
                });
    });
    
    ["dragleave", "drop"].forEach(function(evt){
                logoZone.addEventListener(evt, function(){
                logoZone.classList.remove("drag-over");
                });
    });
   
    // Cas 2 : dépôt du fichier (drag & drop)
    logoZone.addEventListener("drop", function(e){
            var files = e.dataTransfer.files;
            if (files.length > 0) {
            logoinputFile.files = files;
            // injecte le fichier dans l'input Django
            afficherApercu(files[0]);
            }
    });


    // Fonction commune : affiche l'aperçu de la signature du DG
    function afficherApercuDG(file) {
    if (!file || !file.type.startsWith("image/")) return;
        var reader = new FileReader();
        reader.onload = function(e) {
        $("#SignaDGPreview").attr("src", e.target.result).show();
        $("#SignaDGPlaceholder").hide();
        };
        reader.readAsDataURL(file);
    }

    // Signqture DG
    function previewSignatureDG(input) {
        if (input.files && input.files[0]) {
        afficherApercuDG(input.files[0]);
        }
    }

    // Cas du template enregsitrer une ecole
    var signaDGZone = document.getElementById("signaDGZone");
    var dginputFile = document.getElementById("id_signa_dg");

    // Empêcher le navigateur d'ouvrir l'image dans un nouvel onglet
    ["dragenter", "dragover", "dragleave", "drop"].forEach(function(evt){
                signaDGZone.addEventListener(evt, function(e){
                e.preventDefault();
                e.stopPropagation();
                });
    });

    // Effet visuel pendant le survol avec un fichier
    ["dragenter", "dragover"].forEach(function(evt){
                signaDGZone.addEventListener(evt, function(){
                signaDGZone.classList.add("drag-over");
                });
    });
    
    ["dragleave", "drop"].forEach(function(evt){
                signaDGZone.addEventListener(evt, function(){
                signaDGZone.classList.remove("drag-over");
                });
    });
   
    // Cas 2 : dépôt du fichier (drag & drop)
    signaDGZone.addEventListener("drop", function(e){
            var files = e.dataTransfer.files;
            if (files.length > 0) {
            dginputFile.files = files;
            // injecte le fichier dans l'input Django
            afficherApercu(files[0]);
            }
    });


    // Fonction commune : affiche l'aperçu de la signature du DE
    function afficherApercuDE(file) {
    if (!file || !file.type.startsWith("image/")) return;
        var reader = new FileReader();
        reader.onload = function(e) {
        $("#SignaDEPreview").attr("src", e.target.result).show();
        $("#SignaDEPlaceholder").hide();
        };
        reader.readAsDataURL(file);
    }

    // Signature du DE
    function previewSignatureDE(input) {
        if (input.files && input.files[0]) {
        afficherApercuDE(input.files[0]);
        }
    }

    // Cas du template enregsitrer une ecole
    var signaDEZone = document.getElementById("signaDEZone");
    var deinputFile = document.getElementById("id_signa_de");

    // Empêcher le navigateur d'ouvrir l'image dans un nouvel onglet
    ["dragenter", "dragover", "dragleave", "drop"].forEach(function(evt){
                signaDEZone.addEventListener(evt, function(e){
                e.preventDefault();
                e.stopPropagation();
                });
    });

    // Effet visuel pendant le survol avec un fichier
    ["dragenter", "dragover"].forEach(function(evt){
                signaDEZone.addEventListener(evt, function(){
                signaDEZone.classList.add("drag-over");
                });
    });
    
    ["dragleave", "drop"].forEach(function(evt){
                signaDEZone.addEventListener(evt, function(){
                signaDEZone.classList.remove("drag-over");
                });
    });
   
    // Cas 2 : dépôt du fichier (drag & drop)
    signaDEZone.addEventListener("drop", function(e){
            var files = e.dataTransfer.files;
            if (files.length > 0) {
            deinputFile.files = files;
            // injecte le fichier dans l'input Django
            afficherApercu(files[0]);
            }
    });

    // Pour la photo de l'élève
    function resetPhotoZone() {
        $("#id_photo_identite").val("");            // vide le contenu du input file
        $("#photoPreview").attr("src", "").hide();  // masque et vide l'aperçu
        $("#photoPlaceholder").show();               // réaffiche l'icône + le texte par défaut
    }

    // Pour le logo de l'ecole
    function resetLogoZone() {
        $("#id_logo_ecole").val("");            // vide le contenu du input file
        $("#logoPreview").attr("src", "").hide();  // masque et vide l'aperçu
        $("#logoPlaceholder").show();               // réaffiche l'icône + le texte par défaut
    }

    // Pour la signature du DG
    function resetSignaDGZone() {
        $("#id_signa_dg").val("");            // vide le contenu du input file
        $("#SignaDGPreview").attr("src", "").hide();  // masque et vide l'aperçu
        $("#SignaDGPlaceholder").show();               // réaffiche l'icône + le texte par défaut
    }

    // Pour la signature du DE
    function resetSignaDEZone() {
        $("#id_signa_de").val("");            // vide le contenu du input file
        $("#SignaDEPreview").attr("src", "").hide();  // masque et vide l'aperçu
        $("#SignaDEPlaceholder").show();               // réaffiche l'icône + le texte par défaut
    }