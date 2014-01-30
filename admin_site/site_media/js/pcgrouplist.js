(function(BibOS, $) {
    function PCGroupList() {
        // Initial variables?
    }
    $.extend(PCGroupList.prototype, {
        init: function() {
        },
        setupList: function(id) {
            var container = $(id), t = this,
                submit_name = container.attr('id').replace(/^id_/, '');

            container.find('li.pcgrouplist-item').each(function() {
                var li = $(this);
                li.on('click', function(e) {
                    t.moveToSelected(e, submit_name, li)
                });
                li.find('ul.dropdown-menu li').on('click', function(e) {
                    t.moveToAvailable(e, submit_name, li);
                });
            });
        },
        moveToSelected: function(e, submit_name, li) {
            var container = $('#id_' + submit_name),
                name = li.attr('data-group-name'),
                pk = li.attr('data-group-pk');


            // When not in the available list, move to default handler
            // eg. show dropdown
            if(!li.parents('ul.addgrouplist').length) {
                return true;
            }

            // Otherwise stop everything else
            e.preventDefault();
            e.stopPropagation();

            // Add hidden input with the value
            var input = $('<input type="hidden" />');
            input.attr('name', container.attr('id').replace(/^id_/, ''));
            input.val(pk);
            input.appendTo(li.find('div').first());

            // Move to the other list
            BibOS.insertToOrderedList(
                container,
                'li',
                function(matchElem) {
                    return matchElem.attr('data-group-name') > name
                },
                li,
                function() {
                    li.detach().insertAfter(container.children('li').last())
                }
            )
            return false;
        },
        moveToAvailable: function(e, submit_name, li) {
            var container = $('#id_' + submit_name),
                name = li.attr('data-group-name');

            // Remove the hidden input with the submit value
            li.find('input').remove();

            // Move to the other list
            BibOS.insertToOrderedList(
                container.find('ul.addgrouplist'),
                'li',
                function(matchElem) {
                    return matchElem.attr('data-group-name') > name
                },
                li
            )
            e.preventDefault();
            e.stopPropagation();
            li.find('div.btn-group.profile').removeClass('open');
        }
    });

    BibOS.PCGroupList = new PCGroupList();
    $(function() { BibOS.PCGroupList.init() });
})(BibOS, $);