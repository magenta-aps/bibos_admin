(function(BibOS, $) {
    tr = BibOS.translate;
    if(!document.getElementById('packagelist-templates')) {
        alert(
            'package_list.js loaded without templates present' + "\n" +
            'Did you forget to include system/package_lists/templates.html?'
        );
        return;
    }

    BibOS.addTemplate('packagelist-item', '#packagelist_item');
    $('#packagelist_item input').attr('disabled', 'disabled');
    var PackageList = function() {
        this.activeList = null
        this.currentPackages = {}
    };

    function addPackageToList(id, label, submit_name) {
        var input = $('#' + id + "_addremovepackagename"),
            list = $('#' + id + ' ul.packagelist');

        var val = input.val()
        if (!val)
            return;

        var existing = null;
        list.find('li.packagemarker').each(function() {
            if ($(this).attr('data-packagename') == val) {
                existing = $(this);
                return false;
            }
            return true;
        });

        if (existing) {
            if (existing.find("a").first().hasClass(label)) {
                input.val('');
                return;
            }
        }

        var errorhandler = function() {
            alert(tr('Could not find a package with name %s', val));
        };

        $.ajax({
            'dataType': "json",
            'url': '/packages/',
            'data': {'get_by_name': val},
            'success': function(data) {
                if (!data[0]) {
                    errorhandler();
                    return;
                }
                var item = $(BibOS.expandTemplate(
                    'packagelist-item',
                    $.extend(data[0], {
                        'label': label,
                        'submit_name': submit_name
                    })
                ));
                if (existing) {
                    existing.remove();
                }
                // Insert in correct place in list
                var inserted = false;
                list.find('li.packagemarker').each(function() {
                    li = $(this)
                    if (li.attr('data-packagename') > val &&
                        li.find('span.' + label).length) {
                        item.insertBefore(li)
                        input.val('');
                        inserted = true;
                        return false;
                    }
                    return true;
                });
                if (!inserted) {
                    if(label == 'label-success') {
                        var anchor = list.find('span.label-important');
                        if(anchor.length)
                            item.insertBefore(anchor.first().parents('li.packagemarker'))
                        else
                            item.appendTo(list);
                    } else {
                        item.appendTo(list);
                    }
                }
                input.val('');
            },
            'error': errorhandler
        })
    }
    
    $.extend(PackageList.prototype, {
        init: function() {
            $(".addpackagecontrol input[type=text]").typeahead({
                source: function(q, cb) {
                    $.getJSON(
                        '/packages/?distinct_by_name=1&q=' + escape(q),
                        function(data) {
                            var arr = [];
                            $.each(data, function() {
                                arr.push(this.name + " | " + this.description)
                            })
                            cb(arr);
                        }
                    );
                },
                // Matching and sorting is handled by the query
                matcher: function() { return true },
                sorter: function(items) { return items },
                updater: function (item) {
                    return item.substr(0, item.indexOf('|') - 1)
                }
            });
        },
        addPackage: function(id) {
            addPackageToList(id, 'label-success', id + '_add')
            return false;
        },
        removePackage: function(id) {
            addPackageToList(id, 'label-important', id + '_remove')
            return false;
        },
        setActiveLists: function(id) {
            this.removeList = $('#' + id + ' ul.removedpackages')
        },
        cancelEditing: function() {
            location.href=location.href;
            return false;
        },
        markUpgradePackages: function(container_id, form_id) {
            var form = $(form_id);
            form.find('input[name=packages]').remove();
            $(container_id).find('input[name=upgrade_package]:checked').each(
                function() {   
                    if($(this).attr('name') == 'upgrade_package') {
                        $('<input>').attr(
                            { 'type': 'hidden', 'name': 'packages'}
                        ).val($(this).val()).appendTo(form)
                    }
                }
            )
            form.submit()
        }
    });
    
    BibOS.PackageList = new PackageList()
    $(function() { BibOS.PackageList.init() })
})(BibOS, $);
    
function toggle_package_selection(source) {
        var element_name = "upgrade_package";
        var checkboxes = document.getElementsByName(element_name);
        for(var i=0, n=checkboxes.length;i<n;i++) {
            checkboxes[i].checked = source.checked;
	}
    }

