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
                {
                    pk: '',
                    position: count || 0,
                    name: '',
                    value_type: 'STRING',
                    name_error: '',
                    type_error: ''
                },
                data_in
            );
            var elem = $(BibOS.expandTemplate(
                'script-input',
                data
            ));
            elem.find('select').val(data['value_type']);
            elem.insertBefore($('#script-input-add'));
            this.updateInputNames();
        },
        removeInput: function(elem) {
            $(elem).remove();
            this.updateInputNames();
        },
        updateInputNames: function() {
            inputs = $('#script-input-container tr.script-input');
            inputs.each(function(i, e) {
                var elem = $(e);
                elem.find('input.pk-input').attr('name', 'script-input-' + i + '-pk')
                elem.find('input.name-input').attr('name', 'script-input-' + i + '-name')
                elem.find('select.type-input').attr('name', 'script-input-' + i + '-type')
            })
            $('#script-number-of-inputs').val(inputs.length);
        }
    })
    BibOS.ScriptEdit = new ScriptEdit()
})(BibOS, $);