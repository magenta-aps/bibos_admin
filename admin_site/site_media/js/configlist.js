(function(BibOS, $) {
    tr = BibOS.translate;
    if(!document.getElementById('configlist-templates')) {
        alert(
            'configlist.js loaded without templates present' + "\n" +
            'Did you forget to include system/configlist/templates.html?'
        );
        return;
    }

    var ConfigList = function() {
        // Member variables?
    };

    $.extend(ConfigList.prototype, {
        init: function() {
            BibOS.addTemplate(
                'configlist-item',
                '#configuration-item-template'
            );
            $('#configuration-item-template input').attr(
                'disabled', 'disabled'
            );
            $('#editconfigdialog input').attr('disabled', 'disabled');
            $('#editconfigdialog').on('shown', function() {
                if($('#editconfig_pk').val() == 'new') {
                    $('#editconfig_name').focus();
                } else {
                    $('#editconfig_value').focus().select()
                }
            })
        },
        addConfig: function(id, key, value) {
            var num_new = $('#' + id + '_new_entries').val()
            var item = $(BibOS.expandTemplate('configlist-item', {
                pk: 'new_' + num_new,
                key: key,
                value: value,
                submit_name: id
            }));
            item.insertBefore($('#' + id + '_new_entries').parent().parent())
            this.updateNew(id)
        },
        updateNew: function(id) {
            var num = 0;
            $('#' + id + ' input.config-pk').each(function() {
                var t =  $(this), p = t.parent;

                if (t.val().match(/new_^/)) {
                    parent.find('input.config-key').attr(
                        'name',
                        id + '_' + num + '_key'
                    )
                    parent.find('input.config-value').attr(
                        'name',
                        id + '_' + num + '_value'
                    )
                    $(this).val('new_' + num);
                    num++
                }

                $('#' + id + '_new_entries').val(num);
            });
        },
        removeItem: function(clickElem) {
            var e = $(clickElem).parent();
            while (e && e.length && !e.is('tr')) {
                e = e.parent()
            }
            if (e)
                e.remove()
            this.updateNew();
        },
        startEdit: function(clickElem, id) {
            var c = $(clickElem).parent();
            while (c && c.length && !c.is('div.btn-group')) {
                c = c.parent();
            }
            $('#editconfigdialog input').removeAttr('disabled');
            $('#editconfig_id').val(id);
            $('#editconfig_pk').val(c.find('input.config-pk').val());
            var e = $('#editconfig_name').val(c.find('input.config-key').val());
            e.attr('disabled', 'disabled');
            $('#editconfig_value').val(c.find('input.config-value').val());
            $('#editconfigdialog').modal('show');
        },
        startAdd: function(id) {
            $('#editconfigdialog input').removeAttr('disabled');
            $('#editconfig_id').val(id);
            $('#editconfig_pk').val('new');
            $('#editconfig_name').val('');
            $('#editconfig_value').val('');
            $('#editconfigdialog').modal('show');
        },
        submitEditDialog: function() {
            var id = $('#editconfig_id').val(),
                pk = $('#editconfig_pk').val(),
                name = $('#editconfig_name').val(),
                value = $('#editconfig_value').val();

            if (pk == 'new') {
                if (! name) {
                    alert(tr("Du skal angive et navn"));
                    return false;
                }
                existing = $('#' + id).find(
                    'input.config-key[value=' + name + ']'
                );
                if (existing.length) {
                    alert(tr("Config-navnet %s findes allerede", name))
                    $('#editconfig_name').focus().select();
                    return false;
                }
                this.addConfig(id, name, value);
            } else {
                p = $('#' + id).find(
                    'input.config-pk[value=' + pk + ']'
                );
                while (p && p.length && !p.is('tr')) {
                    p = p.parent();
                }
                if (p && p.length) {
                    p.find('input.config-value').val(value)
                    p.find('.config-print-value').html(value)
                }
            }
            $('#editconfigdialog input').attr('disabled', 'disabled');
            $('#editconfigdialog').modal('hide');
            return false;
        }
    });

    BibOS.ConfigList = new ConfigList()
    $(function() { BibOS.ConfigList.init() })
})(BibOS, $);