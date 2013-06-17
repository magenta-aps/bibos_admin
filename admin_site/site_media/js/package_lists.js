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
                    if (li.attr('data-packagename') > val) {
                        item.insertBefore(li)
                        input.val('');
                        inserted = true;
                        return false;
                    }
                    return true;
                });
                if (!inserted) {
                    item.appendTo(list);
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
        },
        removePackage: function(id) {
            addPackageToList(id, 'label-important', id + '_remove')
        },
        setActiveLists: function(id) {
            this.removeList = $('#' + id + ' ul.removedpackages')
        },
        getCurrentPackages: function(id) {
            var packs = this.currentPackages[id];
            if(!packs) {
                var str_list = $('#' + id).attr('data-base-packages') || '';
                packs = this.currentPackages[id] = str_list.split(",");
            }
            return packs;
        }
    });

    BibOS.PackageList = new PackageList()
    $(function() { BibOS.PackageList.init() })
})(BibOS, $);
