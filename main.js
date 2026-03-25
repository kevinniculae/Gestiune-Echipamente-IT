$(document).ready(function() {
    var tabelEchipamente = $('#tabelEchipamente').DataTable({
        processing: true,
        ajax: {
            url: '/api/echipamente', 
            type: 'GET',
            dataSrc: '',
            error: function(xhr, error, code) {
                console.error("Eroare la preluarea datelor:", error);
                $('#tabelEchipamente_processing').html("Eroare la conectarea la baza de date.");
            }
        },
        columns: [
            { data: 'nr_inventar' },
            { data: 'denumire' },
            { data: 'tip' },
            { data: 'locatie' },
            { data: 'utilizator' },
            { 
                data: 'activ',
                render: function(data, type, row) {
                    if (data) {
                        return '<span class="badge text-bg-success">Activ</span>';
                    } else {
                        return '<span class="badge text-bg-danger">Inactiv</span>';
                    }
                }
            },
            { 
                data: 'id',
                render: function(data, type, row) {
                    return `<a href="/echipament/${data}" class="btn btn-sm btn-info me-1">Fișă</a>
                            <button class="btn btn-sm btn-warning" onclick="deschideEditare(${data})">Edit</button>`;
                },
                orderable: false 
            }
        ]
    });
    
    $('#btnAplicaFiltre').on('click', function() {
        var filterData = {
            tip: $('#filterTip').val(),
            locatie: $('#filterLocatie').val(),
            status: $('#filterStatus').val()
        };

        tabelEchipamente.ajax.url('/api/echipamente/filtre?' + $.param(filterData)).load();
    });

});