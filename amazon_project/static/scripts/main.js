$(document).ready(function () {
    let marketplaces = {
        'com.br': 'Brazil',
        'ca': 'Canada',
        'com.mx': 'Mexico',
        'com': 'United States',
        'cn': 'China',
        'in': 'India',
        'co.jp': 'Japan',
        'sg': 'Singapore',
        'com.tr': 'Turkey',
        'ae': 'United Arab Emirates (U.A.E.)',
        'fr': 'France',
        'de': 'Germany',
        'it': 'Italy',
        'nl': 'Netherlands',
        'es': 'Spain',
        'co.uk': 'United Kingdom',
        'com.au': 'Australia'
    };

    let i = 0;
    $.each(marketplaces, function (key, value) {
        console.log(i);
        let col = $('#column1');
        if (i >= 9) {
            col = $('#column2');
        }
        col.append(
            '<label class="anim">' +
            '<input type="checkbox" class="checkbox" name="marketplace" value="' + key + '">' +
            '<label class="text"> ' + value + '</label>' +
            '</label> <br>'
        );
        i++;
    });
});