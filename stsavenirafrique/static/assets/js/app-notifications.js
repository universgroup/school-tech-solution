(function () {

    const CLASSES_BOOTSTRAP = {
        'success': 'alert-success',
        'warning': 'alert-warning',
        'info':    'alert-info',
        'error':   'alert-danger'
    };

    const DUREE_MS = 4000;

    window.afficherMessage = function (type, texte) {
        const classeAlerte = CLASSES_BOOTSTRAP[type] || 'alert-info';

        const $alerte = $(`
            <div class="alert ${classeAlerte} alert-dismissible notif-cool" role="alert">
                <button type="button" class="close" data-dismiss="alert" aria-label="close">
                    <span aria-hidden="true">&times;</span>
                </button>
                <div class="notif-cool-corps">
                    <i class="notif-cool-icone notif-icone-${classeAlerte}"></i>
                    <span class="notif-cool-texte">${texte}</span>
                </div>
                <div class="notif-cool-barre"></div>
            </div>
        `);

        $('#toast-container').append($alerte);

        requestAnimationFrame(function () {
            $alerte.find('.notif-cool-barre').css('transition', `width ${DUREE_MS}ms linear`).css('width', '0%');
        });

        const minuteur = setTimeout(fermer, DUREE_MS);

        $alerte.hover(
            function () {
                clearTimeout(minuteur);
                $alerte.find('.notif-cool-barre').css('transition', 'none');
            },
            function () {
                setTimeout(fermer, 1200);
            }
        );

        $alerte.find('.close').on('click', fermer);

        function fermer() {
            $alerte.addClass('notif-cool-sortie');
            setTimeout(() => $alerte.remove(), 300);
        }
    };

    // Convertit les messages Django rendus classiquement (non-AJAX) en toasts
    $(function () {
        $('#zone-messages .alert').each(function () {
            const $original = $(this);
            const classeAlerte = ['alert-success', 'alert-warning', 'alert-info', 'alert-danger']
                .find(c => $original.hasClass(c)) || 'alert-info';
            const texte = $original.find('.notif-cool-texte').length
                ? $original.find('.notif-cool-texte').text()
                : $original.clone().children().remove().end().text().trim();

            $original.closest('.container-fluid').remove(); // on retire l'original du flux normal
            const typeInterne = Object.keys(CLASSES_BOOTSTRAP).find(k => CLASSES_BOOTSTRAP[k] === classeAlerte) || 'info';
            window.afficherMessage(typeInterne, texte);
        });
    });

})();