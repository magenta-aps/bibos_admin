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
          return '<input class="policy-script-param'
                  + (type == 'FILE' ? ' phantom' : '')
                  + '" type="' + (type == 'FILE' ? 'file' : 'hidden')
                  + '" name="' + name + '" value="" data-inputtype="' + type +
                  '"' + (mandatory ? ' required="required"' : '') + '/>';
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
                    p.find('input.policy-script-param').each(function(i) {
                        $(this).attr('name',
                                id + '_new_' + num + '_param_' + i)
                    })
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
              /* In principle, it'd be nice (for display purposes) to copy the
                 FileList from the hidden input into the modal dialog -- but
                 this confuses Firefox 65 enormously, and when we try to copy
                 the FileList back again, it gets cleared! */
//              newElement[0].files = t[0].files
            } else {
              newElement[0].value = t.val()
            }
            inputFields = inputFields.add($('<label/>', {
              for: t.attr('name'),
              text: label.text()
            })).add(newElement)
          });
          $("#editpolicyscriptdialog .modal-body").append(inputFields);
          $('#editpolicyscriptdialog').modal('show');
        },
        renderScriptFields: function(name, scriptPk, submitName) {
          // If we come directly from adding a new script, django template variable "params" will only be #PARAMS#, so we need to render the fields dynamically
          var param_fields = ''

          // generate the hidden input fields and divs to render the parameters for the selected script
          for(var i = 0; i < BibOS.PolicyList.scriptInputs.length; i++) {
            paramName = submitName + '_' + scriptPk + '_param_' + i;
            param_fields += this.hiddenParamField(paramName, BibOS.PolicyList.scriptInputs[i].type, BibOS.PolicyList.scriptInputs[i].mandatory)
            param_fields += this.visibleParamField(BibOS.PolicyList.scriptInputs[i].name);
          }

          // output the fields
          $('[data-name="policy-script-' + name + '"]').last().append(param_fields)
        },
        submitEditDialog: function(policy_id) {
          var wrapper = $("#" + policy_id);

          var modalInputs = $("#editpolicyscriptdialog .modal-body input");
          /* Check that each of our mandatory inputs has a value (or that its
             corresponding hidden input field already has a value) */
          var count = 0;
          modalInputs.each(function(){
            var t = $(this);
            var inputField = wrapper.find('input[name="' + t.attr('name').substring(5) + '"]');
            if (inputField.prop("required") == true) {
              if (t.attr('type') == 'file') {
                /* If the hidden input field has a value, then it's fine if
                   this one doesn't -- we won't overwrite it */
                if (t[0].files.length == 0 && inputField[0].files.length == 0) {
                  t.addClass("invalid")
                  return false;
                }
              } else {
                if (t.val().trim().length == 0) {
                  t.addClass("invalid")
                  return false;
                }
              }
            }
            t.removeClass("invalid")
            count += 1;
          });
          console.log(count, modalInputs.length);
          if (count != modalInputs.length)
            return false;

          // loop over inputs inside the modal, and set their corresponding hidden input fields in the group form
          modalInputs.each(function(){
            var t = $(this);
            var inputField = wrapper.find('input[name="' + t.attr('name').substring(5) + '"]');
            var visibleValueField = inputField.next('.policy-script-print').find('.policy-script-print-value')
            if (t.attr('type') == 'file') {
              if (t[0].files.length != 0) {
                inputField[0].files = t[0].files
                visibleValueField.text(t[0].files[0].name)
              }
            } else if (t.val().trim().length != 0) {
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
