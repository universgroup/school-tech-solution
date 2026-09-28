// Garde ouvert dans le sidebar l'onglet correspondant à la page affichée

document.addEventListener('DOMContentLoaded', function () {
    var currentPath = window.location.pathname;

    document.querySelectorAll('.nav-sidebar .nav-treeview a.nav-link').forEach(function (link) {
        var href = link.getAttribute('href');

        // On ignore les liens non encore fonctionnels ("#") : ils ne
        // provoquent aucune navigation, donc rien à restaurer pour eux.
        if (!href || href === '#') return;

        if (link.pathname === currentPath) {
            link.classList.add('active');

            var parentTreeview = link.closest('ul.nav-treeview');
            var parentLi = parentTreeview ? parentTreeview.closest('li.nav-item.has-treeview') : null;

            if (parentLi) {
                parentLi.classList.add('menu-open');
                var parentLink = parentLi.querySelector(':scope > a.nav-link');
                if (parentLink) {
                    parentLink.classList.add('active');
                }
            }
        }
    });
});