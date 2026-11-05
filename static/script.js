$(document).ready(function() {
    $('#capture-btn').click(function() {
        $.ajax({
            type: 'POST',
            url: '/start_capture',
            success: function(response) {
                // Téléchargement du fichier PDF généré
                window.location.href = '/' + response;
            }
        });
    });
});