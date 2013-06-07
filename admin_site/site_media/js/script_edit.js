(function(BibOS, $) {
    BibOS.addTemplate('script-input', '#script-input-template');

    ScriptEdit = function() {
    }
    $.extend(ScriptEdit.prototype, {
        addInput: function (data_in) {
            if (!data_in)
                data_in = {}
            var count = $('#script-input-container tr.script-input').length;
            var data = $.extend(
                { position: count || 0, name: '', value_type: 'STRING' },
                data_in
            );
            var elem = $(BibOS.expandTemplate(
                'script-input',
                data
            ));
            elem.find('select').val(data['value_type']);
            elem.insertBefore($('#script-input-add'));
            count = $('#script-input-container tr.script-input').length;
            $('#script-number-of-inputs').val(count)
        }
    })
    BibOS.ScriptEdit = new ScriptEdit()
})(BibOS, $);