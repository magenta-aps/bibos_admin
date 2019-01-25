(function(BibOS, $) {
    tr = BibOS.translate;
    if(!document.getElementById('policylist-templates')) {
        alert(
            'policy_list.js loaded without templates present' + "\n" +
            'Did you forget to include system/policy_list/templates.html?'
        );
        return;
    }

    var PolicyList = function() {
        // Member variables?
    };

    $.extend(PolicyList.prototype, {
        init: function() {
            BibOS.addTemplate(
                'policylist-item',
                '#policy-item-template'
            );
            $('#policy-item-template input').attr(
                'disabled', 'disabled'
            );
            $('#editpolicyscriptdialog input').attr('disabled', 'disabled');
            $('#editpolicyscriptdialog').on('shown', function() {
                $(".editpolicyscript-field").first().focus();
            })
        },
        addToPolicy: function(id, key, value) {
            var num_new = $('#' + id + '_new_entries').val()
            // TODO: Here we probably need to loop over script arguments
            var item = $(BibOS.expandTemplate('policylist-item', {
                pk: 'new_' + num_new,
                key: key,
                value: value,
                submit_name: id
            }));
            // end TODO
            item.insertBefore($('#' + id + '_new_entries').parent().parent())
            this.updateNew(id)
        },
        updateNew: function(id) {
            var num = 0;
            $('#' + id + ' input.policy-pk').each(function() {
                var t =  $(this), p = t.parent;

                if (t.val().match(/new_^/)) {
                    parent.find('input.policy-key').attr(
                        'name',
                        id + '_' + num + '_key'
                    )
                    parent.find('input.policy-value').attr(
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
        addScript: function(id) {
            $('#editpolicyscriptdialog input').removeAttr('disabled');
            $('#editpolicyscript_script_id').val(id);
            $('#editpolicyscript_script_pk').val('new');
            $('.editpolicyscript-field').val('');
            $('#editpolicyscriptdialog').modal('show');
        },
        editScript: function(clickElem, id) {
            var c = $(clickElem).parent();
            while (c && c.length && !c.is('div.btn-group')) {
                c = c.parent();
            }
            $('#editpolicyscriptdialog input').removeAttr('disabled');
            $('#editpolicyscript_script_id').val(id);
            $('#editpolicyscript_script_pk').val(c.find('input.policy-pk').val());
            // TODO: Here we need to loop over script arguments
            var e = $('#editpolicyscript_name').val(c.find('input.policy-key').val());
            e.attr('disabled', 'disabled');
            $('#editpolicyscript_value').val(c.find('input.policy-value').val());
            // end TODO
            $('#editpolicyscriptdialog').modal('show');
        },
        submitEditDialog: function() {
            var id = $('#editpolicyscript_script_id').val(),
                pk = $('#editpolicyscript_script_pk').val(),
                // TODO: Here we need to loop over script arguments
                name = $('#editpolicyscript_name').val(),
                value = $('#editpolicyscript_value').val();
                // end TODO

            if (pk == 'new') {
                if (! name) {
                    alert(tr("Du skal angive et navn"));
                    return false;
                }
                existing = $('#' + id).find(
                    'input.policy-key[value=' + name + ']'
                );
                if (existing.length) {
                    alert(tr("Policy-navnet %s findes allerede", name))
                    $('#editpolicyscript_name').focus().select();
                    return false;
                }
                this.addToPolicy(id, name, value);
            } else {
                p = $('#' + id).find(
                    'input.policy-pk[value=' + pk + ']'
                );
                while (p && p.length && !p.is('tr')) {
                    p = p.parent();
                }
                if (p && p.length) {
                    p.find('input.policy-value').val(value)
                    p.find('.policy-print-value').html(value)
                }
            }
            $('#editpolicyscriptdialog input').attr('disabled', 'disabled');
            $('#editpolicyscriptdialog').modal('hide');
            return false;
        }
    });

    BibOS.PolicyList = new PolicyList()
    $(function() { BibOS.PolicyList.init() })
})(BibOS, $);
