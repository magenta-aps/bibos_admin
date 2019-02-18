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
        this.scriptInputs = []
        // These two snippets of HTML should match what's inside item.html
        this.hiddenParamField = function (name, type, mandatory) {
          return '<input class="policy-script-param" type="hidden" name="' + name + '" value="" data-inputtype="' + type + '"' + (mandatory ? ' required="required"' : '') + '/>';
        }
        this.visibleParamField = function (name) {
          return '<div class="policy-script-print"><strong class="policy-script-print-name">' + name + ': </strong><span class="policy-script-print-value"></span></div>'
        }
        this.getFieldType = function(type) {
          switch(type) {
            case 'INT':
              return 'number';
            case 'STRING':
              return 'text';
            case 'FILE':
              return 'file';
            case 'DATE':
              return 'date';
            default:
              return 'text';
          }
        }
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
        addToPolicy: function(id, scriptId, scriptName, scriptPk, scriptInputs) {
            var num_new = $('#' + id + '_new_entries').val()
            var item = $(BibOS.expandTemplate('policylist-item', {
                ps_pk: 'new_' + num_new,
                script_pk: scriptPk,
                name: scriptName,
                position: 'new_' + num_new,
                submit_name: id
            }));
            this.scriptInputs = scriptInputs
            item.insertBefore($('#' + id + '_new_entries').parent().parent())
            this.updateNew(id)
            $("#addpolicyscriptdialog").modal('hide');
        },
        updateNew: function(id) {
            var num = 0;
            $('#' + id + ' input.policy-script-pos').each(function() {
                var t =  $(this), p = t.parent();

                if (t.val().match(/^new_/)) {
                    p.find('input.policy-script-name').attr(
                        'name',
                        id + '_new_' + num
                    )
                    p.find('input.policy-script-param').attr(
                        'name',
                        id + '_new_' + num + '_params'
                    )
                    t.val('new_' + num);
                    num++
                }

                $('#' + id + '_new_entries').val(num);
            });
        },
        removeItem: function(clickElem, id) {
            var e = $(clickElem).parent();
            while (e && e.length && !e.is('tr')) {
                e = e.parent()
            }
            if (e)
                e.remove()
            this.updateNew(id);
        },
        addScript: function(id) {
            $('#addpolicyscriptdialog input').removeAttr('disabled');
            // $('#addpolicyscript_script_id').val(id);
            // $('#addpolicyscript_script_pk').val('new');
            // $('.addpolicyscript-field').val('');
            $('#addpolicyscriptdialog').modal('show');
        },
        editScript: function(clickElem, id) {
          $("#editpolicyscriptdialog .modal-body").html(''); // delete old inputs

          // loop over all input fields in the list view, and render fields for them in the modal
          var inputWrapper = $(clickElem).closest('div.btn-group');
          var inputFields = $([]); // make an empty jQuery object we can add to later
          $.each(inputWrapper.find('.policy-script-param'), function(idx, elm) {
            var t = $(elm);
            var label = t.next('.policy-script-print').find('.policy-script-print-name');
            var newElement = $('<input/>', {
              type: BibOS.PolicyList.getFieldType(t.attr('data-inputtype')),
              name: "edit_" + t.attr('name'),
              id: "edit_" + t.attr('name')
            })
            if (newElement.attr('type') == "file") {
              newElement[0].files = t[0].files
            } else {
              newElement[0].value = t.val()
            }
            inputFields = inputFields.add($('<label/>', {
              for: t.attr('name'),
              text: label.text()
            })).add(newElement)
          });
          $("#editpolicyscriptdialog .modal-body").append(inputFields);
          // var c = $(clickElem).parent();
          // while (c && c.length && !c.is('div.btn-group')) {
          //     c = c.parent();
          // }
          // $('#editpolicyscriptdialog input').removeAttr('disabled');
          // $('#editpolicyscript_script_id').val(id);
          // $('#editpolicyscript_script_pk').val(c.find('input.policy-script-pos').val());
          // // TODO: Here we need to loop over script arguments
          // var e = $('#editpolicyscript_name').val(c.find('input.policy-script-name').val());
          // e.attr('disabled', 'disabled');
          // $('#editpolicyscript_value').val(c.find('input.policy-script-param').val());
          // // end TODO
          $('#editpolicyscriptdialog').modal('show');
        },
        renderScriptFields: function(name, scriptPk, submitName) {
          // If we come directly from adding a new script, django template variable "params" will only be #PARAMS#, so we need to render the fields dynamically
          var param_fields = ''

          // generate the hidden input fields and divs to render the parameters for the selected script
          for(var i = 0; i < BibOS.PolicyList.scriptInputs.length; i++) {
            paramName = submitName + '_' + scriptPk + '_params';
            param_fields += this.hiddenParamField(paramName, BibOS.PolicyList.scriptInputs[i].type, BibOS.PolicyList.scriptInputs[i].mandatory)
            param_fields += this.visibleParamField(BibOS.PolicyList.scriptInputs[i].name);
          }

          // output the fields
          $('[data-name="policy-script-' + name + '"]').last().append(param_fields)
        },
        submitEditDialog: function(policy_id) {
          // var id = $('#editpolicyscript_script_id').val(),
          //     pk = $('#editpolicyscript_script_pk').val(),
          //     // TODO: Here we need to loop over script arguments
          //     name = $('#editpolicyscript_name').val(),
          //     value = $('#editpolicyscript_value').val();
          //     // end TODO
          //
          // if (pk == 'new') {
          //     if (! name) {
          //         alert(tr("Du skal angive et navn"));
          //         return false;
          //     }
          //     existing = $('#' + id).find(
          //         'input.policy-script-name[value=' + name + ']'
          //     );
          //     if (existing.length) {
          //         alert(tr("Policy-navnet %s findes allerede", name))
          //         $('#editpolicyscript_name').focus().select();
          //         return false;
          //     }
          //     this.addToPolicy(id, name, value);
          // } else {
          //     p = $('#' + id).find(
          //         'input.policy-script-pos[value=' + pk + ']'
          //     );
          //     while (p && p.length && !p.is('tr')) {
          //         p = p.parent();
          //     }
          //     if (p && p.length) {
          //         p.find('input.policy-script-param').val(value)
          //         p.find('.policy-print-value').html(value)
          //     }
          // }
          // loop over inputs inside the modal, and set their corresponding hidden input fields in the group form
          var wrapper = $("#" + policy_id);
          $("#editpolicyscriptdialog .modal-body input").each(function(idx){
            var t = $(this);
            var inputField = wrapper.find('input[name="' + t.attr('name').substring(5) + '"]').eq(idx);
            var visibleValueField = inputField.next('.policy-script-print').find('.policy-script-print-value')
            if (t.attr('type') == 'file') {
              inputField.addClass('phantom')
              inputField.attr('type', 'file')
              if (t[0].files.length != 0) {
                inputField[0].files = t[0].files
                visibleValueField.text(t[0].files[0].name)
              }
            } else {
              inputField.val(t.val());
              visibleValueField.text(t.val());
            }
          });
          $('#editpolicyscriptdialog').modal('hide');
          return false;
        }
    });

    BibOS.PolicyList = new PolicyList()
    $(function() { BibOS.PolicyList.init(); })
})(BibOS, $);
