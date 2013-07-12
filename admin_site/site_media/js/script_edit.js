(function(BibOS, $) {
    BibOS.addTemplate('script-input', '#script-input-template');
    
    ScriptEdit = function() {
        this.reload = false
        this.iframeCount = 0;
    }
    $.extend(ScriptEdit.prototype, {
        init: function() {
            this.modal = $('#runscriptmodal')
            this.modalHeader = $('#runscriptmodalheader');
            this.modalFooter = $('#runscriptmodalfooter');
            this.modalIframe = $('#runscriptmodaliframe');
            var b = this;
            this.modal.on('show', function() {
                if(b.reload) {
                    b.modalIframe.attr('src', b.defaultIframeSrc)
                } else {
                    b.defaultIframeSrc = b.modalIframe.attr('src');
                    b.reload = true;
                }
            })
        },
        setModalLoading: function() {
            var modal = $('#runscriptmodal');
            if(this.modalDefaultHTML) {
                modal.html(this.modalDefaultHTML);
            } else {
                this.modalDefaultHTML = modal.html()
            }
        },
        setModalContent: function(html) {
            $('#runscriptmodal').html(html);
        },
        addInput: function (id, data_in) {
            var container = $(id)
            if (!data_in)
                data_in = {}
            var count = container.find('tr.script-input').length;
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
            elem.insertBefore(container.find('tr.script-input-add').first());
            this.updateInputNames(id);
        },
        removeInput: function(elem) {
            var container = $(elem).parents('fieldset').first()
            $(elem).remove();
            this.updateInputNames(container);
        },
        updateInputNames: function(id) {
            var container = $(id)
            inputs = container.find('tr.script-input');
            inputs.each(function(i, e) {
                var elem = $(e);
                elem.find('input.pk-input').attr('name', 'script-input-' + i + '-pk')
                elem.find('input.name-input').attr('name', 'script-input-' + i + '-name')
                elem.find('select.type-input').attr('name', 'script-input-' + i + '-type')
            })
            container.find('input.script-number-of-inputs').val(inputs.length);
        },
        selectGroupOrPC: function(htmlElem) {
            elem = $(htmlElem);
            input = elem.find('input[type=checkbox]').first()
            if(input.is(':checked')) {
                elem.removeClass('selected')
                input.removeAttr('checked')
            } else {
                elem.addClass('selected')
                input.attr('checked', 'checked')
            }
            
        },
        updateDialog: function(form, header, footer, height) {
            this.form = form;
            this.modalHeader.html(header);
            this.modalFooter.html(footer);
            this.modalIframe.height(height + 100);
        },
        submitForm: function() {
            this.form.submit();
        },
        submitStep2: function(button) {
            form = $(button).parent().parent()
            this.iframeCount++
            name = 'run_script_step2_iframe' + this.iframeCount
            $('<iframe></iframe>', {
                id: name,
                name: name,
                src: 'about:blank'
            }).appendTo($('body').first());
            form.attr('target', name);
            form.submit();
        }
    })

    BibOS.ScriptEdit = new ScriptEdit()
    $(function() { BibOS.ScriptEdit.init() })
})(BibOS, $);